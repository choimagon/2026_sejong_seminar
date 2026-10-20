"""Local practice runner. Policies receive sensors/odometry, never the Robot.

This is an educational local runner, not the sandbox or website for official
submissions. Simulator truth is read solely for local scoring and comparison.
"""

from collections import deque
import csv
from dataclasses import dataclass
import importlib
import importlib.util
import math
from pathlib import Path
import sys

import mujoco
import numpy as np

from .. import motion, sensor
from ..robot import Robot
from ..motion.speed import angular_speed
from ..move import move
from .actions import Action
from .control import EstimatedController
from .odometry import Estimate, Odometry
from .scenes import OUTPUT


@dataclass(frozen=True)
class Observation:
    time_s: float
    estimate: Estimate
    imu: dict
    encoders: dict
    ultrasonic: np.ndarray | None = None
    lidar: dict | None = None


def sector(scan, center_deg=0, width_deg=20):
    """Nearest range in a scanner-frame sector; inf means no return.

    0=front, +90=left, -90=right, 180=back. Degrees describe directions;
    the original scan angles remain in radians.
    """
    if scan is None:
        raise ValueError("This robot has no lidar; turn and sample ultrasonic instead")
    if not 0 < width_deg <= 360:
        raise ValueError("width_deg must be in (0, 360]")
    angles = np.arctan2(np.sin(scan["angles_rad"] - math.radians(center_deg)),
                        np.cos(scan["angles_rad"] - math.radians(center_deg)))
    ranges = scan["ranges_m"][np.abs(angles) <= math.radians(width_deg / 2)]
    return float(np.min(ranges)) if ranges.size else math.inf


def front_distance(observation):
    """Front sector from LiDAR when present, otherwise the ultrasonic pair."""
    if observation.lidar is not None:
        return sector(observation.lidar, 0)
    if observation.ultrasonic is not None:
        return float(np.min(observation.ultrasonic))
    raise ValueError("Select the sonic, lidar, or all model")


def load_policy(spec):
    """Load module.path:Policy or a local .py file defining class Policy."""
    path = Path(spec)
    if path.suffix == ".py":
        loader = importlib.util.spec_from_file_location("local_student_policy", path.resolve())
        if loader is None or loader.loader is None:
            raise ValueError(f"Cannot load policy: {spec}")
        module = importlib.util.module_from_spec(loader)
        sys.modules[loader.name] = module
        loader.loader.exec_module(module)
        policy_type = module.Policy
    else:
        name, _, attribute = str(spec).partition(":")
        policy_type = getattr(importlib.import_module(name), attribute or "Policy")
    return policy_type()


