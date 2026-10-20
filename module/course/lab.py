"""Prepared-course runner and sensor plots shared by the teaching examples."""

import math

import numpy as np

from ..robot import Robot
from . import scenes
from .runtime import Session, load_policy, sector


def practice(case, kind, policy, *, view=True, motor_speed=0.30, show_plot=True):
    """Run an importable policy in the native GUI or headlessly with plots."""
    world = scenes.scenario(case, kind)
    if view:
        from . import view as open_view
        return open_view(world, policy=policy, max_sim_time=None,
                         motor_speed=motor_speed, playback_speed=1)
    selected = load_policy(policy) if isinstance(policy, str) else policy
    rows = []
    with Robot(world.path, motor_speed=motor_speed) as robot:
        robot.run_for(0.5)
        session = Session(robot, selected, max_sim_time=None)
        following = robot.time
        while not session.done:
            session.advance()
            if robot.time >= following:
                observation = session.observe()
                wheels = observation.encoders["velocity_rad_s"]
                distances = ([sector(observation.lidar, angle, 10) for angle in (0, 90, -90)]
                             if observation.lidar is not None else
                             [float(min(observation.ultrasonic)), math.nan, math.nan])
                rows.append([observation.time_s, session.estimate.x_m, session.estimate.y_m,
                             math.degrees(session.estimate.yaw_rad), *wheels, *distances])
                following = robot.time + 0.05
        result = session.result()
        result["case"], result["sensor"] = case, kind
        result["seed"] = world.seed
        result["scan_samples"] = getattr(selected, "samples", [])
        if show_plot:
            result["graph"] = str(plot(robot, session, selected, rows, case, kind))
        print(result, flush=True)
        return result


def plot(robot, session, policy, rows, case, kind):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    values = np.asarray(rows)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    path, ranges, heading, wheels = axes.flat
    for index in range(robot.model.ngeom):
        if robot.model.geom(index).name.startswith("course_wall_"):
            sx, sy = robot.model.geom_size[index, :2]
            corners = np.array(((-sx, -sy), (sx, -sy), (sx, sy), (-sx, sy)))
            rotation = robot.data.geom_xmat[index].reshape(3, 3)[:2, :2]
            origin = robot.data.geom_xpos[index, :2] - session._origin
            path.add_patch(Polygon(corners @ rotation.T + origin, color="0.8"))
    path.plot(values[:, 1], values[:, 2], color="#14785e", label="Encoder + IMU")
    path.set(xlabel="X (m)", ylabel="Y (m)", aspect="equal", title="Prepared course / estimated path")
    path.autoscale_view()
    path.legend()
    for column, label in zip((6, 7, 8), ("Sensor forward", "LiDAR left", "LiDAR right")):
        if kind == "lidar" or column == 6:
            ranges.plot(values[:, 0], np.where(np.isfinite(values[:, column]), values[:, column], np.nan), label=label)
    for direction in ("left", "right"):
        samples = [row for row in getattr(policy, "samples", []) if row["direction"] == direction]
        if samples:
            ranges.scatter([row["time_s"] for row in samples], [row["distance_m"] for row in samples],
                           marker="x", s=55, label=f"Ultrasonic {direction} scan")
    ranges.set(xlabel="Simulation time (s)", ylabel="Range (m)", title="Measured ranges / scan timestamps")
    ranges.legend()
    heading.plot(values[:, 0], values[:, 3], label="IMU integrated yaw")
    heading.set(xlabel="Simulation time (s)", ylabel="Heading (deg)")
    heading.legend()
    for column, label in ((4, "Left encoder"), (5, "Right encoder")):
        wheels.plot(values[:, 0], values[:, column], label=label)
    wheels.set(xlabel="Simulation time (s)", ylabel="Wheel speed (rad/s)")
    wheels.legend()
    for axis in axes.flat:
        axis.grid(alpha=0.2)
    style = getattr(policy, "turn_style", "straight")
    fig.suptitle(f"{kind} / {case} / {style} | wall contacts {session.collisions}")
    folder = scenes.OUTPUT / "course_labs"
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / f"{kind}_{case}_{style}.png"
    fig.savefig(output, dpi=130)
    plt.show()
    return output
