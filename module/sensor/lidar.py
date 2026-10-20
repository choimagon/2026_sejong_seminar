"""Lidar access independent of any GUI."""

import mujoco
import numpy as np

from ._common import require_sensor


def read(robot, num_rays=360, max_range=5.0):
    """Return a scan dict with angles_rad, ranges_m, and points_xy_m arrays.

    X is scanner-forward and Y left. inf/NaN mark missing ranges/points.
    """
    require_sensor(robot, "lidar")
    return read_lidar(robot.model, robot.data, num_rays, max_range)


def view(xml_kind="lidar", **options):
    """Open Controls and the LiDAR tab only, in a new simulation."""
    from . import view as open_monitor
    return open_monitor(xml_kind, sensors=("lidar",), **options)


def read_lidar(model, data, num_rays=360, max_range=5.0):
    """Cast a 360-degree scan from the existing lidar_scanner geom.

    Angles run counterclockwise from the scanner's +X (forward) toward +Y
    (left). Its position and orientation follow the robot. Ranges are in m;
    np.inf means no return. points_xy_m is in the scanner frame, with NaN for
    missing points. Call mj_forward after changing qpos before reading sensors.
    """
    if (isinstance(num_rays, (bool, np.bool_)) or not isinstance(num_rays, (int, np.integer))
            or num_rays < 1 or not np.isfinite(max_range) or max_range <= 0):
        raise ValueError("num_rays must be a positive integer; max_range must be finite and positive")
    lidar = model.geom("lidar_scanner")
    origin = data.geom_xpos[lidar.id].copy()
    rotation = data.geom_xmat[lidar.id].reshape(3, 3)
    angles = np.linspace(0.0, 2.0 * np.pi, num_rays, endpoint=False)
    local_directions = np.column_stack((np.cos(angles), np.sin(angles), np.zeros(num_rays)))
    world_directions = np.ascontiguousarray(local_directions @ rotation.T)
    distances = np.full(num_rays, -1.0)
    geom_ids = np.full(num_rays, -1, dtype=np.int32)
    mujoco.mj_multiRay(
        model, data, origin, world_directions.ravel(), None, True,
        int(lidar.bodyid[0]), geom_ids, distances, None, num_rays, max_range,
    )
    valid = (distances >= 0) & (distances <= max_range)
    points = np.full((num_rays, 2), np.nan)
    points[valid] = local_directions[valid, :2] * distances[valid, None]
    return {
        "angles_rad": angles,
        "ranges_m": np.where(valid, distances, np.inf),
        "points_xy_m": points,
        "origin_world_m": origin,
        "directions_world": world_directions,
        "geom_ids": np.where(valid, geom_ids, -1),
    }

