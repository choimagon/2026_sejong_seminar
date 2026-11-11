# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from module import Robot, sensor
from module.viewer import view
from examples.runtime import arguments
from examples.world import SCENES

# model_sonic.xml 기반: ultrasonic 센서가 실제로 장착된 XML입니다.
XML = SCENES / "pillar_sonic.xml"

args = arguments("07: ultrasonic 센서 읽기")
with Robot(XML) as robot:
    print("Ultrasonic [left, right] m:", sensor.ultrasonic.read(robot))
if not args.headless:
    view(XML, demo=False, sensors=("ultrasonic",), motor_speed=.25, drive_function=move)
