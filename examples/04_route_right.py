# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from examples.runtime import Lab
from examples.world import SCENES

XML = SCENES / "pillar_basic.xml"
# (선속도 m/s, 각속도 rad/s, 시간 s): 기둥의 오른쪽으로 우회합니다.
ACTIONS = [
    (0.25, 0.0, 1.0),
    (0.0, -1.0, 1.9),
    (0.25, 0.0, 3.5),
    (0.0, 1.0, 1.9),
    (0.25, 0.0, 6.0),
    (0.0, 1.0, 1.9),
    (0.25, 0.0, 3.5),
    (0.0, -1.0, 1.9),
    (0.25, 0.0, 1.5),
]

lab = Lab(xml_path=XML, show=True, move=move)
try:
    for linear, angular, seconds in ACTIONS:
        lab.run_for(linear, angular, seconds)
    lab.stop()
    print(lab.result())
finally:
    lab.close()
