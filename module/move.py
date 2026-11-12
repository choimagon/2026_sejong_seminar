"""TurtleBot-style linear/angular driving, without ROS or automatic windows."""

import math

from .motion import drive as _drive, stop, view

__all__ = ["move", "stop", "view"]


def move(robot, linear=0.0, angular=0.0, seconds=None):
    """Set forward m/s and left-turn rad/s; optionally run for seconds.

    The drive uses wheel radius r and separation L from the loaded XML:
        left  = (linear - angular * L / 2) / r
        right = (linear + angular * L / 2) / r
    Both wheel targets are rad/s. Positive angular turns left; negative
    angular turns right. Combined input drives a curve. The target persists
    until the next command; move(robot, 0, 0) or stop(robot) requests braking.
    Acceleration, torque and ground contact limit achieved velocity.
    With seconds=None this only sets the target, preserving the original API.
    A fourth argument advances physics for that duration with the same target.
    """
    if seconds is not None:
        seconds = float(seconds)
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("seconds must be finite and nonnegative")
    _drive(robot, linear=linear, angular=angular)
    if seconds is not None:
        robot.run_for(seconds)
