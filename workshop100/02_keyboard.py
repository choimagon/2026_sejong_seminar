# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module.viewer import view
from workshop100.runtime import arguments
from workshop100.world import world

if __name__ == "__main__":
    args = arguments("GUI의 Controls 탭을 클릭하고 W/S/Q/E로 운전")
    if args.headless:
        raise SystemExit("Keyboard practice needs a desktop; omit --headless")
    target = "workshop100.reference:move" if args.answer else "workshop100.01_move:move"
    print("MAP:", args.map, "| GUI Controls 클릭 → W/S/Q/E | 키 놓으면 정지")
    view(world(args.map), demo=False, sensors=(), motor_speed=.25, drive_function=target)
