"""Wheel translation + integrated IMU Z gyro, without simulator pose reads."""

from dataclasses import asdict, dataclass
import math

import numpy as np

from .. import sensor


@dataclass(frozen=True)
class Estimate:
    time: float = 0.0
    x_m: float = 0.0
    y_m: float = 0.0
    yaw_rad: float = 0.0
    wheel_yaw_rad: float = 0.0
    distance_m: float = 0.0
    velocity_m_s: float = 0.0
    gyro_rad_s: float = 0.0

    def to_dict(self):
        return asdict(self)


class Odometry:
    """Origin is the initial robot frame; yaw is unwrapped.

    mode='fused' uses encoder translation and gyro heading. mode='wheel'
    uses only differential wheel travel. No position correction from truth.
    """

    def __init__(self, radius=0.038, track=0.174, *, mode="fused"):
        if not math.isfinite(radius) or not math.isfinite(track) or radius <= 0 or track <= 0 or mode not in ("fused", "wheel"):
            raise ValueError("Positive radius/track and mode fused/wheel required")
        self.radius, self.track, self.mode = radius, track, mode
        self.state = Estimate()
        self._previous = None

    def update(self, time, angles_rad, gyro_z):
        angles = np.asarray(angles_rad, dtype=float)
        if angles.shape != (2,) or not np.isfinite(angles).all() or not np.isfinite([time, gyro_z]).all():
            raise ValueError("Expected finite time, two encoder angles, and gyro Z")
        previous = self._previous
        if previous is not None and time < previous[0]:
            raise ValueError("Time moved backwards; reset the estimator")
        self._previous = (float(time), angles.copy(), float(gyro_z))
        if previous is None or time == previous[0]:
            return self.state
        dt = time - previous[0]
        dl, dr = (angles - previous[1]) * self.radius
        ds = float((dl + dr) / 2)
        wheel_turn = float((dr - dl) / self.track)
        turn = (gyro_z + previous[2]) * dt / 2 if self.mode == "fused" else wheel_turn
        old = self.state
        mid = old.yaw_rad + turn / 2
        self.state = Estimate(
            old.time + dt, old.x_m + ds * math.cos(mid), old.y_m + ds * math.sin(mid),
            old.yaw_rad + turn, old.wheel_yaw_rad + wheel_turn, old.distance_m + ds,
            ds / dt, float(gyro_z),
        )
        return self.state

    def sample(self, robot):
        encoders = sensor.encoders.read(robot)
        gyro = sensor.imu.read(robot)["angular_velocity_rad_s"][2]
        return self.update(robot.time, encoders["position_rad"], float(gyro))

    @classmethod
    def for_robot(cls, robot, **options):
        radius = float(robot.model.geom("drive_left_tire").size[0])
        track = float(robot.model.body("left_wheel").pos[1] - robot.model.body("right_wheel").pos[1])
        estimator = cls(radius, track, **options)
        estimator.sample(robot)
        return estimator
