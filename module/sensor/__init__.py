"""Independent sensor modules. Importing or reading them never opens a window.

    sensor.imu.read(robot)                 # dict of XYZ acceleration/gyro
    sensor.encoders.read(robot)            # dict of left/right wheel arrays
    sensor.ultrasonic.read(robot)          # left/right distances, m
    sensor.lidar.read(robot, num_rays=180)  # angles, ranges, XY points
    sensor.available(robot)                # only groups present in this XML
    sensor.read(robot, sensors=("imu",))    # selected groups only

Use sensor.view("all") for all sensor tabs, or sensor.imu.view("all") for
one sensor tab. The Controls guide opens first in both cases.
"""

from . import imu, encoders, ultrasonic, lidar
from ._common import (
    MissingSensorError, SENSOR_LABELS, available_sensors, select_sensors,
)
from .imu import read_imu
from .encoders import read_encoders
from .ultrasonic import read_ultrasonic
from .lidar import read_lidar


def available(robot):
    """Return available group names, e.g. ('imu', 'encoders') for basic."""
    robot._check_open()
    return available_sensors(robot.model)


def sensor_snapshot(model, data, sensors, scan=None):
    """Low-level reader for an existing MuJoCo state; no physics or GUI."""
    snapshot = {"time": float(data.time)}
    if "imu" in sensors:
        snapshot["imu"] = read_imu(data)
    if "encoders" in sensors:
        radius = float(model.geom("drive_left_tire").size[0])
        snapshot["encoders"] = read_encoders(data, radius)
    if "ultrasonic" in sensors:
        snapshot["ultrasonic"] = read_ultrasonic(data)
    if "lidar" in sensors:
        snapshot["lidar"] = scan if scan is not None else read_lidar(model, data)
    return snapshot


def read(robot, sensors=None):
    """Read selected sensors at the current time. This does not step physics.

    sensors=None reads all available groups. Missing groups raise
    MissingSensorError. Passing () reads only the current simulation time.
    """
    robot._check_open()
    selected = select_sensors(robot.model, sensors)
    return sensor_snapshot(robot.model, robot.data, selected)


def view(xml_kind="all", *, sensors=None, **options):
    """Open native MuJoCo plus a separate monitor for the selected sensors.

    This creates a new simulation; read(robot) reads your existing Robot.
    demo=True by default adds test obstacles to this monitor's simulation.
    """
    from ..viewer import view as open_monitor
    return open_monitor(xml_kind, sensors=sensors, **options)


__all__ = ["imu", "encoders", "ultrasonic", "lidar", "available", "read", "view",
           "MissingSensorError"]
