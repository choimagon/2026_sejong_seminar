# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from workshop100.runtime import arguments, Lab, sensor_route, save_map
from workshop100.reference import move, choose

if __name__ == "__main__":
    args = arguments("제공 데모: 엔코더+IMU 위치 추정에 초음파/라이다 측정점을 누적")
    lab = Lab(args.map, show=not args.headless, move=move)
    try:
        print(sensor_route(lab, choose, args.sensor))
        save_map(lab, show=not args.headless)
    finally:
        lab.close()
