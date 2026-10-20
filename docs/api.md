# 라이브러리 안내

`module/`은 구현된 공용 라이브러리이며 학생은 `examples/`의 본문을 작성합니다.
아래는 사용할 함수와 반환값을 찾기 위한 안내입니다.

## 모델과 시간

`from module import Robot`으로 가져옵니다.

| 호출 | 의미 |
| --- | --- |
| `Robot("all")` | 로봇과 물리 상태 생성. 자동으로 창을 열지 않음 |
| `robot.view()` | 같은 로봇의 MuJoCo 창 열기 |
| `robot.time` | 현재 시뮬레이션 시각(초) |
| `robot.step()` | 물리 한 스텝 진행 |
| `robot.run_for(seconds)` | 지정한 시뮬레이션 초만큼 진행 |
| `robot.reset()` | 시작 상태로 초기화 |
| `robot.close()` | 로봇과 연결된 창 정리 |

`with Robot(...) as robot:`으로 사용하면 블록이 끝날 때 자동으로 닫힙니다.
`robot.view()`로 창을 연 상태의 `step`·`run_for`는 실시간으로 표시합니다.
창을 열지 않으면 실시간 대기 없이 물리를 계산합니다.

## 선속도·각속도

`from module.move import move`로 가져옵니다.

| 호출·인자 | 의미 |
| --- | --- |
| `move(robot, linear=..., angular=...)` | 선속도·각속도 목표를 함께 설정 |
| `linear` | m/s. 양수 전진, 음수 후진 |
| `angular` | rad/s. 양수 좌회전, 음수 우회전 |
| 두 값을 함께 지정 | 곡선 주행 |
| 두 값 모두 0 | 정지 목표 |

명령 뒤에 `step`·`run_for`로 물리를 진행해야 실제로 움직이고 제동합니다.
목표 속도는 바퀴의 구동으로 적용되며 실제 움직임은 가속도·토크·접촉 조건의 영향을 받습니다.

## 센서별 측정

`from module import sensor`로 가져옵니다.
`read`는 현재 시점의 값을 읽으며 물리 시간을 진행하지 않습니다.

| 호출 | 주요 반환값 | 단위·배열 순서 |
| --- | --- | --- |
| `sensor.available(robot)` | 장착된 센서 그룹 이름 | 모델에 있는 센서만 반환 |
| `sensor.imu.read(robot)` | `acceleration_m_s2`, `angular_velocity_rad_s` | 각각 `[X, Y, Z]`, m/s²·rad/s |
| `sensor.encoders.read(robot)` | `position_rad`, `velocity_rad_s`, `distance_m` | 각각 `[왼쪽, 오른쪽]`, rad·rad/s·m |
| `sensor.ultrasonic.read(robot)` | 거리 배열 | `[왼쪽, 오른쪽]`, m |
| `sensor.lidar.read(robot)` | `angles_rad`, `ranges_m`, `points_xy_m` | 각도 rad, 거리·스캔 좌표 m |
| `sensor.read(robot)` | 장착 센서들의 측정값과 `time` | 한 시점의 묶음 |

라이다 기준은 X축 전방·Y축 왼쪽이며 각도는 반시계 방향으로 증가합니다.
측정 범위 안에 반환이 없으면 거리는 `inf`, 라이다의 해당 좌표는 `NaN`입니다.
모델에 없는 센서를 읽으면 `MissingSensorError`가 발생합니다.

엔코더의 `distance_m`은 바퀴 각도×반지름이며 차체의 실제 이동거리와 다를 수 있습니다.
초음파는 XML의 이상적인 단일 광선 거리 모델을 사용합니다.
정지 상태의 IMU 가속도 Z에는 약 +9.81m/s²가 나타납니다.

## GUI

| 호출 | 표시 |
| --- | --- |
| `sensor.view("all")` | MuJoCo와 Controls·장착 센서 탭 |
| `sensor.imu.view("basic")` | Controls·IMU 탭 |
| `sensor.encoders.view("basic")` | Controls·엔코더 탭 |
| `sensor.ultrasonic.view("sonic")` | Controls·초음파 탭 |
| `sensor.lidar.view("lidar")` | Controls·라이다 탭 |
| `motion.view("basic")` | MuJoCo와 Controls만 표시 |

