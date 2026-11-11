"""Ultrasonic access independent of any GUI."""

import numpy as np

from ._common import require_sensor


def read(robot, max_range=4.0):
    """Return one forward distance as a float in metres; inf means no return."""
    require_sensor(robot, "ultrasonic")
    return read_ultrasonic(robot.data, max_range)


def view(xml_kind="sonic", **options):
    """Open Controls and the ultrasonic tab only, in a new simulation."""
    from . import view as open_monitor
    return open_monitor(xml_kind, sensors=("ultrasonic",), **options)


def read_ultrasonic(data, max_range=4.0):
    """Read one HC-SR04-style module, represented by a front-facing ray.

    The transmitter and receiver are two parts of one module, not two ranges.
    This ideal ray does not model acoustic spread, travel time or noise.
    """
    if not np.isfinite(max_range) or max_range <= 0:
        raise ValueError("max_range must be finite and positive")
    distance = float(data.sensor("front_ultrasonic_ray").data[0])
    return distance if 0 <= distance <= max_range else float("inf")
