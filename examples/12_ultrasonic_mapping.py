# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from examples.runtime import arguments, Lab, sensor_route, save_map
from examples.world import SCENES

XML = SCENES / "pillar_sonic.xml"


def choose(front):
    if front > 0.55:
        return 0.25, 0.0
    return 0.0, 0.0


args = arguments("12: ultrasonic 측정점으로 2D 지도 누적")
lab = Lab(xml_path=XML, show=not args.headless, move=move)
try:
    print(sensor_route(lab, choose, "ultrasonic"))
    save_map(lab, show=not args.headless, name="ultrasonic_map")
finally:
    lab.close()
