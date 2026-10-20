"""Separate sensor GUI with tabs; the native 3D viewer runs independently."""

from collections import deque
import subprocess
import time

import glfw
import mujoco
import numpy as np

from .models import load_sensor_scene, resolve_xml
from .guide import contains, draw_guide, guide_layout
from .motion.keyboard import keyboard_control
from .motion.commands import FORWARD_SPEED, MotionCommand, normalize_commands, parse_command
from .motion.speed import angular_speed, next_motor_speed, validate_motor_speed
from .sensor import SENSOR_LABELS, select_sensors
from .simulation import start_simulation
from .plotting import make_figure, update_history_figure
from .playback import validate_speed


def sensor_tab_at(x, y, width, count):
    """Return the tab at a GLFW mouse position (logical pixels, top origin)."""
    if count and 64 <= y < 118 and 12 <= x < width - 12:
        return min(count - 1, int((x - 12) / ((width - 24) / count)))
    return None


def view(xml_kind="all", *, sensors=None, control=keyboard_control, commands=None, demo=True,
         course=False, policy=None, max_sim_time=600, playback_speed=1.0, motor_speed=FORWARD_SPEED,
         playback_controls=False):
    """Open the selected model and only its sensor tabs; block until GUI closes.

    xml_kind: all/basic/lidar/sonic, model_all.xml, or an existing XML path.
    control: callback control(pressed) -> (forward_m_s, left_rad_s).
    commands: optional list of motion.commands descriptions
              or strings such as "forward 0.3" and "rotate 90".
    sensors: None for all present sensors, a sequence of group names for a
             subset, or () for Controls only with no sensor polling/plots.
    demo: add the optional sensor test area; XML files are not modified.
    course: use estimated motion for typed commands and automatic policies.
            policy: optional import spec for automatic decisions.
    motor_speed: actual chassis speed setting (m/s), adjustable with Motor or +/-.
    playback_speed: explicit wall-clock multiplier; default 1 (real time).
    playback_controls: enable speed <multiplier> and [/] during this session.
    The callback runs while this GUI has focus; releasing keys or switching
    windows sends a stop command. Without it, use MuJoCo's actuator controls.
    """
    playback_speed = validate_speed(playback_speed)
    motor_speed = validate_motor_speed(motor_speed)
    xml_path = resolve_xml(xml_kind)
    commands = normalize_commands(commands)
    model = load_sensor_scene(xml_path, demo=demo)
    sensors = select_sensors(model, sensors)
    tabs = ("controls", *sensors)
    tab_labels = {"controls": "Controls", **SENSOR_LABELS}
    if not glfw.init():
        raise RuntimeError("GLFW could not initialize the display")
    work_x, work_y, work_width, work_height = glfw.get_monitor_workarea(glfw.get_primary_monitor())
    gui_width = min(1040, max(760, int(work_width * 0.42)))
    gui_height = min(800, max(620, work_height - 80))
    title = "Sensor Monitor" if sensors else "Motion Controls"
    window = glfw.create_window(gui_width, gui_height, f"TurtleBot - {title}", None, None)
    if window is None:
        glfw.terminate()
        raise RuntimeError("Could not open the sensor monitor")
    glfw.set_window_size_limits(window, 760, 620, glfw.DONT_CARE, glfw.DONT_CARE)
    glfw.set_window_pos(window, work_x + work_width - gui_width - 20, work_y + 40)
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    # The GUI uses MuJoCo's 2D plotting only. All physics and 3D rendering live
    # in the separate native viewer process, with no second simulation here.
    context = mujoco.MjrContext(model, mujoco.mjtFontScale.mjFONTSCALE_100)
    try:
        simulation_options = {"sensors": sensors, "demo": demo, "playback_speed": playback_speed,
                              "motor_speed": motor_speed}
        if course:
            simulation_options.update(course=True, policy=policy, max_sim_time=max_sim_time)
        process, connection = start_simulation(xml_path, control_enabled=control is not None,
                                             **simulation_options)
    except Exception:
        context.free()
        glfw.destroy_window(window)
        glfw.terminate()
        raise
    state = {"tab": 0, "connected": True, "focused_once": False,
             "editing": False, "entry": "", "message": "", "motor_speed": motor_speed,
             "playback_speed": playback_speed}
    latest = None
    history = deque(maxlen=201)
    previous_drive = None

    xyz = [(1.0, 0.4, 0.35), (0.35, 0.9, 0.55), (0.35, 0.65, 1.0)]
    lr = [(0.3, 0.85, 1.0), (1.0, 0.65, 0.25)]
    acceleration = make_figure("Acceleration (m/s^2)", ("X", "Y", "Z"), xyz) if "imu" in sensors else None
    gyro = make_figure("Angular velocity (rad/s)", ("X", "Y", "Z"), xyz) if "imu" in sensors else None
    encoder_angle = make_figure("Wheel angle (rad)", ("Left", "Right"), lr) if "encoders" in sensors else None
    encoder_velocity = make_figure("Wheel angular velocity (rad/s)", ("Left", "Right"), lr) if "encoders" in sensors else None
    ultrasonic = make_figure("Ultrasonic distance (m) - gaps mean no return", ("Left", "Right"), lr) if "ultrasonic" in sensors else None
    lidar = (make_figure("2D LiDAR - scanner frame", ("Returns", "Robot", "Forward"),
                         ((0.3, 1.0, 0.6), (1.0, 0.6, 0.2), (1.0, 0.6, 0.2)))
             if "lidar" in sensors else None)
    if lidar is not None:
        lidar.xlabel = "X forward (m); Y left (m)"
        lidar.flg_legend = 0
        lidar.flg_barplot = 1
        lidar.range[:] = ((-3.0, 3.0), (-3.0, 3.0))
        lidar.linepnt[1:3] = 2
        lidar.linedata[1, :4] = (-0.06, 0, 0.06, 0)
        lidar.linedata[2, :4] = (0, 0, 0.25, 0)
    def send(action, **values):
        if state["connected"]:
            try:
                connection.send({"action": action, **values})
            except (BrokenPipeError, EOFError, OSError):
                state["connected"] = False

    def submit_command():
        if not state["connected"]:
            state["message"] = "MuJoCo viewer is closed"
            return
        try:
            words = state["entry"].lower().split()
            if playback_controls and words and words[0] == "speed":
                if len(words) != 2:
                    raise ValueError("Use: speed <positive multiplier>")
                change_playback(words[1])
                state["editing"] = False
            elif state["entry"].strip().lower() == "stop":
                send("stop")
                state["message"] = "Stopped; command queue cleared"
            else:
                command = parse_command(state["entry"])
                speed = angular_speed(state["motor_speed"]) if command.kind == "rotate" else state["motor_speed"]
                command = MotionCommand(command.kind, command.amount, speed)
                send("motion", command=command.to_dict())
                unit = "deg" if command.kind == "rotate" else "m"
                state["message"] = f"Queued: {command.kind} {command.amount:g} {unit}"
            state["entry"] = ""
        except (ValueError, TypeError) as error:
            state["message"] = f"Error: {error}"

    def change_speed(direction=1, *, wrap=False):
        speed = next_motor_speed(state["motor_speed"], direction, wrap=wrap)
        state["motor_speed"] = speed
        send("motor_speed", value=speed)

    def change_playback(value):
        speed = validate_speed(value)
        state["playback_speed"] = speed
        send("speed", value=speed)
        state["message"] = f"Playback {speed:g}x; motor targets unchanged"

    def on_character(_window, codepoint):
        if state["editing"] and 32 <= codepoint < 127 and len(state["entry"]) < 80:
            state["entry"] += chr(codepoint)

    def on_key(_window, key, _scancode, action, _mods):
        if action not in (glfw.PRESS, glfw.REPEAT):
            return
        if state["editing"]:
            if key == glfw.KEY_BACKSPACE:
                state["entry"] = state["entry"][:-1]
            elif key in (glfw.KEY_ENTER, glfw.KEY_KP_ENTER):
                submit_command()
            elif key == glfw.KEY_ESCAPE:
                state["editing"] = False
            return
        if action != glfw.PRESS:
            return
        if glfw.KEY_1 <= key < glfw.KEY_1 + len(tabs):
            state["tab"] = key - glfw.KEY_1
        elif playback_controls and key in (glfw.KEY_LEFT_BRACKET, glfw.KEY_RIGHT_BRACKET):
            try:
                change_playback(state["playback_speed"] * (0.5 if key == glfw.KEY_LEFT_BRACKET else 2))
            except ValueError as error:
                state["message"] = f"Error: {error}"
        elif key in (glfw.KEY_EQUAL, glfw.KEY_KP_ADD):
            change_speed(1)
        elif key in (glfw.KEY_MINUS, glfw.KEY_KP_SUBTRACT):
            change_speed(-1)
        elif key == glfw.KEY_SPACE:
            send("pause")
        elif key == glfw.KEY_R:
            send("reset")
        elif key == glfw.KEY_F:
            send("camera", mode="follow")
        elif key == glfw.KEY_H:
            send("camera", mode="overview")
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

    def on_click(_window, button, action, _mods):
        if button != glfw.MOUSE_BUTTON_LEFT or action != glfw.PRESS:
            return
        x, y = glfw.get_cursor_pos(window)
        width, height = glfw.get_window_size(window)
        tab = sensor_tab_at(x, y, width, len(tabs))
        if tab is not None:
            state["tab"] = tab
            state["editing"] = False
        elif state["tab"] == 0 and contains(guide_layout(width)["entry"], x, y):
            state["editing"] = True
        elif state["tab"] == 0 and contains(guide_layout(width)["submit"], x, y):
            submit_command()
        elif height - 54 <= y < height - 10:
            if 12 <= x < 132:
                send("pause")
            elif 144 <= x < 244:
                send("reset")
            elif 256 <= x < 356:
                send("stop")
            elif width - 132 <= x < width - 12:
                change_speed(wrap=True)
            elif playback_controls and width - 272 <= x < width - 144:
                state["tab"] = 0
                state["entry"] = f"speed {state['playback_speed']:g}"
                state["editing"] = True
                return
            state["editing"] = False
        else:
            state["editing"] = False

    glfw.set_key_callback(window, on_key)
    glfw.set_mouse_button_callback(window, on_click)
    glfw.set_char_callback(window, on_character)
    font = mujoco.mjtFont.mjFONT_NORMAL
    top_left = mujoco.mjtGridPos.mjGRID_TOPLEFT

    def text(rect, labels, values=""):
        mujoco.mjr_overlay(font, top_left, rect, labels, values, context)

    def label(rect, caption, selected=False):
        color = (0.13, 0.34, 0.58) if selected else (0.12, 0.16, 0.21)
        mujoco.mjr_label(rect, font, caption, *color, 1, 0.95, 0.97, 1, context)

    def pressed(key):
        return glfw.get_key(window, ord(key.upper())) == glfw.PRESS

    print(f"Opened {xml_path.name}: {', '.join(SENSOR_LABELS[sensor] for sensor in sensors) or 'Controls only'}", flush=True)
    for command in commands:
        send("motion", command=command.to_dict())
    try:
        while not glfw.window_should_close(window):
            frame_start = time.perf_counter()
            glfw.poll_events()
            try:
                while state["connected"] and connection.poll():
                    latest = connection.recv()
                    if not state["focused_once"]:
                        glfw.focus_window(window)
                        state["focused_once"] = True
                    if history and latest["time"] < history[-1]["time"]:
                        history.clear()
                    if not history or latest["time"] > history[-1]["time"]:
                        sample = {"time": latest["time"]}
                        if "imu" in sensors:
                            sample["acceleration"] = latest["imu"]["acceleration_m_s2"]
                            sample["gyro"] = latest["imu"]["angular_velocity_rad_s"]
                        if "encoders" in sensors:
                            sample["encoder_velocity"] = latest["encoders"]["velocity_rad_s"]
                            sample["encoder_angle"] = latest["encoders"]["position_rad"]
                        if "ultrasonic" in sensors:
                            sample["ultrasonic"] = latest["ultrasonic"]
                        history.append(sample)
                        for figure, key in ((acceleration, "acceleration"), (gyro, "gyro"),
                                            (encoder_velocity, "encoder_velocity"),
                                            (ultrasonic, "ultrasonic"), (encoder_angle, "encoder_angle")):
                            if key in sample:
                                update_history_figure(figure, history, key)
            except (EOFError, OSError):
                state["connected"] = False
            if process.poll() is not None:
                state["connected"] = False

            if control is not None:
                focused = glfw.get_window_attrib(window, glfw.FOCUSED)
                drive = tuple(control(pressed)) if focused and not state["editing"] else (0.0, 0.0)
                if len(drive) != 2 or not np.isfinite(drive).all():
                    raise ValueError("control must return finite (forward_m_s, left_turn_rad_s)")
                if drive != previous_drive:
                    send("drive", value=drive)
                    previous_drive = drive

            width, height = glfw.get_framebuffer_size(window)
            logical_width, _ = glfw.get_window_size(window)
            if not width or not height:
                glfw.wait_events_timeout(0.05)
                continue
            scale = width / max(1, logical_width)
            px = lambda value: int(value * scale)
            rect = lambda x, y, w, h: mujoco.MjrRect(px(x), px(y), px(w), px(h))
            logical_height = height / scale
            mujoco.mjr_rectangle(mujoco.MjrRect(0, 0, width, height), 0.07, 0.09, 0.12, 1)
            status = "Waiting for MuJoCo..." if latest is None else (
                f"{'PAUSED' if latest['paused'] else 'LIVE'}  |  Simulation {latest['time']:.2f} s"
                f"  |  Motor {latest['motor_speed']:.2f} m/s  |  Playback {latest['playback_speed']:g}x")
            if not state["connected"]:
                status = "MuJoCo viewer closed - last readings shown"
            text(rect(16, logical_height - 58, logical_width - 32, 48),
                 f"{title.upper()}  /  {xml_path.name}\n{status}")

            tab_width = (logical_width - 24) / len(tabs)
            for index, sensor in enumerate(tabs):
                label(rect(12 + index * tab_width, logical_height - 118, tab_width - 4, 50),
                      tab_labels[sensor], index == state["tab"])
            footer = 64
            body_top = logical_height - 132
            summary = rect(18, body_top - 94, logical_width - 36, 88)
            plot_top = px(body_top - 100)
            plot_bottom = px(footer)
            plot_height = max(1, plot_top - plot_bottom)
            plot_width = width - px(24)

            selected = tabs[state["tab"]]
            if selected == "controls":
                draw_guide(logical_width, logical_height, scale, context, latest,
                           state["entry"], state["editing"], state["message"], motor_speed=state["motor_speed"],
                           playback_controls=playback_controls)
            elif latest is not None:
                pair = lambda array: " / ".join(f"{value:+.3f}" for value in array)
                if selected == "imu":
                    imu = latest["imu"]
                    text(summary, "Acceleration X / Y / Z (m/s^2)\nAngular velocity X / Y / Z (rad/s)",
                         f"{pair(imu['acceleration_m_s2'])}\n{pair(imu['angular_velocity_rad_s'])}")
                    for row, figure in enumerate((gyro, acceleration)):
                        y0 = plot_bottom + plot_height * row // 2
                        y1 = plot_bottom + plot_height * (row + 1) // 2
                        mujoco.mjr_figure(mujoco.MjrRect(px(12), y0, plot_width, y1 - y0), figure, context)
                elif selected == "encoders":
                    enc = latest["encoders"]
                    text(summary, "Left / right angle (rad)\nLeft / right speed (rad/s)\nWheel rotation travel (m)",
                         f"{pair(enc['position_rad'])}\n{pair(enc['velocity_rad_s'])}\n{pair(enc['distance_m'])}")
                    for row, figure in enumerate((encoder_velocity, encoder_angle)):
                        y0 = plot_bottom + plot_height * row // 2
                        y1 = plot_bottom + plot_height * (row + 1) // 2
                        mujoco.mjr_figure(mujoco.MjrRect(px(12), y0, plot_width, y1 - y0), figure, context)
                elif selected == "ultrasonic":
                    ranges = latest["ultrasonic"]
                    formatted = [f"{value:.3f} m" if np.isfinite(value) else "no return" for value in ranges]
                    text(summary, "Left ultrasonic\nRight ultrasonic\nRange model", "\n".join(formatted) + "\nIdeal single ray; max 4 m")
                    mujoco.mjr_figure(mujoco.MjrRect(px(12), plot_bottom, plot_width, plot_height), ultrasonic, context)
                elif selected == "lidar":
                    scan = latest["lidar"]
                    valid = np.isfinite(scan["ranges_m"])
                    ranges = scan["ranges_m"][valid]
                    nearest = f"{ranges.min():.3f} m" if len(ranges) else "no return"
                    text(summary, "LiDAR scan\nValid returns\nNearest obstacle",
                         f"360 degrees / 360 rays / 10 Hz / max 5 m\n{valid.sum()} / 360\n{nearest}")
                    points = scan["points_xy_m"][valid]
                    ticks = np.empty((2 * len(points), 2))
                    ticks[0::2] = points - (0.009, 0)
                    ticks[1::2] = points + (0.009, 0)
                    lidar.linepnt[0] = len(ticks)
                    lidar.linedata[0, :ticks.size] = ticks.ravel()
                    finite_points = np.abs(points).max() if len(points) else 2.0
                    extent = max(3.0, float(finite_points) * 1.1)
                    lidar.range[:] = ((-extent, extent), (-extent, extent))
                    side = min(plot_width, plot_height)
                    mujoco.mjr_figure(mujoco.MjrRect((width - side) // 2, plot_bottom, side, side), lidar, context)
            else:
                text(summary, "Starting the separate native MuJoCo viewer...")

            label(rect(12, 10, 120, 44), "Resume" if latest and latest["paused"] else "Pause")
            label(rect(144, 10, 100, 44), "Reset")
            label(rect(256, 10, 100, 44), "Stop")
            label(rect(logical_width - 132, 10, 120, 44), f"Motor {state['motor_speed']:.2f}")
            if playback_controls:
                label(rect(logical_width - 272, 10, 128, 44), f"Playback {state['playback_speed']:g}x")
                text(rect(372, 10, logical_width - 660, 44), "[] replay\nSpace pause")
            else:
                hint = "W/S drive  Q/E turn" if control is not None else "Native actuator controls"
                text(rect(372, 10, logical_width - 516, 44),
                     f"{hint}\nSpace pause  R reset  +/- motor")
            glfw.swap_buffers(window)
            time.sleep(max(0.0, 1 / 30 - (time.perf_counter() - frame_start)))
    finally:
        send("close")
        connection.close()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        context.free()
        glfw.destroy_window(window)
        glfw.terminate()

