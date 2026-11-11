# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from workshop100.runtime import arguments, load_move, Lab

# 실습: (선속도 m/s, 각속도 rad/s, 시간 s)를 순서대로 작성합니다.
# 처음 세 동작을 확인하고 나머지 경로를 이어서 완성하세요.
ACTIONS = [
    (0.25, 0.0, 1.0),   # 전진
    (0.0, 1.0, 1.9),    # 왼쪽 회전
    (0.25, 0.0, 3.5),   # 옆 통로로 이동
    (0.0, -1.0, 1.9),   # 오른쪽 회전
    (0.25, 0.0, 6.0),   # 기둥 옆을 지나기
    (0.0, -1.0, 1.9),   # 출발선 방향으로 회전
    (0.25, 0.0, 3.5),   # 원래 선으로 복귀
    (0.0, 1.0, 1.9),    # 목표 방향으로 회전
    (0.25, 0.0, 1.5),   # 목표로 이동
]

if __name__ == "__main__":
    args = arguments("03: 센서 없이 시간으로 기둥 뒤 목표까지 이동")
    move = load_move(args.answer)  # 01_move.py에서 작성한 함수
    actions = ACTIONS
    if args.answer:
        from workshop100.reference import ACTIONS as actions
    lab = Lab(args.map, show=not args.headless, move=move)
    try:
        for linear, angular, seconds in actions:
            lab.run_for(linear, angular, seconds)
        lab.stop()
        print(lab.result())
    finally:
        lab.close()
