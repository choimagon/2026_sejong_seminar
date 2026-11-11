# 번호별 로봇 실습

프로젝트 루트에서 `seminar_mujoco` 환경을 켠 뒤 실행합니다.
Windows/Linux는 모두 `python`입니다. Mac은 01·03·04·07~10은 `mjpython`, 02·05·06·11은 `python`입니다. 아래 표의 명령을 그대로 실행하세요.
준비 단계의 `show.py`만 Mac에서도 `python show.py`로 실행합니다.

| 번호 파일 | 내용 | XML | Windows/Linux | Mac |
| --- | --- | --- | --- | --- |
| [01_move.py](01_move.py) | move 함수와 전진·후진·회전·정지 | `pillar_basic.xml` | `python examples/01_move.py` | `mjpython examples/01_move.py` |
| [02_keyboard.py](02_keyboard.py) | 중앙 기둥 통로 운전·조작 키 직접 변경 | `obstacle_basic.xml` | `python examples/02_keyboard.py` | `python examples/02_keyboard.py` |
| [03_route_left.py](03_route_left.py) | 시간으로 넓은 방 기둥 왼쪽 우회 | `pillar_basic.xml` | `python examples/03_route_left.py` | `mjpython examples/03_route_left.py` |
| [04_route_right.py](04_route_right.py) | 시간으로 넓은 방 기둥 오른쪽 우회 | `pillar_basic.xml` | `python examples/04_route_right.py` | `mjpython examples/04_route_right.py` |
| [05_ultrasonic.py](05_ultrasonic.py) | 초음파 배열 출력과 GUI 관찰 | `pillar_sonic.xml` | `python examples/05_ultrasonic.py` | `python examples/05_ultrasonic.py` |
| [06_lidar.py](06_lidar.py) | 라이다 딕셔너리·거리/좌표 배열과 GUI 관찰 | `pillar_lidar.xml` | `python examples/06_lidar.py` | `python examples/06_lidar.py` |
| [07_ultrasonic_route.py](07_ultrasonic_route.py) | 초음파 거리로 판단하며 우회 | `pillar_sonic.xml` | `python examples/07_ultrasonic_route.py` | `mjpython examples/07_ultrasonic_route.py` |
| [08_lidar_route.py](08_lidar_route.py) | 라이다 거리로 판단하며 우회 | `pillar_lidar.xml` | `python examples/08_lidar_route.py` | `mjpython examples/08_lidar_route.py` |
| [09_ultrasonic_mapping.py](09_ultrasonic_mapping.py) | 초음파 측정점 누적 지도 | `pillar_sonic.xml` | `python examples/09_ultrasonic_mapping.py` | `mjpython examples/09_ultrasonic_mapping.py` |
| [10_lidar_mapping.py](10_lidar_mapping.py) | 라이다 측정점 누적 지도 | `pillar_lidar.xml` | `python examples/10_lidar_mapping.py` | `mjpython examples/10_lidar_mapping.py` |
| [11_maze.py](11_maze.py) | 라이다로 작은 미로 탐색 | `라이다 모델로 생성한 미로 XML` | `python examples/11_maze.py` | `python examples/11_maze.py` |

## 직접 작성할 부분

1. `01_move.py`: 바퀴 움직임을 이해하고 `left`, `right` 계산식을 작성합니다.
2. `02_keyboard.py`: `pressed("w")`의 키 문자를 바꿔 조작 키를 연결합니다.
3. `03_route_left.py`: 전진·회전·시간을 조합합니다. `04_route_right.py`에서 반대쪽 경로를 비교합니다.
4. `07_ultrasonic_route.py`: `read_front()`로 실제 센서값을 읽고 `choose(front)` 조건문으로 전진·정지를 선택합니다.
5. `08_lidar_route.py`에서는 XML과 읽기 함수가 어떻게 달라졌는지 확인합니다.

전체 코드가 파일에 들어 있습니다. PPT의 줄 번호를 따라 작성하거나 해당 부분을 바꾸고 저장한 뒤 다시 실행합니다.
01번은 move 함수를 만드는 연습입니다. 뒤 실습은 기존 공용 구현을 `from module.move import move`로 가져와 사용합니다.
번호 파일은 직접 실행하는 전용 파일이며 다른 번호 파일을 import하지 않습니다.
`runtime.py`, `world.py`, `maze_policy.py`는 제공 코드입니다. 복잡한 물리·GUI·위치 추정·탐색기를 전부 새로 작성하지 않습니다.

