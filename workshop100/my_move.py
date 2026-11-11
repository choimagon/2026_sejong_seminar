"""실습 1: TODO 두 줄만 바꿉니다. 나머지 코드는 제공합니다."""
from module.motion.wheels import set_velocity


def move(robot, linear=0.0, angular=0.0):
    radius = float(robot.model.geom("drive_left_tire").size[0])
    track = float(robot.model.body("left_wheel").pos[1]
                  - robot.model.body("right_wheel").pos[1])
    # TODO: 왼쪽 = (linear - angular * track / 2) / radius
    left = 0.0
    # TODO: 오른쪽 = (linear + angular * track / 2) / radius
    right = 0.0
    set_velocity(robot, left, right)