`motion`은 `from module import motion`으로 가져옵니다.
이 GUI 호출들은 새 시뮬레이션을 엽니다. 기존 `Robot`을 직접 읽을 때는 센서의 `read(robot)`를 사용합니다.
`demo=False`는 추가 센서 시험 장애물을 사용하지 않는 옵션입니다.
`motor_speed`는 실제 주행 속도 설정(m/s), `playback_speed`는 시뮬레이션 재생 배속입니다.

## 코스와 랜덤 미로

`from module import course`로 가져옵니다.

| 호출 | 의미 |
| --- | --- |
| `course.scenario(case, kind)` | 준비된 코스 XML 읽기 |
| `course.square_maze(kind, size=10, seed=None)` | 30cm 셀의 새 정사각형 미로 생성 |
| `course.view(world, ...)` | 코스·미로 GUI 열기 |
| `course.practice(case, kind, policy, ...)` | 준비된 코스에서 작성한 정책 실행 |
| `course.run(world, policy, ...)` | 창 없이 작성한 정책 실행·기록 |
| `course.sector(scan, degrees, half_width)` | 라이다의 지정한 방향·범위 거리(m) |

`case`는 `straight`·`corner`·`junction`·`cross`, `kind`는 `basic`·`lidar`·`sonic`·`all`입니다.
`world.path`로 XML 경로를 얻습니다.
`policy`는 작성한 정책 객체 또는 `examples.08_lidar_straight:Policy` 형식의 import 경로입니다.
`course.view`의 `policy`에는 import 경로를 사용합니다.

정책은 `decide(observation)`에서 아래 행동 중 하나를 반환하거나,
`velocity(observation)`에서 `(linear, angular)`를 반환하도록 작성할 수 있습니다.
`observation`의 `lidar`·`ultrasonic`·`estimate`·`time_s` 등에서 현재 관측을 확인합니다.
엔코더·IMU 기반 `estimate`는 주행 판단에 사용할 수 있으며 GUI 탭에는 표시하지 않습니다.

| 행동 생성 함수 | 의미 |
| --- | --- |
| `course.forward(metres)` | 전진 거리(m) |
| `course.backward(metres)` | 후진 거리(m) |
| `course.left(degrees)` | 제자리 좌회전(도) |
| `course.right(degrees)` | 제자리 우회전(도) |
| `course.arc(radius=..., degrees=...)` | 곡선 이동. 반지름 m, 양수 좌회전·음수 우회전 |
| `course.stop()` | 정지 |

`course` 행동 함수는 실행기가 받을 행동을 만듭니다.
기존 `robot`에 속도 목표를 직접 줄 때는 `move`를 사용합니다.
미로에서 시간 제한을 끄려면 `max_sim_time=None`을 명시합니다.
배속 입력 함수는 `from module.playback import ask_speed`로 가져옵니다.

## 바퀴별 제어와 거리 명령

실습 외에 바퀴별 실험을 할 때 사용할 수 있습니다.

| 호출 | 의미 |
| --- | --- |
| `motion.wheels.set_velocity(robot, left, right)` | 좌우 바퀴 목표 각속도(rad/s), 이후 물리 진행 필요 |
| `motion.wheels.rotate(robot, left, right)` | 좌우 바퀴 상대 회전각(rad) |
| `motion.forward(robot, metres)` | 기존 Robot을 지정 거리만큼 전진 |
| `motion.backward(robot, metres)` | 기존 Robot을 지정 거리만큼 후진 |
| `motion.rotate(robot, degrees)` | 기존 Robot을 지정 각도만큼 회전, 양수 왼쪽 |

`motion`의 거리·회전 명령은 기본적으로 완료까지 물리를 진행합니다.
코스 실습의 엔코더·IMU 추정 기반 행동과는 제어 방식이 다르므로 해당 실습에서는 `course` 실행기를 사용합니다.
