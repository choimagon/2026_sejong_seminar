# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from workshop100.runtime import arguments, selected, Lab

if __name__ == "__main__":
    args = arguments("my_move.py의 두 줄을 작성하고 기본 동작 확인")
    move, _, _ = selected(args.answer)
    lab = Lab(args.map, show=not args.headless, move=move)
    try:
        lab.run_for(.2, 0, 2)
        lab.run_for(0, 0, .5)
        lab.run_for(0, 1, 1.5)
        lab.run_for(.2, 0, 2)
        lab.stop()
        print(lab.result())
    finally:
        lab.close()
