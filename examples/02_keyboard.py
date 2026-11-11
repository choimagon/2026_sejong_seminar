# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from module.viewer import view
from examples.world import SCENES

# model_basic.xml 기반: 거리 센서 없는 맵에서 직접 운전합니다.
XML = SCENES / "obstacle_basic.xml"

# 따옴표 속 키를 바꾸면 조작 키가 바뀝니다. 예: w→i, s→k, q→j, e→l
# 0.35는 전후진 속도(m/s), 2.0은 회전 속도(rad/s)입니다.
def keyboard_control(pressed):
    linear = 0.0
    angular = 0.0
    if pressed("w"):
        linear += 0.35
    if pressed("s"):
        linear -= 0.35
    if pressed("q"):
        angular += 2.0
    if pressed("e"):
        angular -= 2.0
    return linear, angular


# 키로 운전하기 전 Motion Controls 창의 Controls 탭을 먼저 클릭하세요.
# MuJoCo 3D 창이 선택되어 있으면 MuJoCo 단축키가 작동합니다.
view(XML, demo=False, sensors=(), motor_speed=.25, control=keyboard_control, drive_function=move)
