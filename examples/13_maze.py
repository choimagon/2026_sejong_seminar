# 파일 경로로 실행할 때도 프로젝트 라이브러리를 찾습니다.
if __package__ in (None, ""):
    import _bootstrap

from module import course
from module.playback import ask_speed
from examples.runtime import arguments
from examples.maze_policy import Policy

if __name__ == "__main__":
    args = arguments("13: 라이다 모델로 작은 미로 탐색")
    world = course.square_maze("lidar", size=3, seed=7)
    print("3 x 3 cells, 30 cm cells, seed=7; parameters are in maze_policy.py")
    if args.headless:
        print(course.run(world, Policy(), max_sim_time=180, trace_name="examples_maze"))
    else:
        course.view(world, policy="examples.maze_policy:Policy", max_sim_time=None,
                    motor_speed=.30, playback_speed=ask_speed(), playback_controls=True)
