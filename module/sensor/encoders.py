"""Encoders access independent of any GUI."""

import numpy as np

from ._common import require_sensor


def read(robot):
    """Read left/right position_rad, velocity_rad_s, and wheel distance_m."""
    require_sensor(robot, "encoders")
    radius = float(robot.model.geom("drive_left_tire").size[0])
    return read_encoders(robot.data, radius)


def view(xml_kind="all", **options):
    """Open Controls and the wheel encoder tab only, in a new simulation."""
    from . import view as open_monitor
    return open_monitor(xml_kind, sensors=("encoders",), **options)


def read_encoders(data, wheel_radius=0.038):
    """Read unwrapped wheel angles and speeds, ordered [left, right].

    distance_m is wheel rotation times radius, not ground-truth robot travel.
    No encoder tick resolution is assumed.
    """
    positions = np.array([
        data.sensor("left_encoder").data[0],
        data.sensor("right_encoder").data[0],
    ])
    return {
        "position_rad": positions,
        "velocity_rad_s": np.array([
            data.sensor("left_wheel_speed").data[0],
            data.sensor("right_wheel_speed").data[0],
        ]),
        "distance_m": positions * wheel_radius,
    }