class Session:
    """One physics owner; policies use sensors and encoder/gyro estimates.

    decide(observation) returns a distance/turn Action. Alternatively,
    velocity(observation) returns (linear m/s, angular rad/s), read at 20 Hz.
    max_sim_time=None runs without a time limit.
    """

    def __init__(self, robot, policy=None, *, max_sim_time=600):
        if max_sim_time is not None and (not math.isfinite(max_sim_time) or max_sim_time <= 0):
            raise ValueError("max_sim_time must be finite and positive, or None for no limit")
        self.robot, self.policy = robot, policy
        self.max_sim_time = max_sim_time
        self.estimator = Odometry.for_robot(robot)
        self.wheel_estimator = Odometry.for_robot(robot, mode="wheel")
        self.controller = EstimatedController()
        self.queue = deque()
        self.done, self.reason = False, "running"
        self.started = robot.time
        self._pose_adr = int(robot.model.joint("base_freejoint").qposadr[0])
        self._origin = robot.data.qpos[self._pose_adr:self._pose_adr+2].copy()
        self._initial_yaw = self._last_yaw = self._yaw()
        self._truth_yaw = 0.0
        self._walls = {g for g in range(robot.model.ngeom)
                       if (mujoco.mj_id2name(robot.model, mujoco.mjtObj.mjOBJ_GEOM, g) or "").startswith("course_wall_")}
        self._in_contact, self.collisions = False, 0
        goal_id = mujoco.mj_name2id(robot.model, mujoco.mjtObj.mjOBJ_SITE, "course_goal")
        self._goal = robot.data.site_xpos[goal_id, :2].copy() if goal_id >= 0 else None
        self._goal_radius = float(robot.model.site_size[goal_id, 0]) if goal_id >= 0 else 0.0
        self.trace = []
        self._trace_period = 0.05
        self._velocity_target = (0.0, 0.0)
        self._next_velocity_update = 0.0
        self.record()

    @property
    def estimate(self):
        return self.estimator.state

    def observe(self):
        values = sensor.read(self.robot)
        return Observation(self.robot.time-self.started, self.estimate, values["imu"],
                           values["encoders"], values.get("ultrasonic"), values.get("lidar"))

    def enqueue(self, action):
        if not isinstance(action, Action):
            raise TypeError("Expected a course Action")
        self.done, self.reason = False, "running"
        self.queue.append(action)

    def stop(self, reason="stopped"):
        self.done, self.reason = True, reason
        self.queue.clear()
        self.controller.cancel()
        messages = {"finished": ("completed", "Goal reached"),
                    "time_limit": ("failed", "Local practice time limit"),
                    "motion_timeout": ("failed", "Estimated movement timed out"),
                    "policy_error": ("failed", "Policy error (see local console/report)")}
        state, message = messages.get(reason, ("cancelled", "Stopped"))
        self.controller.result = {"state": state, "message": message}
        motion.stop(self.robot)

    def advance(self, manual=None):
        """Advance one physics step. Nonzero keys cancel the automatic policy."""
        self.controller.linear_speed = self.robot.motor_speed
        self.controller.angular_speed = angular_speed(self.robot.motor_speed)
        if manual is not None and any(manual):
            self.done, self.reason = False, "running"
            self.policy = None
            self.queue.clear()
            self.controller.cancel()
        target = tuple(manual) if manual is not None and any(manual) else (0.0, 0.0)
        velocity_policy = self.policy is not None and callable(getattr(self.policy, "velocity", None))
        if not any(target) and not self.done and velocity_policy:
            if self.robot.time >= self._next_velocity_update:
                try:
                    values = np.asarray(self.policy.velocity(self.observe()), dtype=float)
                    if values.shape != (2,) or not np.isfinite(values).all():
                        raise ValueError("velocity(observation) must return finite (linear, angular)")
                    self._velocity_target = tuple(values)
                    self._next_velocity_update = self.robot.time + 0.05
                    self.controller.result = {"state": "running", "kind": "velocity",
                                              "linear": values[0], "angular": values[1],
                                              "message": getattr(self.policy, "message", "Sensor-guided driving")}
                except Exception as error:
                    self.error = f"{type(error).__name__}: {error}"
                    self.stop("policy_error")
            target = self._velocity_target
        elif not any(target) and not self.done:
            if self.controller.active is None:
                if self.controller.result["state"] == "failed":
                    self.stop("motion_timeout")
                else:
                    action = self.queue.popleft() if self.queue else None
                    if action is None and self.policy is not None:
                        try:
                            action = self.policy.decide(self.observe())
                            if not isinstance(action, Action):
                                raise TypeError("decide() must return an Action")
                        except Exception as error:
                            self.error = f"{type(error).__name__}: {error}"
                            self.stop("policy_error")
                    if action is not None:
                        if action.kind == "stop":
                            self.stop()
                        else:
                            self.controller.begin(action, self.estimate)
            target = self.controller.update(self.estimate)
        if self.done:
            target = (0.0, 0.0)
        move(self.robot, *target)
        self.robot.step()
        self.estimator.sample(self.robot)
        self.wheel_estimator.sample(self.robot)
        yaw = self._yaw()
        self._truth_yaw += math.atan2(math.sin(yaw-self._last_yaw), math.cos(yaw-self._last_yaw))
        self._last_yaw = yaw
        contact = any((int(c.geom1) in self._walls or int(c.geom2) in self._walls) and c.dist <= 0
                      for c in self.robot.data.contact)
        self.collisions += int(contact and not self._in_contact)
        self._in_contact = contact
        if not self.done and self._goal is not None and np.linalg.norm(self._position() - self._goal) < self._goal_radius:
            self.stop("finished")
        if not self.done and self.max_sim_time is not None and self.robot.time-self.started >= self.max_sim_time:
            self.stop("time_limit")
        self.record()

    def _position(self):
        return self.robot.data.qpos[self._pose_adr:self._pose_adr+2]

    def _yaw(self):
        w,x,y,z = self.robot.data.qpos[self._pose_adr+3:self._pose_adr+7]
        return math.atan2(2*(w*z+x*y), 1-2*(y*y+z*z))

    def record(self, *, force=False):
        if not force and self.trace and self.robot.time-self.started-self.trace[-1]["time_s"] < self._trace_period:
            return
        if len(self.trace) >= 50000:
            self.trace[:] = self.trace[::2]
            self._trace_period *= 2
        delta = self._position() - self._origin
        c, s = math.cos(self._initial_yaw), math.sin(self._initial_yaw)
        estimate, wheel = self.estimate, self.wheel_estimator.state
        self.trace.append({
            "time_s": self.robot.time-self.started,
            "truth_x_m": c*delta[0]+s*delta[1], "truth_y_m": -s*delta[0]+c*delta[1],
            "truth_yaw_rad": self._truth_yaw,
            "estimated_x_m": estimate.x_m, "estimated_y_m": estimate.y_m,
            "estimated_yaw_rad": estimate.yaw_rad,
            "wheel_x_m": wheel.x_m, "wheel_y_m": wheel.y_m,
            "wheel_yaw_rad": wheel.yaw_rad, "encoder_distance_m": estimate.distance_m,
        })

    def telemetry(self):
        self.record(force=True)
        return {**self.trace[-1], "velocity_m_s": self.estimate.velocity_m_s,
                "gyro_rad_s": self.estimate.gyro_rad_s,
                "reason": self.reason, "collisions": self.collisions}

    def save_csv(self, name="practice"):
        self.record(force=True)
        folder = OUTPUT / "traces"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{name}.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=self.trace[0].keys())
            writer.writeheader()
            writer.writerows(self.trace)
        return path

    def result(self):
        self.record(force=True)
        row = self.trace[-1]
        return {"finished": self.reason == "finished", "simulation_time_s": self.robot.time-self.started,
                "reason": self.reason, "wall_contacts": self.collisions,
                "position_error_m": math.hypot(row["truth_x_m"]-row["estimated_x_m"],
                                                row["truth_y_m"]-row["estimated_y_m"]),
                **({"error": self.error} if hasattr(self, "error") else {})}


def run(world, policy, *, max_sim_time=600, trace_name=None, motor_speed=None):
    """Local practice; max_sim_time=None removes the simulation time limit."""
    with Robot(world.path, motor_speed=motor_speed) as robot:
        robot.run_for(0.5)
        session = Session(robot, policy, max_sim_time=max_sim_time)
        while not session.done:
            session.advance()
        result = session.result()
        if trace_name is not None:
            result["trace_csv"] = str(session.save_csv(trace_name))
        return result
