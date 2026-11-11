"""Supplied runner: sensor reads, odometry and stepping stay outside student tasks."""
import argparse
import math
from pathlib import Path

import mujoco
import numpy as np
from module import Robot, sensor
from module.course import Odometry, sector
from examples.world import world, MAPS


def arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--headless", action="store_true", help="run without windows or real-time waits")
    return parser.parse_args()


def load_move():
    """Compatibility for instructor capture helpers; return the user's public move."""
    from module.move import move
    return move


class Lab:
    def __init__(self, map_name="pillar", *, show=False, move=None, kind="all", xml_path=None):
        self.robot = Robot(xml_path if xml_path is not None else world(map_name, kind))
        self.sensors = sensor.available_sensors(self.robot.model)
        self.robot.run_for(.3)
        self.odom = Odometry.for_robot(self.robot)
        self.move = move
        self.contacts = 0
        self.path = []
        self.lidar_points, self.sonar_points = [], []
        self._next_sample = 0
        if show:
            viewer = self.robot.view()
            viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
            viewer.cam.lookat[:] = (1.1, 0, .1)
            viewer.cam.distance = 4.8
            viewer.cam.azimuth, viewer.cam.elevation = 90, -70

    def step(self, linear=0.0, angular=0.0):
        self.move(self.robot, linear, angular)
        self.robot.step()
        state = self.odom.sample(self.robot)
        for contact in self.robot.data.contact:
            names = [self.robot.model.geom(int(g)).name for g in (contact.geom1, contact.geom2)]
            if any(n.startswith("workshop_wall") or n == "workshop_pillar" for n in names):
                self.contacts += 1
        if self.robot.time >= self._next_sample:
            self.sample()
            self._next_sample = self.robot.time + .1
        return state

    def sample(self):
        state = self.odom.state
        c, s = math.cos(state.yaw_rad), math.sin(state.yaw_rad)
        rotation = np.array([[c, -s], [s, c]])
        origin = np.array([state.x_m, state.y_m])
        if "lidar" in self.sensors:
            scan = sensor.lidar.read(self.robot)
            points = scan['points_xy_m']
            points = points[np.isfinite(points).all(axis=1)]
            # The prepared LiDAR model has scanner XY=(0,0) in the base frame.
            self.lidar_points.extend(points @ rotation.T + origin)
        if "ultrasonic" in self.sensors:
            distances = sensor.ultrasonic.read(self.robot)
            for side, distance in zip(("left", "right"), distances):
                if np.isfinite(distance):
                    site = self.robot.model.site(f"ultra_{side}_ray_site")
                    point = site.pos[:2] + (distance, 0)
                    self.sonar_points.append(point @ rotation.T + origin)
        self.path.append((state.x_m, state.y_m))

    def run_for(self, linear, angular, seconds):
        end = self.robot.time + seconds
        while self.robot.time < end:
            self.step(linear, angular)

    def front(self, kind):
        if kind == "ultrasonic":
            return float(min(sensor.ultrasonic.read(self.robot)))
        return float(sector(sensor.lidar.read(self.robot), 0, 8))

    def turn(self, radians):
        target = self.odom.state.yaw_rad + radians
        deadline = self.robot.time + 12
        while abs(target - self.odom.state.yaw_rad) > .015:
            if self.robot.time > deadline:
                raise RuntimeError("Rotation did not finish; complete the two lines in 01_move.py")
            error = target - self.odom.state.yaw_rad
            self.step(0, float(np.clip(3 * error, -1, 1)))
        self.run_for(0, 0, .3)

    def forward(self, metres):
        target = self.odom.state.distance_m + metres
        deadline = self.robot.time + metres / .1 + 5
        while target - self.odom.state.distance_m > .008:
            if self.robot.time > deadline:
                raise RuntimeError("Movement did not finish; check 01_move.py or obstacle clearance")
            left = target - self.odom.state.distance_m
            self.step(min(.25, 1.5 * left), 0)
        self.run_for(0, 0, .3)

    def stop(self):
        self.run_for(0, 0, .5)

    def close(self):
        self.robot.close()

    def result(self):
        # Truth is used only for a teacher's validation/result, never control or mapping.
        xy = self.robot.data.qpos[:2].copy()
        goal_name = "course_goal" if mujoco.mj_name2id(self.robot.model, mujoco.mjtObj.mjOBJ_SITE, "course_goal") >= 0 else "workshop_goal"
        goal = self.robot.model.site(goal_name).pos[:2]
        return {"x_m": float(xy[0]), "y_m": float(xy[1]),
                "goal_reached": bool(np.linalg.norm(xy - goal) < .28),
                "obstacle_contacts": self.contacts, "simulation_s": self.robot.time}


def sensor_route(lab, choose, kind="ultrasonic", *, read_front=None):
    front = (lambda: read_front(lab.robot)) if read_front is not None else (lambda: lab.front(kind))
    # Students supply the approach decision; measured turns/distances are provided.
    deadline = lab.robot.time + 30
    start_distance = lab.odom.state.distance_m
    while True:
        command = choose(front())
        if command == (0.0, 0.0):
            if lab.odom.state.distance_m - start_distance < .02:
                raise RuntimeError("Complete choose(front) in 10_ultrasonic_route.py / 11_lidar_route.py before running,.")
            break
        if lab.robot.time > deadline:
            raise RuntimeError("Approach did not finish. Complete 01_move.py and 10_ultrasonic_route.py / 11_lidar_route.py,.")
        lab.step(*command)
    lab.stop()
    lab.turn(math.pi / 2)
    lab.forward(.8)
    lab.turn(-math.pi / 2)
    lab.forward(1.35)
    lab.turn(-math.pi / 2)
    lab.forward(.8)
    lab.turn(math.pi / 2)
    deadline = lab.robot.time + 30
    while front() > .45:
        if lab.robot.time > deadline:
            raise RuntimeError("Goal approach did not finish")
        lab.step(.2, 0)
    lab.stop()
    return lab.result()


def save_map(lab, *, show=True, name="sensor_map"):
    import matplotlib.pyplot as plt
    folder = Path(__file__).resolve().parents[1] / 'outputs/examples'
    folder.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    lidar = np.asarray(lab.lidar_points).reshape(-1, 2)
    sonar = np.asarray(lab.sonar_points).reshape(-1, 2)
    path = np.asarray(lab.path).reshape(-1, 2)
    if len(lidar): ax.scatter(*lidar.T, s=1, alpha=.2, label='LiDAR endpoints')
    if len(sonar): ax.scatter(*sonar.T, s=8, label='Ultrasonic endpoints')
    if len(path): ax.plot(*path.T, color='black', label='Encoder + IMU path')
    ax.set(xlabel='Estimated X (m)', ylabel='Estimated Y (m)',
           title='Accumulated sensor points (no SLAM or ground-truth pose)', aspect='equal')
    ax.legend()
    filename = folder / f"{name}.png"
    fig.savefig(filename, dpi=160)
    np.savez(folder / f"{name}.npz", lidar=lidar, ultrasonic=sonar, path=path)
    print('Saved:', filename)
    if show: plt.show()
    plt.close(fig)
    return filename
