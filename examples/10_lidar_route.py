# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from module import sensor
from module.course import sector
from examples.runtime import arguments, Lab, sensor_route
from examples.world import SCENES

XML = SCENES / "pillar_lidar.xml"
STOP_DISTANCE = 0.55


def read_front(robot):
    scan = sensor.lidar.read(robot)
    return float(sector(scan, 0, 8))


def choose(front):
    if front > STOP_DISTANCE:
        return 0.25, 0.0
    return 0.0, 0.0


args = arguments("10: lidar 거리로 기둥 우회")
lab = Lab(xml_path=XML, show=not args.headless, move=move)
try:
    print(sensor_route(lab, choose, "lidar", read_front=read_front))
finally:
    lab.close()
