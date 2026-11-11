# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from module import sensor
from module.course import sector
from examples.runtime import Lab, sensor_route
from examples.world import SCENES

XML = SCENES / "pillar_sonic.xml"
STOP_DISTANCE = 0.55


def read_front(robot):
    return float(min(sensor.ultrasonic.read(robot)))


def choose(front):
    if front > STOP_DISTANCE:
        return 0.25, 0.0
    return 0.0, 0.0


lab = Lab(xml_path=XML, show=True, move=move)
try:
    print(sensor_route(lab, choose, "ultrasonic", read_front=read_front))
finally:
    lab.close()
