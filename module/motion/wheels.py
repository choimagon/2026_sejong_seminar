"""Left/right wheel commands: radians and rad/s, positive rolls forward.

set_velocity persists until replaced or stopped; call robot.step/run_for.
rotate adds relative encoder angles to a queue, blocking by default.
set_position replaces the queue with absolute encoder angle targets.
Only wheel encoders feed back into position control; no base pose is read.
"""

from collections import deque
from dataclasses import dataclass, replace
import math

import numpy as np


def _pair(left, right):
    values = np.array([left, right], dtype=float)
    if values.shape != (2,) or not np.isfinite(values).all():
        raise ValueError("Left and right must be finite numbers")
    return values


def _rotation(robot, left, right, speed):
    robot._check_open()
    angles = _pair(left, right)
    if speed is None:
        speed = robot.motor_speed / float(robot.model.geom("drive_left_tire").size[0])
    speed = float(speed)
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError("Wheel speed must be finite and positive (rad/s)")
    return _Rotation(tuple(angles), speed)


def set_velocity(robot, left, right):
    """Set signed wheel rad/s; cancel queued moves, then step/run_for.

    Equal positive speeds roll forward; left negative/right positive turns
    left. Acceleration, motor torque, and contact limit the achieved speed.
    Explicit rad/s targets do not scale when motion.set_speed() is called.
    """
    values = _pair(left, right)
    robot._enable_wheels()
    controller = robot._wheel_controller
    controller.cancel("Wheel velocity control")
    controller.velocity[:] = values
    controller.result = {"state": "running", "kind": "wheel_velocity",
                         "target_rad_s": values.tolist(), "message": "Wheel velocity control"}


def rotate(robot, left, right, *, speed=None, wait=True):
    """Turn each wheel by signed relative radians, at up to speed rad/s.

    left=right=math.tau means one forward revolution of both wheels, not a
    robot heading change. wait=False queues without advancing time.
    Completion is based on encoders; wheel slip can change chassis travel.
    """
    command = _rotation(robot, left, right, speed)
    robot._enable_wheels()
    robot._wheel_controller.enqueue(command)
    return wait_until_done(robot) if wait else status(robot)


def set_position(robot, left, right, *, speed=None, wait=True):
    """Replace moves with absolute, unwrapped encoder targets in radians.

    The encoder origin is the XML/reset wheel angle. Targets are not wrapped
    to +/-pi. Default speed is robot.motor_speed / wheel radius.
    """
    command = _rotation(robot, left, right, speed)
    robot._enable_wheels()
    controller = robot._wheel_controller
    angles = robot.data.sensordata[controller.position_ids]
    command = replace(command, angles=tuple(np.asarray(command.angles) - angles))
    controller.cancel("New absolute wheel position")
    controller.enqueue(command)
    return wait_until_done(robot) if wait else status(robot)


def stop(robot):
    """Cancel wheel moves and request zero wheel speed; step to brake."""
    robot._enable_wheels()
    robot._wheel_controller.cancel("Stopped")
    robot.data.ctrl[robot._driver.motors] = 0


def status(robot):
    """Read the wheel command state without advancing physics."""
    robot._check_open()
    if robot._wheel_controller is None:
        return {"state": "idle", "message": "Ready", "pending": 0}
    return robot._wheel_controller.status()


def wait_until_done(robot):
    """Run queued wheel rotations; return status or raise motion.MotionError."""
    robot._check_open()
    controller = robot._wheel_controller
    if robot._mode != "wheels" or controller is None:
        raise ValueError("No wheel control is active")
    while controller.active is not None or controller.queue:
        robot.step()
    result = status(robot)
    if result["state"] in ("failed", "cancelled"):
        from .api import MotionError
        raise MotionError(result)
    return result


wait = wait_until_done


@dataclass(frozen=True)
class _Rotation:
    angles: tuple
    speed: float


class WheelController:
    """Encoder feedback producing left/right rad/s for the shared drive."""

    def __init__(self, model):
        self.position_ids = [int(model.sensor(f"{side}_encoder").adr[0]) for side in ("left", "right")]
        self.velocity_ids = [int(model.sensor(f"{side}_wheel_speed").adr[0]) for side in ("left", "right")]
        self.velocity = np.zeros(2)
        self.queue = deque()
        self.active = None
        self.result = {"state": "idle", "message": "Ready"}

    def cancel(self, message):
        self.queue.clear()
        self.active = None
        self.velocity[:] = 0
        self.result = {"state": "cancelled", "message": message}

    def reset(self):
        self.cancel("Ready")
        self.result["state"] = "idle"

    def enqueue(self, command):
        self.velocity[:] = 0
        self.queue.append(command)
        if self.active is None:
            self.result = {"state": "queued", "kind": "wheel_rotation", "unit": "rad"}

    def scale_speed(self, ratio):
        self.queue = deque(replace(c, speed=c.speed * ratio) for c in self.queue)
        if self.active is not None:
            command = self.active["command"]
            self.active["command"] = replace(command, speed=command.speed * ratio)

    def update(self, data):
        angles = data.sensordata[self.position_ids]
        if self.active is None:
            if not self.queue:
                return self.velocity
            command = self.queue.popleft()
            self.active = {"command": command, "start": angles.copy(),
                           "started": float(data.time), "last_progress": float(data.time),
                           "checkpoint": angles.copy(), "settled": None}
        active = self.active
        command = active["command"]
        progress = angles - active["start"]
        error = np.asarray(command.angles) - progress
        remaining = float(np.max(np.abs(error)))
        self.result = {"state": "running", "kind": "wheel_rotation", "unit": "rad",
                       "amount": list(command.angles), "progress": progress.tolist(),
                       "message": "Wheel encoder feedback"}
        slow = np.max(np.abs(data.sensordata[self.velocity_ids])) < 0.06
        if remaining <= 0.02 and slow:
            if active["settled"] is None:
                active["settled"] = float(data.time)
            if data.time - active["settled"] >= 0.15:
                self.active = None
                self.result = {**self.result, "state": "completed", "message": "Wheel angles reached"}
            return np.zeros(2)
        active["settled"] = None
        if np.max(np.abs(angles - active["checkpoint"])) >= 0.005:
            active["checkpoint"] = angles.copy()
            active["last_progress"] = float(data.time)
        extent = float(np.max(np.abs(command.angles)))
        timeout = 15 + 2 * extent / command.speed + 4 * math.sqrt(extent)
        if data.time - active["started"] > timeout or (remaining > 0.04 and data.time - active["last_progress"] > 3):
            self.active = None
            self.queue.clear()
            self.result = {**self.result, "state": "failed", "message": "Wheel motion blocked or timed out"}
            return np.zeros(2)
        # Scale unequal wheel displacements so both approach their targets
        # together; keep feedback available to hold a nominally fixed wheel.
        fractions = np.maximum(np.abs(command.angles) / max(extent, 1e-12), 0.1)
        return np.clip(4 * error, -command.speed * fractions, command.speed * fractions)

    def status(self):
        return {**self.result, "pending": len(self.queue)}
