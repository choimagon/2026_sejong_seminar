"""The same four chassis motions for held keys and automatic decisions."""

from .commands import FORWARD_SPEED, TURN_SPEED


def velocity(kind, linear_speed=FORWARD_SPEED, turn_speed=TURN_SPEED):
    """Return (forward m/s, counterclockwise rad/s). A/D have no action."""
    return {"forward": (linear_speed, 0.0), "backward": (-linear_speed, 0.0),
            "left": (0.0, turn_speed), "right": (0.0, -turn_speed),
            "stop": (0.0, 0.0)}[kind]