## 맵과 XML

02번 운전에는 `obstacle_basic.xml` 하나만 사용합니다. 직선·코너 XML은 추가 참고 자산입니다.

- `straight_basic.xml`: 직선 통로.
- `left_corner_basic.xml`: +X로 약 2.8m 직진한 다음 왼쪽 통로로 진행.
- `right_corner_basic.xml`: +X로 약 2.8m 직진한 다음 오른쪽 통로로 진행.
- `pillar_basic.xml`: 넓은 방의 기둥 우회, 거리 센서 없음.
- `pillar_sonic.xml`: 같은 방·기둥, 초음파 장착.
- `pillar_lidar.xml`: 같은 방·기둥, 라이다 장착.

센서는 실제 XML 모델에 장착되어야 읽을 수 있습니다. 초음파 모델에는 라이다가 없고 라이다 모델에는 초음파가 없습니다.
원본 모델은 `model_xml/model_basic.xml`, `model_sonic.xml`, `model_lidar.xml`이고, 준비된 맵 XML에는 로봇과 벽·기둥이 함께 들어 있습니다.
`world.py`는 강사용 XML 생성기이며 학생은 준비된 XML을 그대로 불러옵니다.

## 직접 운전

Motion Controls / Sensor Monitor의 **Controls 탭을 먼저 클릭**하고 W/S/Q/E를 누릅니다.
기본값은 W/S 전진·후진, Q/E 좌·우 회전입니다. 키를 놓거나 다른 창을 클릭하면 정지합니다.
카메라 조작 뒤에는 GUI를 다시 클릭하세요.

## 센서와 지도

초음파는 전방 두 거리값(m), 라이다는 360방향 거리값(m)을 읽으며 반사가 없는 방향은 `inf`입니다.
초음파는 이 모델에서 이상적인 단일 광선으로 구현되며 실제 음파 확산·잡음은 재현하지 않습니다.
07·08번은 전진/정지를 센서로 판단하고 우회 단계·엔코더/IMU 이동량 추정은 제공합니다.
고정된 방의 우회이며 모든 장애물 배치에서 성공하는 범용 회피는 아닙니다.
09번은 초음파 측정점만, 10번은 라이다 측정점만 엔코더+IMU 추정 좌표에 누적합니다.
주행 뒤 실제 결과 그래프가 열리고 `outputs/examples/ultrasonic_map.png`, `lidar_map.png`와 `.npz`를 저장합니다.
정답 좌표를 쓰지 않으며 누적 오차가 있습니다. SLAM·루프 폐쇄는 구현하지 않습니다.
11번은 라이다 모델로 3×3셀·seed7 미로를 탐색합니다. 시작 배속을 입력하고 실행 중 [ / ]로 조절합니다.
GUI 미로에는 주행 제한시간이 없습니다.

## 실행과 검증

번호 파일에는 `args`, `--headless` 같은 옵션이 없습니다. 저장 후 표의 명령어로 바로 실행합니다.
강사 검증은 `python -m unittest discover -s tests -v`로 실행합니다.
이전 버전은 로컬 백업에 보존했습니다.

## W/S/Q/E 입력을 move에 연결하기

02번 파일에 `keyboard_control(pressed)` 함수를 직접 보여줍니다.
`pressed("w")`처럼 현재 눌린 키를 확인하고, `(linear, angular)`를 반환합니다.

| 키 | 입력 함수의 반환값 | 동작 |
| --- | --- | --- |
| W | `(0.35, 0)` | 전진 |
| S | `(-0.35, 0)` | 후진 |
| Q | `(0, 2.0)` | 좌회전 |
| E | `(0, -2.0)` | 우회전 |
| 모두 놓기 | `(0, 0)` | 정지 |

W+Q처럼 동시에 누르면 선속도와 각속도를 함께 주어 곡선으로 움직입니다.
코드의 0.35(m/s)와 2.0(rad/s)은 기본 입력 속도이며, 실행기가 GUI의 Motor 설정에 맞춰 속도를 조절합니다.

