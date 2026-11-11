"""Instructor answers; demos use these without replacing student files."""
from module.motion.wheels import set_velocity


def move(robot, linear=0.0, angular=0.0):
    radius = float(robot.model.geom("drive_left_tire").size[0])
    track = float(robot.model.body("left_wheel").pos[1] - robot.model.body("right_wheel").pos[1])
    left = (linear - angular * track / 2) / radius
    right = (linear + angular * track / 2) / radius
    set_velocity(robot, left, right)


def choose(front):
    return (0.25, 0.0) if front > 0.55 else (0.0, 0.0)


# Timed motion is only an initial guess. Students observe and tune it.
ACTIONS = [(0.25, 0, 1.0), (0, 1.0, 1.9), (0.25, 0, 3.5),
           (0, -1.0, 1.9), (0.25, 0, 6.0), (0, -1.0, 1.9),
           (0.25, 0, 3.5), (0, 1.0, 1.9), (0.25, 0, 1.5)]
