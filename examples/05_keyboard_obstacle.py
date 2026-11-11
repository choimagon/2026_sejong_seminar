# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from module.motion.keyboard import keyboard_control
from module.viewer import view
from examples.runtime import arguments
from examples.world import SCENES

# 출발점과 도착점 사이 가운데 기둥을 좌우로 우회합니다.
XML = SCENES / "obstacle_basic.xml"

args = arguments("05: 가운데 기둥을 피해 도착점까지 W/S/Q/E 운전")
if args.headless:
    raise SystemExit("Keyboard practice needs a desktop; omit --headless")
view(XML, demo=False, sensors=(), motor_speed=.25, control=keyboard_control, drive_function=move)
