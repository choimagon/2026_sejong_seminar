# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from module.motion.keyboard import keyboard_control
from module import Robot, sensor
from module.viewer import view
from examples.world import SCENES

# model_sonic.xml 기반: ultrasonic 센서가 실제로 장착된 XML입니다.
XML = SCENES / "pillar_sonic.xml"

with Robot(XML) as robot:
    distance = sensor.ultrasonic.read(robot)
    print("type:", type(distance).__name__)
    print("front distance (m):", distance)

view(XML, demo=False, sensors=("ultrasonic",), motor_speed=.25, control=keyboard_control, drive_function=move)
