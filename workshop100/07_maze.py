# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module import course
from module.playback import ask_speed
from workshop100.runtime import arguments
from workshop100.maze_policy import Policy

if __name__ == "__main__":
    args = arguments("제공 데모: 작은 미로에서 센서 기반 탐색 실행")
    world = course.square_maze("all", size=3, seed=7)
    print("3 x 3 cells, 30 cm cells, seed=7; parameters are in maze_policy.py")
    if args.headless:
        print(course.run(world, Policy(), max_sim_time=180, trace_name="workshop100_maze"))
    else:
        course.view(world, policy="workshop100.maze_policy:Policy", max_sim_time=None,
                    motor_speed=.30, playback_speed=ask_speed(), playback_controls=True)
