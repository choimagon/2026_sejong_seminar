# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from math import cos, sin, isfinite
from module.move import move
from module.viewer import view
from examples.world import SCENES

XML = SCENES / "pillar_sonic.xml"


# x, y, yaw는 엔코더·IMU로 추정한 센서 위치와 방향(rad)입니다.
def add_points(distance, x, y, yaw, points):
    if isfinite(distance):
        point_x = x + distance * cos(yaw)
        point_y = y + distance * sin(yaw)
        points.append((point_x, point_y))


# Controls 탭을 클릭하고 WSQE로 운전합니다. M: 지도, P: 저장, R: 초기화.
view(XML, demo=False, sensors=("ultrasonic",), motor_speed=.25,
     drive_function=move, mapping=add_points)
