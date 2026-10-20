"""Movement independent of sensor readers and GUI.

    motion.forward(robot, 1)             # execute 1 m, blocking
    motion.backward(robot, 0.2)
    motion.rotate(robot, 90)             # +left, -right, degrees
    motion.forward(robot, 1, wait=False) # queue; your loop calls robot.step()
    motion.drive(robot, linear=0.1)      # velocity target, then robot.run_for()
    motion.stop(robot)
    motion.wheels.set_velocity(robot, left=5, right=5)  # rad/s, then step()
    motion.wheels.rotate(robot, left=6.283, right=6.283) # relative wheel radians

commands.forward(1) only builds a description for queues/GUI sequences.
motion.view("basic") opens MuJoCo and a Controls-only window; no sensors
are polled or plotted. W/S drive and Q/E turn while Controls has focus.
"""

from . import commands, motors, wheels
from .api import (
    MotionError, backward, drive, execute, forward, rotate, set_speed, status, stop,
    wait_until_done as wait,
)
from .keyboard import keyboard_control, view

__all__ = ["forward", "backward", "rotate", "execute", "wait", "drive", "stop",
           "status", "set_speed", "view", "commands", "motors", "wheels", "keyboard_control", "MotionError"]
