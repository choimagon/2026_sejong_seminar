"""Distance and angle feedback; produces chassis velocities without changing poses."""

from collections import deque
import math
import numpy as np

from .commands import MotionCommand


def wrapped_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))



class MotionController:
    """Execute queued commands using actual base position and unwrapped yaw.

    update() returns the velocity for WheelDrive.apply(); it never writes qpos.
    Translation measures signed ground-plane displacement from the starting
    base position, while holding the starting heading (wheel slip can cause
    lateral drift). Distance tolerance is 5 mm and turn tolerance is 1 degree.
    Completion
    also requires low velocity for 0.2 simulated seconds. A blocked command
    fails after 3 seconds without progress instead of being reported complete.
    """

    def __init__(self, model):
        joint = model.joint("base_freejoint")
        self.pose_index = int(joint.qposadr[0])
        self.velocity_index = int(joint.dofadr[0])
        self.dt = float(model.opt.timestep)
        self.queue = deque()
        self.active = None
        self.last_result = {"state": "idle", "message": "Ready"}

    def enqueue(self, command):
        if not isinstance(command, MotionCommand):
            raise TypeError("Expected a MotionCommand")
        self.queue.append(command)

    def cancel(self, reason="Stopped"):
        self.queue.clear()
        self.active = None
        self.last_result = {"state": "cancelled", "message": reason}

    def reset(self):
        self.queue.clear()
        self.active = None
        self.last_result = {"state": "idle", "message": "Ready"}

    def _pose(self, data):
        q = data.qpos[self.pose_index:self.pose_index + 7]
        w, x, y, z = q[3:7]
        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        return q[:2].copy(), yaw

    def _start(self, data):
        command = self.queue.popleft()
        position, yaw = self._pose(data)
        target = math.radians(command.amount) if command.kind == "rotate" else command.amount
        if command.kind == "backward":
            target = -target
        self.active = {
            "command": command, "position": position, "yaw": yaw, "last_yaw": yaw,
            "turn": 0.0, "progress": 0.0, "target": target,
            "started": float(data.time), "last_progress": float(data.time),
            "checkpoint": 0.0, "settled": None,
        }

    def _finish(self, state, message):
        active = self.active
        self.last_result = {
            "state": state, "message": message, "kind": active["command"].kind,
            "amount": active["command"].amount,
            "achieved": math.degrees(active["progress"]) if active["command"].kind == "rotate"
                        else active["progress"] * (-1 if active["command"].kind == "backward" else 1),
        }
        self.active = None
        if state == "failed":
            self.queue.clear()

    def update(self, data, manual=(0.0, 0.0)):
        if np.any(np.asarray(manual) != 0):
            if self.active is not None or self.queue:
                self.cancel("Manual keyboard control")
            return tuple(manual)
        if self.active is None:
            if not self.queue:
                return 0.0, 0.0
            self._start(data)
        active = self.active
        command = active["command"]
        position, yaw = self._pose(data)
        yaw_delta = wrapped_angle(yaw - active["last_yaw"])
        active["turn"] += yaw_delta
        active["last_yaw"] = yaw
        heading = np.array([math.cos(active["yaw"]), math.sin(active["yaw"])])
        is_turn = command.kind == "rotate"
        displacement = position - active["position"]
        along_heading = float(displacement @ heading)
        progress = active["turn"] if is_turn else math.copysign(float(np.linalg.norm(displacement)), along_heading)
        active["progress"] = progress
        error = active["target"] - progress
        remaining = abs(error)
        tolerance = math.radians(1) if is_turn else 0.005
        velocity = abs(yaw_delta / self.dt) if is_turn else float(np.linalg.norm(data.qvel[self.velocity_index:self.velocity_index + 2]))
        slow = velocity < (0.025 if is_turn else 0.015)
        if remaining <= tolerance and slow:
            if active["settled"] is None:
                active["settled"] = float(data.time)
            if data.time - active["settled"] >= 0.2:
                self._finish("completed", "Target reached")
            return 0.0, 0.0
        else:
            active["settled"] = None
        threshold = math.radians(0.2) if is_turn else 0.002
        checkpoint_progress = progress if is_turn else along_heading
        if abs(checkpoint_progress - active["checkpoint"]) >= threshold:
            active["checkpoint"] = checkpoint_progress
            active["last_progress"] = float(data.time)
        timeout = 10 + abs(active["target"]) / (0.15 if is_turn else 0.025)
        if data.time - active["started"] > timeout:
            self._finish("failed", "Timed out before reaching the target")
            return 0.0, 0.0
        if remaining > 2 * tolerance and data.time - active["last_progress"] > 3:
            self._finish("failed", "Blocked: no progress for 3 s")
            return 0.0, 0.0
        if is_turn:
            rate = math.copysign(min(command.speed, 1.8 * abs(error), math.sqrt(2.4 * abs(error))), error)
            return 0.0, rate
        # Hold the initial heading, including during small overshoot corrections.
        direction = 1 if error >= 0 else -1
        desired_heading = active["yaw"]
        heading_error = wrapped_angle(desired_heading - yaw)
        speed = direction * min(command.speed, 1.5 * abs(error), math.sqrt(0.5 * abs(error)))
        speed *= max(0.0, math.cos(heading_error))
        heading_correction = float(np.clip(2.5 * heading_error, -0.7, 0.7))
        return speed, heading_correction

    def status(self):
        if self.active is None:
            return {**self.last_result, "pending": len(self.queue)}
        active = self.active
        command = active["command"]
        progress = math.degrees(active["progress"]) if command.kind == "rotate" else active["progress"]
        if command.kind == "backward":
            progress = -progress
        return {"state": "running", "kind": command.kind, "amount": command.amount,
                "progress": progress, "unit": "deg" if command.kind == "rotate" else "m",
                "pending": len(self.queue), "message": "Moving toward target"}

