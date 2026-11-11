# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.move import move
from module.motion.keyboard import keyboard_control
from module import Robot, sensor
from module.viewer import view
from examples.world import SCENES

# model_lidar.xml 기반: lidar 센서가 실제로 장착된 XML입니다.
XML = SCENES / "pillar_lidar.xml"

with Robot(XML) as robot:
    scan = sensor.lidar.read(robot)
    print("type:", type(scan).__name__, "keys:", list(scan))
    for key, values in scan.items():
        print(key, "shape:", values.shape, "dtype:", values.dtype)
    for index in (0, 90, 180, 270):
        print("index:", index, "angle rad:", scan["angles_rad"][index],
              "range m:", scan["ranges_m"][index], "XY m:", scan["points_xy_m"][index])
view(XML, demo=False, sensors=("lidar",), motor_speed=.25, control=keyboard_control, drive_function=move)
