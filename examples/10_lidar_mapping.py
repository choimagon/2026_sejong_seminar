# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from math import cos, sin, isfinite
from module.move import move
from module.viewer import view
from examples.world import SCENES

XML = SCENES / "pillar_lidar.xml"


# 각 광선의 상대 각도에 로봇의 추정 방향 yaw를 더합니다.
def add_points(scan, x, y, yaw, points):
    for angle, distance in zip(scan["angles_rad"], scan["ranges_m"]):
        if isfinite(distance):
            direction = yaw + angle
            point_x = x + distance * cos(direction)
            point_y = y + distance * sin(direction)
            points.append((point_x, point_y))


# Controls 탭을 클릭하고 WSQE로 운전합니다. M: 지도, P: 저장, R: 초기화.
view(XML, demo=False, sensors=("lidar",), motor_speed=.25,
     drive_function=move, mapping=add_points)
