# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from importlib import import_module
from examples.runtime import arguments, load_move, Lab, sensor_route, save_map
from examples.world import SCENES

XML = SCENES / "pillar_lidar.xml"
policy = import_module("examples.10_lidar_route")

if __name__ == "__main__":
    args = arguments("12: lidar 측정점으로 2D 지도 누적")
    lab = Lab(xml_path=XML, show=not args.headless, move=load_move(args.answer))
    try:
        print(sensor_route(lab, policy.choose, "lidar", read_front=policy.read_front))
        save_map(lab, show=not args.headless, name="lidar_map")
    finally:
        lab.close()