```python
view(XML, demo=False, sensors=(), motor_speed=.25,
     control=keyboard_control, drive_function=move)
```

`control`은 키 상태를 속도 두 개로 바꾸는 함수이고, `drive_function`은 기존 `module.move.move`입니다.
GUI가 `control(pressed)`를 호출 → 속도를 전달 → 시뮬레이터가 `move(robot, linear, angular)`를 실행합니다.
운전 실습은 02번의 중앙 기둥 통로 하나로 진행합니다.
Controls 탭을 클릭해야 입력되며, 다른 창으로 포커스를 옮기거나 명령을 입력하는 동안에는 정지합니다.

### 조작 키 바꾸기

02번에서 `pressed("w")`는 W 키가 눌렸는지 확인합니다. 따옴표 속 한 글자를 바꾸면 됩니다.

```python
if pressed("i"):      # W 대신 I로 전진
    linear += 0.35
```

같은 방법으로 `s`→`k`, `q`→`j`, `e`→`l`로 바꾸면 I/K/J/L로 운전합니다.
저장하고 창을 닫은 뒤 02번을 다시 실행하세요. 영문 한 글자 키를 사용합니다.
`control=keyboard_control`이 이 함수를 GUI에 연결하고, 반환된 두 속도가 `move`로 전달됩니다.
GUI에 표시된 W/S/Q/E 안내는 기본 키 기준이며, 실제 입력은 수정한 함수에 따릅니다.

## 센서 출력 형태

초음파 `sensor.ultrasonic.read(robot)`는 NumPy 배열입니다.

```python
# 실제 값은 맵과 자세에 따라 달라집니다.
distances.shape       # (2,)
distances[0]          # 전방 왼쪽 센서 거리(m)
distances[1]          # 전방 오른쪽 센서 거리(m)
```

`shape (2,)`는 원소 2개인 1차원 배열입니다. `(2, 1)` 행렬과 구분합니다.
두 초음파 센서는 모두 전방을 봅니다. 왼쪽·오른쪽이라는 이름이 옆 통로를 향한다는 뜻은 아닙니다.
기본 최대 범위는 4m이며 반사가 없으면 `inf`입니다.

라이다 `sensor.lidar.read(robot)`는 다음 배열을 가진 딕셔너리입니다.

| 키 | 기본 shape | 의미 |
| --- | --- | --- |
| `angles_rad` | `(360,)` | 센서 기준 광선 각도(rad) |
| `ranges_m` | `(360,)` | 각 광선의 거리(m), 미반사는 `inf` |
| `points_xy_m` | `(360, 2)` | 센서 기준 측정점 `[x, y]`(m), 미반사는 `[NaN, NaN]` |
| `origin_world_m` | `(3,)` | 센서의 실제 시뮬레이터 원점 위치, 부가 검증 정보 |
| `directions_world` | `(360, 3)` | 세계 좌표의 광선 단위 방향벡터, 부가 검증 정보 |
| `geom_ids` | `(360,)` | 부딪힌 MuJoCo 물체 번호, 미반사는 `-1` |

기본 360개 광선에서 인덱스 0은 전방, 90은 왼쪽, 180은 뒤, 270은 오른쪽입니다.
각도 배열의 단위는 도가 아니라 rad이며 최대 범위 기본값은 5m입니다.
`points_xy_m[i] = ranges_m[i] * [cos(angles_rad[i]), sin(angles_rad[i])]`로 같은 광선을 연결할 수 있습니다.
로컬 X는 전방, Y는 왼쪽입니다. NumPy 배열의 행 인덱스와 공간의 좌우 방향을 구분하세요.
수업 제어·지도 누적에는 주로 앞의 세 배열을 쓰고, 실제 세계 위치·물체 번호를 정답 지도처럼 사용하지 않습니다.
05·06 실행 파일이 type·shape·dtype와 대표 인덱스를 출력하며 PPT는 실제 출력과 센서 화면을 도해로 연결합니다.

센서가 XML에 없으면 읽기 오류가 나고, 센서는 있지만 반사가 없으면 `inf`가 반환됩니다. 두 경우를 구분하세요.
