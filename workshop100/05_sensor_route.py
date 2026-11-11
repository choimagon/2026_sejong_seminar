# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from workshop100.runtime import arguments, selected, Lab, sensor_route

if __name__ == "__main__":
    args = arguments("my_sensor.py의 choose를 작성해 센서로 전진/정지 판단")
    move, _, choose = selected(args.answer)
    lab = Lab(args.map, show=not args.headless, move=move)
    try:
        print(sensor_route(lab, choose, args.sensor))
    finally:
        lab.close()
