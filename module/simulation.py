"""The native MuJoCo viewer, physics loop, and local GUI connection."""

from multiprocessing import Pipe
from pathlib import Path
import subprocess
import sys
import time

import mujoco
import mujoco.viewer
import numpy as np

from .models import resolve_xml
from .robot import Robot
from .motion import execute, set_speed, status, stop
from .motion.commands import FORWARD_SPEED, MotionCommand
from .sensor import read_lidar, select_sensors, sensor_snapshot
from .playback import validate_speed


def run_simulation(connection, xml_path="all", control_enabled=False, *, sensors=None, demo=True,
                   course=False, policy=None, max_sim_time=600, playback_speed=1.0,
                   motor_speed=FORWARD_SPEED):
    """Own the physics and native MuJoCo viewer; publish sensor snapshots."""
    playback_speed = validate_speed(playback_speed)
    robot = Robot(xml_path, demo=demo, motor_speed=motor_speed)
    model, data = robot.model, robot.data
    sensors = select_sensors(model, sensors)
    state = {"paused": False, "reset": False, "close": False, "drive": np.zeros(2),
             "playback_speed": playback_speed, "camera": None, "following": False}

    def on_viewer_key(key):
        if key == 32:
            state["paused"] = not state["paused"]
        elif key == ord("R"):
            state["reset"] = True
        elif key == ord("F"):
            state["camera"] = "overview" if state["following"] else "follow"
        elif key == ord("H"):
            state["camera"] = "overview"

    if control_enabled:
        robot._enable_motion()
    def new_lesson():
        if not course:
            return None
        from .course import Session, load_policy
        return Session(robot, load_policy(policy) if policy is not None else None, max_sim_time=max_sim_time)
    lesson = new_lesson()
    accumulator = 0.0
    last_scan = last_publish = previous_sim_time = -1.0
    scan = read_lidar(model, data) if "lidar" in sensors else None
    try:
        # mjpython supplies the macOS UI thread for the standard viewer.
        with mujoco.viewer.launch_passive(model, data, key_callback=on_viewer_key) as viewer:
            with viewer.lock():
                viewer.cam.lookat[:] = (0.1, 0.0, 0.1)
                viewer.cam.distance = 1.1
                viewer.cam.azimuth = 150
                viewer.cam.elevation = -30
                if course:
                    viewer.cam.lookat[:] = model.stat.center
                    viewer.cam.distance = (3 if model.stat.extent >= 2 else 2) * model.stat.extent
                    viewer.cam.azimuth = 90
                    viewer.cam.elevation = -90 if model.stat.extent >= 2 else -65
                    viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_RANGEFINDER] = False
            last_wall_time = time.perf_counter()
            while viewer.is_running() and not state["close"]:
                frame_start = time.perf_counter()
                elapsed = min(frame_start - last_wall_time, 0.1)
                last_wall_time = frame_start
                while connection.poll():
                    message = connection.recv()
                    if message["action"] == "pause":
                        state["paused"] = not state["paused"]
                    elif message["action"] == "speed":
                        state["playback_speed"] = validate_speed(message["value"])
                        accumulator = 0.0
                    elif message["action"] == "motor_speed":
                        set_speed(robot, message["value"])
                    elif message["action"] == "camera":
                        state["camera"] = message["mode"]
                    elif message["action"] == "reset":
                        state["reset"] = True
                    elif message["action"] == "drive":
                        state["drive"] = np.array(message["value"], dtype=float)
                    elif message["action"] == "motion":
                        command = MotionCommand(**message["command"])
                        if lesson is None:
                            execute(robot, command, wait=False)
                        else:
                            from .course import Action
                            kind = ("left" if command.amount >= 0 else "right") if command.kind == "rotate" else command.kind
                            lesson.policy = None
                            lesson.enqueue(Action(kind, abs(command.amount)))
                    elif message["action"] == "stop":
                        stop(robot)
                        if lesson is not None:
                            lesson.stop()
                        state["drive"][:] = 0
                    elif message["action"] == "close":
                        state["close"] = True
                if state["close"]:
                    break

                with viewer.lock():
                    if state["camera"] is not None:
                        state["following"] = state["camera"] == "follow"
                        viewer.cam.type = (mujoco.mjtCamera.mjCAMERA_TRACKING if state["following"]
                                           else mujoco.mjtCamera.mjCAMERA_FREE)
                        viewer.cam.trackbodyid = model.body("base").id
                        viewer.cam.lookat[:] = data.xpos[model.body("base").id] if state["following"] else model.stat.center
                        viewer.cam.distance = (1.5 if state["following"] else
                                               (3 if model.stat.extent >= 2 else 2)*model.stat.extent)
                        viewer.cam.azimuth = 90
                        viewer.cam.elevation = -70 if state["following"] else -90
                        state["camera"] = None
                    if state["reset"]:
                        robot.reset()
                        lesson = new_lesson()
                        state["drive"][:] = 0
                        state["reset"] = False
                        accumulator = 0
                        last_scan = -1
                    if data.time < previous_sim_time:
                        if robot._controller is not None:
                            robot._controller.reset()
                            robot._driver.reset()
                        lesson = new_lesson()
                        state["drive"][:] = 0
                        accumulator = 0
                        last_scan = -1
                    previous_sim_time = data.time
                    if not state["paused"]:
                        accumulator += elapsed * state["playback_speed"]
                        frame_steps = 0
                        while accumulator >= model.opt.timestep and frame_steps < 200:
                            manual = state["drive"] * (robot.motor_speed / FORWARD_SPEED)
                            if lesson is not None:
                                lesson.advance(manual=manual)
                            else:
                                if robot._mode == "velocity":
                                    robot._manual = tuple(manual)
                                robot.step()
                            accumulator -= model.opt.timestep
                            frame_steps += 1
                    else:
                        accumulator = 0
                    mujoco.mj_forward(model, data)
                    if "lidar" in sensors and (data.time - last_scan >= 0.1 or last_scan < 0):
                        scan = read_lidar(model, data)
                        last_scan = data.time
                    snapshot = None
                    if frame_start - last_publish >= 0.05:
                        snapshot = sensor_snapshot(model, data, sensors, scan)
                        snapshot["paused"] = state["paused"]
                        snapshot["playback_speed"] = state["playback_speed"]
                        snapshot["motor_speed"] = robot.motor_speed
                        snapshot["motion"] = status(robot)
                        if lesson is not None:
                            snapshot["motion"] = {**lesson.controller.result, "pending": len(lesson.queue)}
                            snapshot["odometry"] = lesson.telemetry()
                        last_publish = frame_start
                viewer.sync()
                if snapshot is not None:
                    connection.send(snapshot)
                time.sleep(max(0.0, 1 / 60 - (time.perf_counter() - frame_start)))
    except (BrokenPipeError, EOFError, ConnectionResetError):
        pass
    finally:
        if lesson is not None:
            lesson.save_csv(f"gui_{Path(xml_path).stem}")
        robot.close()
        connection.close()


def start_simulation(xml_path="all", control_enabled=False, *, sensors=None, demo=True,
                     course=False, policy=None, max_sim_time=600, playback_speed=1.0,
                     motor_speed=FORWARD_SPEED):
    """Start one native viewer process and connect its telemetry to the GUI."""
    playback_speed = validate_speed(playback_speed)
    connection, child_connection = Pipe()
    interpreter = Path(sys.executable)
    if sys.platform == "darwin":
        interpreter = interpreter.with_name("mjpython")
    code = ("from multiprocessing.connection import Connection; "
            "from module.simulation import run_simulation; "
            f"run_simulation(Connection({child_connection.fileno()}), {str(resolve_xml(xml_path))!r}, "
            f"{control_enabled!r}, sensors={sensors!r}, demo={demo!r}, "
            f"course={course!r}, policy={policy!r}, max_sim_time={max_sim_time!r}, "
            f"playback_speed={playback_speed!r}, motor_speed={motor_speed!r})")
    try:
        process = subprocess.Popen(
            [str(interpreter), "-c", code], cwd=Path(__file__).resolve().parent.parent,
            pass_fds=(child_connection.fileno(),),
        )
    except Exception:
        connection.close()
        raise
    finally:
        child_connection.close()
    return process, connection

