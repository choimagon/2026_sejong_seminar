"""Distance/turn control from estimated motion, never qpos or simulator pose."""

import math

from ..motion.primitives import velocity
from ..motion.commands import FORWARD_SPEED, TURN_SPEED
from .actions import Action


class EstimatedController:
    def __init__(self, linear_speed=FORWARD_SPEED, angular_speed=TURN_SPEED):
        self.linear_speed, self.angular_speed = linear_speed, angular_speed
        self.active = None
        self.result = {"state": "idle", "message": "Ready: encoder + gyro feedback"}

    def begin(self, action, estimate):
        if not isinstance(action, Action):
            raise TypeError("decide(observation) must return a course Action")
        if action.kind == "stop":
            self.cancel()
            return
        self.active = {"action": action, "start": estimate, "settled": None}

    def cancel(self):
        self.active = None
        self.result = {"state": "cancelled", "message": "Stopped"}

    def update(self, estimate):
        if self.active is None:
            return (0.0, 0.0)
        active, start = self.active, self.active["start"]
        action = active["action"]
        curved = action.kind.startswith("arc_")
        turning = curved or action.kind in ("left", "right")
        sign = -1 if action.kind in ("backward", "right", "arc_right") else 1
        target = math.radians(action.amount) if turning else action.amount
        progress = sign * ((estimate.yaw_rad - start.yaw_rad) if turning else
                           (estimate.distance_m - start.distance_m))
        error = target - progress
        tolerance = math.radians(0.3) if turning else 0.004
        slow = abs(estimate.gyro_rad_s) < 0.035 if turning else abs(estimate.velocity_m_s) < 0.02
        if curved:
            slow = slow and abs(estimate.velocity_m_s) < 0.02
        self.result = {"state": "running", "kind": action.kind, "amount": action.amount,
                       "progress": math.degrees(progress) if turning else progress,
                       "unit": "deg" if turning else "m", "pending": 0,
                       "message": "Encoder + gyro feedback"}
        if abs(error) <= tolerance and slow:
            if active["settled"] is None:
                active["settled"] = estimate.time
            if estimate.time - active["settled"] >= 0.15:
                self.active = None
                self.result = {**self.result, "state": "completed", "message": "Estimated target reached"}
            return (0.0, 0.0)
        active["settled"] = None
        if estimate.time - start.time > 12 + target / (0.1 if turning else 0.015):
            self.active = None
            self.result = {**self.result, "state": "failed", "message": "Estimated movement timed out"}
            return (0.0, 0.0)
        if curved:
            if abs(error) <= tolerance:
                return 0.0, 0.0
            rate = min(self.angular_speed, self.linear_speed/action.radius,
                       2.0*abs(error), math.sqrt(3.6*abs(error)))
            distance = estimate.distance_m - start.distance_m
            heading_error = sign*distance/action.radius - (estimate.yaw_rad-start.yaw_rad)
            angular = sign*math.copysign(rate, error) + max(-0.3, min(0.3, 2.0*heading_error))
            return action.radius*rate, max(-self.angular_speed, min(self.angular_speed, angular))
        linear, angular = velocity(action.kind, self.linear_speed, self.angular_speed)
        correction = math.copysign(1, error)
        if turning:
            return 0.0, angular * correction * min(1.0, 1.8 * abs(error) / abs(angular))
        heading_error = start.yaw_rad - estimate.yaw_rad
        return (linear * correction * min(1.0, 1.5 * abs(error) / abs(linear)),
                max(-0.7, min(0.7, 2.5 * heading_error)))
