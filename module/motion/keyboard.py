"""W/S forward and backward; Q/E left and right rotation."""

from .commands import FORWARD_SPEED, TURN_SPEED
from .primitives import velocity


def keyboard_control(pressed):
    """Read held W/S/Q/E keys as (forward m/s, left rotation rad/s)."""
    movements = (("w", "forward"), ("s", "backward"), ("q", "left"), ("e", "right"))
    targets = [velocity(kind) for key, kind in movements if pressed(key)]
    return tuple(sum(target[axis] for target in targets) for axis in (0, 1))


def view(xml_kind="all", *, commands=None, demo=False, playback_speed=1.0, motor_speed=FORWARD_SPEED):
    """Open the native model and Controls guide with no sensor tabs or scans.

    commands may contain strings or motion.commands descriptions. demo=False
    uses the original XML without sensor test obstacles.
    """
    from ..viewer import view as open_monitor
    return open_monitor(xml_kind, sensors=(), commands=commands, demo=demo,
                        playback_speed=playback_speed, motor_speed=motor_speed)

