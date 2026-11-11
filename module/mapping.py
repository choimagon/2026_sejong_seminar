"""Live endpoint mapping from sensor readings and encoder/IMU odometry only."""

import math
from pathlib import Path

import mujoco
import numpy as np


class MappingSession:
    """Provide the estimated sensor pose to a student's append callback."""

    def __init__(self, model, kind, add_points):
        if kind not in ("ultrasonic", "lidar") or not callable(add_points):
            raise ValueError("Mapping needs one distance sensor and an add_points callback")
        self.kind, self.add_points = kind, add_points
        mount = model.site("ultra_front_ray_site") if kind == "ultrasonic" else model.geom("lidar_scanner")
        self.offset = mount.pos[:2].copy()
        # Encoder integration follows the wheel axle, which is ahead of base.
        self.axle_offset = (model.body("left_wheel").pos[:2] +
                            model.body("right_wheel").pos[:2]) / 2
        rotation = np.empty(9)
        mujoco.mju_quat2Mat(rotation, mount.quat)
        direction = rotation.reshape(3, 3)[:, 2 if kind == "ultrasonic" else 0]
        self.mount_yaw = math.atan2(direction[1], direction[0])
        self.clear()

    def clear(self):
        self.points, self.path = [], []
        self._preview_cells = {}
        self.last_time = None
        self.sensor_pose = (0., 0., 0.)
        self.saved_path = None

    def update(self, packet):
        moment = float(packet["time"])
        if self.last_time is not None and moment < self.last_time:
            self.clear()
        if self.last_time is not None and moment - self.last_time < .099:
            return
        estimate = packet.get("odometry")
        if estimate is None or self.kind not in packet:
            return
        # Never use truth_x/y/yaw, world sensor coordinates, or geom IDs here.
        x, y, yaw = (float(estimate[k]) for k in
                     ("estimated_x_m", "estimated_y_m", "estimated_yaw_rad"))
        c, s = math.cos(yaw), math.sin(yaw)
        base_x = x + self.axle_offset[0] - c*self.axle_offset[0] + s*self.axle_offset[1]
        base_y = y + self.axle_offset[1] - s*self.axle_offset[0] - c*self.axle_offset[1]
        sensor_x = base_x + c * self.offset[0] - s * self.offset[1]
        sensor_y = base_y + s * self.offset[0] + c * self.offset[1]
        self.sensor_pose = (sensor_x, sensor_y, yaw + self.mount_yaw)
        previous_count = len(self.points)
        self.add_points(packet[self.kind], *self.sensor_pose, self.points)
        # A display-only 2 cm bin removes duplicate samples before decimation.
        # Otherwise a stride matching the 360-ray scan can hide whole walls.
        for point in self.points[previous_count:]:
            px, py = point
            if not math.isfinite(px) or not math.isfinite(py):
                raise ValueError("Map coordinates must be finite; skip inf readings in add_points")
            self._preview_cells[(math.floor(px/.02), math.floor(py/.02))] = (px, py)
        self.path.append((base_x, base_y))
        self.last_time = moment

    def arrays(self):
        points = np.asarray(self.points, dtype=float).reshape(-1, 2)
        path = np.asarray(self.path, dtype=float).reshape(-1, 2)
        if not np.isfinite(points).all():
            raise ValueError("Map coordinates must be finite; skip inf readings in add_points")
        return points, path

    def draw(self, figure):
        points = np.asarray(list(self._preview_cells.values()), dtype=float).reshape(-1, 2)
        path = np.asarray(self.path, dtype=float).reshape(-1, 2)
        figure.linepnt[:] = 0
        capacity = figure.linedata.shape[1] // 2

        def segments(index, vertices):
            vertices = np.asarray(vertices).reshape(-1, 2)[:capacity]
            figure.linepnt[index] = len(vertices)
            figure.linedata[index, :vertices.size] = vertices.ravel()

        # Keep all measured points for saving; only decimate the live preview.
        shown = points[::max(1, math.ceil(len(points) / max(1, capacity // 2)))]
        if len(shown):
            ticks = np.stack((shown - (.012, 0), shown + (.012, 0)), axis=1)
            segments(0, ticks)
        route = path[::max(1, math.ceil(len(path) / max(2, capacity // 2)))]
        if len(route) > 1:
            segments(1, np.stack((route[:-1], route[1:]), axis=1))
        if len(path):
            x, y = path[-1]
            segments(2, [(x-.035, y), (x+.035, y), (x, y-.035), (x, y+.035)])
        cloud = np.vstack((shown, route))
        if len(cloud):
            lo, hi = cloud.min(axis=0), cloud.max(axis=0)
            middle = (lo + hi) / 2
            half = max(1., float((hi - lo).max()) / 2 + .25)
            figure.range[:] = ((middle[0]-half, middle[0]+half),
                               (middle[1]-half, middle[1]+half))

    def save(self, folder=None):
        """Save accumulated endpoints separately from the estimated robot path."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        folder = Path(folder) if folder is not None else Path(__file__).resolve().parents[1] / "outputs/examples"
        folder.mkdir(parents=True, exist_ok=True)
        points, path = self.arrays()
        filename = folder / f"{self.kind}_map.png"
        fig, ax = plt.subplots(figsize=(8, 6))
        if len(points):
            ax.scatter(*points.T, s=2 if self.kind == "lidar" else 8, alpha=.35,
                       label=f"{self.kind.title()} measured endpoints")
        if len(path):
            ax.plot(*path.T, color="black", label="Encoder + IMU path")
        ax.set(xlabel="Estimated X (m)", ylabel="Estimated Y (m)",
               title="Manual driving: accumulated sensor endpoints", aspect="equal")
        if len(points) or len(path):
            ax.legend()
        fig.savefig(filename, dpi=160)
        plt.close(fig)
        empty = np.empty((0, 2))
        np.savez(filename.with_suffix(".npz"), path=path,
                 ultrasonic=points if self.kind == "ultrasonic" else empty,
                 lidar=points if self.kind == "lidar" else empty)
        self.saved_path = filename
        return filename
