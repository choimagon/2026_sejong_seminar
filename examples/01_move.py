# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.motion.wheels import set_velocity
from examples.runtime import arguments, Lab
from examples.world import SCENES

XML = SCENES / "pillar_basic.xml"


def move(robot, linear=0.0, angular=0.0):
    radius = float(robot.model.geom("drive_left_tire").size[0])
    track = float(robot.model.body("left_wheel").pos[1]
                  - robot.model.body("right_wheel").pos[1])
    # 실습: 바퀴 동작 그림을 보고 이 두 계산식을 작성합니다.
    left = (linear - angular * track / 2) / radius
    right = (linear + angular * track / 2) / radius
    set_velocity(robot, left, right)


args = arguments("01: move 함수 작성 → 전진·정지·회전 확인")
lab = Lab(xml_path=XML, show=not args.headless, move=move)
try:
    lab.run_for(.2, 0, 2)
    lab.run_for(0, 0, .5)
    lab.run_for(0, 1, 1.5)
    lab.run_for(.2, 0, 2)
    lab.stop()
    print(lab.result())
finally:
    lab.close()
