"""Imu access independent of any GUI."""


from ._common import require_sensor


def read(robot):
    """Return copied acceleration_m_s2 and angular_velocity_rad_s XYZ arrays."""
    require_sensor(robot, "imu")
    return read_imu(robot.data)


def view(xml_kind="all", **options):
    """Open Controls and the IMU tab only, in a new simulation."""
    from . import view as open_monitor
    return open_monitor(xml_kind, sensors=("imu",), **options)


def read_imu(data):
    """Read acceleration (m/s^2) and angular velocity (rad/s), in the IMU frame.

    The accelerometer measures specific force: a stationary upright robot reads
    approximately +9.81 m/s^2 on Z. Arrays are copies, independent of later steps.
    """
    return {
        "acceleration_m_s2": data.sensor("accelerometer").data.copy(),
        "angular_velocity_rad_s": data.sensor("gyro").data.copy(),
    }

