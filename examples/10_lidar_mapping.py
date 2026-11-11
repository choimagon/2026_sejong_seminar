# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from examples.runtime import Lab, sensor_route, save_map
from examples.world import SCENES

XML = SCENES / "pillar_lidar.xml"


def choose(front):
    if front > 0.55:
        return 0.25, 0.0
    return 0.0, 0.0


lab = Lab(xml_path=XML, show=True, move=move)
try:
    print(sensor_route(lab, choose, "lidar"))
    save_map(lab, show=True, name="lidar_map")
finally:
    lab.close()
