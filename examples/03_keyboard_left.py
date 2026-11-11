# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from module.motion.keyboard import keyboard_control
from module.viewer import view
from examples.runtime import arguments
from examples.world import SCENES

# model_basic.xml 기반: 거리 센서 없는 맵에서 직접 운전합니다.
XML = SCENES / "left_corner_basic.xml"

args = arguments("03: left corner 맵에서 W/S/Q/E 운전")
if args.headless:
    raise SystemExit("Keyboard practice needs a desktop; omit --headless")
view(XML, demo=False, sensors=(), motor_speed=.25, control=keyboard_control, drive_function=move)
