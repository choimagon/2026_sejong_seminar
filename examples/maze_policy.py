"""제공 미로 데모 정책: 수업에서는 전체 구현 대신 조건 하나를 관찰합니다."""
import math

import numpy as np

from module import course


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class Policy:
    """Choose paths at cell centers and send continuous (linear, angular).

    The known grid pitch is 0.30 m. LiDAR wall lines correct encoder drift
    against that grid; their connectivity and the exit remain unknown.
    Coordinates track the wheel axle, 3 cm in front of the LiDAR/base origin.
    """

    CELL = 0.30
    AXLE_OFFSET = 0.030
    SPEED = 0.30
    TURN_SPEED = 2.00
    DIRECTIONS = np.array(((1, 0), (0, 1), (-1, 0), (0, -1)))

    def __init__(self):
        self.cell = np.array((0, 0))
        self.heading = 0
        self.correction = np.zeros(2)
        self.phase = "choose"
        self.settled = None
        self.message = "Starting at blue cell"
        self.cells_visited = 0

    def _ranges(self, observation):
        scan = observation.lidar
        if scan is None:
            raise ValueError("The 30 cm maze example requires the all or lidar model")
        yaw = observation.estimate.yaw_rad
        readings = []
        for direction in range(4):
            wanted = direction * math.pi/2 - yaw
            delta = np.arctan2(np.sin(scan["angles_rad"] - wanted),
                               np.cos(scan["angles_rad"] - wanted))
            index = int(np.argmin(np.abs(delta)))
            readings.append(float(scan["ranges_m"][index] * math.cos(delta[index])))
        return np.array(readings)

    def _position(self, observation, ranges):
        estimate = observation.estimate
        yaw = estimate.yaw_rad
        offset = self.AXLE_OFFSET * np.array((math.cos(yaw), math.sin(yaw)))
        odometry = np.array((estimate.x_m, estimate.y_m))
        sensor_position = odometry + self.correction - offset
        # Every wall is on a half-cell grid line. Use the nearest consistent
        # line to correct small slip, without any layout or truth coordinates.
        for axis, directions in ((0, (0, 2)), (1, (1, 3))):
            measurements = []
            for direction in directions:
                distance = ranges[direction]
                if not math.isfinite(distance):
                    continue
                sign = self.DIRECTIONS[direction, axis]
                wall = sensor_position[axis] + sign * distance
                grid_wall = round((wall - self.CELL/2) / self.CELL) * self.CELL + self.CELL/2
                candidate = grid_wall - sign * distance + offset[axis]
                if abs(candidate - (odometry[axis] + self.correction[axis])) < self.CELL/4:
                    measurements.append(candidate)
            if measurements:
                corrected = float(np.median(measurements)) - odometry[axis]
                self.correction[axis] += 0.6 * (corrected - self.correction[axis])
        return odometry + self.correction

    def velocity(self, observation):
        if observation.time_s < 0.5:
            return 0.0, 0.0
        ranges = self._ranges(observation)
        position = self._position(observation, ranges)
        yaw = observation.estimate.yaw_rad
        if self.phase == "choose":
            for direction in ((self.heading+1) % 4, self.heading,
                              (self.heading-1) % 4, (self.heading+2) % 4):
                distance = ranges[direction] - self.AXLE_OFFSET * math.cos(direction*math.pi/2-yaw)
                if distance > self.CELL*0.85:
                    self.target_heading = direction
                    self.target_cell = self.cell + self.DIRECTIONS[direction]
                    self.phase = "turn"
                    self.settled = None
                    break
            else:
                raise RuntimeError("No open passage at the current cell")
        heading = self.target_heading * math.pi/2
        heading_error = wrap(heading-yaw)
        if self.phase == "turn":
            self.message = f"Turn toward next passage | cells {self.cells_visited}"
            if abs(heading_error) < math.radians(0.7) and abs(observation.estimate.gyro_rad_s) < 0.06:
                if self.settled is None:
                    self.settled = observation.time_s
                if observation.time_s-self.settled >= 0.15:
                    self.phase = "drive"
                    self.settled = None
                return 0.0, 0.0
            self.settled = None
            # Brake before the next cell heading, while the shared wheel
            # driver limits actual angular acceleration to 2.4 rad/s^2.
            rate = min(self.TURN_SPEED, 4.0*abs(heading_error),
                       math.sqrt(3.6*abs(heading_error)))
            return 0.0, math.copysign(rate, heading_error)

        direction = self.DIRECTIONS[self.target_heading]
        left = np.array((-direction[1], direction[0]))
        delta = self.target_cell*self.CELL-position
        along, cross = float(delta @ direction), float(delta @ left)
        self.message = f"Drive to next 30 cm cell | cells {self.cells_visited}"
        if abs(along) < 0.006 and abs(cross) < 0.015 and abs(observation.estimate.velocity_m_s) < 0.02:
            if self.settled is None:
                self.settled = observation.time_s
            if observation.time_s-self.settled >= 0.10:
                self.cell = self.target_cell.copy()
                self.heading = self.target_heading
                self.phase = "choose"
                self.cells_visited += 1
                self.settled = None
            return 0.0, 0.0
        self.settled = None
        # Keep a braking-distance margin within a 30 cm cell. Increasing the
        # motor speed must not carry the robot past the turn center.
        speed = min(self.SPEED, 3.0*abs(along), math.sqrt(0.60*abs(along)))
        linear = math.copysign(min(speed, 0.05) if along < 0 else speed, along)
        angular = float(np.clip(3.5*heading_error + 8.0*cross, -1.2, 1.2))
        if abs(heading_error) > 0.4:
            linear = 0.0
        # Extra stopping clearance for the forward ultrasonic face.
        if observation.ultrasonic is not None and min(observation.ultrasonic) < 0.025 and linear > 0:
            linear = 0.0
        return linear, angular

