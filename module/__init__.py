"""Educational MuJoCo library: Robot, independent sensors, and motor motion.

    from module import Robot, motion, sensor

    with Robot("all") as robot:       # No window, no background process.
        motion.forward(robot, 0.3)    # Runs physics until complete.
        print(sensor.imu.read(robot))

Windows are explicit: robot.view(), motion.view("basic") or sensor.view("all").
"""

from .robot import Robot
from . import motion, move, sensor

__all__ = ["Robot", "move", "motion", "sensor"]
