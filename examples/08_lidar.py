# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module import Robot, sensor
from module.viewer import view
from examples.runtime import arguments
from examples.world import SCENES

# model_lidar.xml 기반: lidar 센서가 실제로 장착된 XML입니다.
XML = SCENES / "pillar_lidar.xml"

if __name__ == "__main__":
    args = arguments("08: lidar 센서 읽기")
    with Robot(XML) as robot:
        scan = sensor.lidar.read(robot)
        print("LiDAR rays:", len(scan["ranges_m"]), "| front m:", scan["ranges_m"][0])
    if not args.headless:
        target = "examples.reference:move" if args.answer else "examples.01_move:move"
        view(XML, demo=False, sensors=("lidar",), motor_speed=.25, drive_function=target)
