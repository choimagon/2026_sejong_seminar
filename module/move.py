"""TurtleBot-style linear/angular driving, without ROS or automatic windows."""

from .motion import drive as _drive, stop, view

__all__ = ["move", "stop", "view"]


def move(robot, linear=0.0, angular=0.0):
    """Set forward m/s and left-turn rad/s together; then step/run_for.

    The drive uses wheel radius r and separation L from the loaded XML:
        left  = (linear - angular * L / 2) / r
        right = (linear + angular * L / 2) / r
    Both wheel targets are rad/s. Positive angular turns left; negative
    angular turns right. Combined input drives a curve. The target persists
    until the next command; move(robot, 0, 0) or stop(robot) requests braking.
    Acceleration, torque and ground contact limit achieved velocity.
    """
    _drive(robot, linear=linear, angular=angular)
