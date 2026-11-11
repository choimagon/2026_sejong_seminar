# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from workshop100.runtime import arguments, selected, Lab

if __name__ == "__main__":
    args = arguments("my_route.py의 ACTIONS를 작성해 센서 없이 기둥 뒤 목표로 이동")
    move, actions, _ = selected(args.answer)
    lab = Lab(args.map, show=not args.headless, move=move)
    try:
        for linear, angular, seconds in actions:
            lab.run_for(linear, angular, seconds)
        lab.stop()
        print(lab.result())
    finally:
        lab.close()
