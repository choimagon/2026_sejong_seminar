"""Sensor discovery shared by readers and the optional monitor."""

import mujoco

SENSOR_LABELS = {
    "imu": "IMU", "encoders": "Wheel Encoders",
    "ultrasonic": "Ultrasonic", "lidar": "2D LiDAR",
}


class MissingSensorError(ValueError):
    """The selected XML does not contain the requested sensor group."""


def available_sensors(model):
    """Detect actual XML contents rather than assuming sensors from a filename."""
    groups = {
        "imu": ("gyro", "accelerometer"),
        "encoders": ("left_encoder", "right_encoder", "left_wheel_speed", "right_wheel_speed"),
        "ultrasonic": ("left_ultrasonic_ray", "right_ultrasonic_ray"),
    }
    present = [group for group, names in groups.items()
               if all(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SENSOR, name) >= 0 for name in names)]
    if mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "lidar_scanner") >= 0:
        present.append("lidar")
    return tuple(present)


def select_sensors(model, sensors=None):
    """None selects all present groups; () selects none without polling them."""
    present = available_sensors(model)
    if sensors is None:
        return present
    requested = (sensors,) if isinstance(sensors, str) else tuple(sensors)
    missing = [name for name in requested if name not in present]
    if missing:
        raise MissingSensorError(f"Unavailable sensors: {', '.join(missing)}. Available: {', '.join(present) or 'none'}")
    return tuple(dict.fromkeys(requested))


def require_sensor(robot, name):
    robot._check_open()
    select_sensors(robot.model, (name,))
