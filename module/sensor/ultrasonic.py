"""Ultrasonic access independent of any GUI."""

import numpy as np

from ._common import require_sensor


def read(robot, max_range=4.0):
    """Return left/right distances in metres; inf means no return."""
    require_sensor(robot, "ultrasonic")
    return read_ultrasonic(robot.data, max_range)


def view(xml_kind="sonic", **options):
    """Open Controls and the ultrasonic tab only, in a new simulation."""
    from . import view as open_monitor
    return open_monitor(xml_kind, sensors=("ultrasonic",), **options)


def read_ultrasonic(data, max_range=4.0):
    """Read the XML's ideal single-ray ultrasonic sensors, [left, right], in m.

    np.inf means no return within max_range. These are not acoustic cone or
    noise simulations; their directions come from the XML rangefinder sites.
    """
    if not np.isfinite(max_range) or max_range <= 0:
        raise ValueError("max_range must be finite and positive")
    ranges = np.array([
        data.sensor("left_ultrasonic_ray").data[0],
        data.sensor("right_ultrasonic_ray").data[0],
    ])
    return np.where((ranges >= 0) & (ranges <= max_range), ranges, np.inf)

