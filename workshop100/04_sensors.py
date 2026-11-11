# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module import Robot, sensor
from module.viewer import view
from workshop100.runtime import arguments
from workshop100.world import world

if __name__ == "__main__":
    args = arguments("초음파 거리값과 360도 라이다를 같은 기둥 맵에서 비교")
    path = world(args.map)
    with Robot(path) as robot:
        print("Ultrasonic [left, right] m:", sensor.ultrasonic.read(robot))
        scan = sensor.lidar.read(robot)
        print("LiDAR rays:", len(scan["ranges_m"]), "| front m:", scan["ranges_m"][0])
    if not args.headless:
        target = "workshop100.reference:move" if args.answer else "workshop100.my_move:move"
        view(path, demo=False, sensors=("ultrasonic", "lidar"), motor_speed=.25, drive_function=target)
