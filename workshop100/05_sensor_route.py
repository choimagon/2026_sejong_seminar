# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from workshop100.runtime import arguments, load_move, Lab, sensor_route

STOP_DISTANCE = 0.55


def choose(front):
    # 실습: 전방 거리로 전진/정지를 결정합니다.
    if front > STOP_DISTANCE:
        return 0.25, 0.0
    return 0.0, 0.0


if __name__ == "__main__":
    args = arguments("05: 거리 조건으로 전진/정지 판단 후 기둥 우회")
    move = load_move(args.answer)  # 01_move.py에서 작성한 함수
    decision = choose
    if args.answer:
        from workshop100.reference import choose as decision
    lab = Lab(args.map, show=not args.headless, move=move)
    try:
        # 회전·이동량 추정·우회 단계 실행기는 제공합니다.
        print(sensor_route(lab, decision, args.sensor))
    finally:
        lab.close()
