# 번호별 로봇 실습

프로젝트 루트에서 `seminar_mujoco` 환경을 켠 뒤 실행합니다.
Windows/Linux는 `python examples/번호_이름.py`, Mac은 `mjpython examples/번호_이름.py`입니다.
준비 단계의 `show.py`만 Mac에서도 `python show.py`로 실행합니다.

| 번호 파일 | 내용 | XML | Windows/Linux | Mac |
| --- | --- | --- | --- | --- |
| [01_move.py](01_move.py) | move 함수와 전진·후진·회전·정지 | `pillar_basic.xml` | `python examples/01_move.py` | `mjpython examples/01_move.py` |
| [02_keyboard_straight.py](02_keyboard_straight.py) | 직선 통로에서 W/S/Q/E 운전 | `straight_basic.xml` | `python examples/02_keyboard_straight.py` | `mjpython examples/02_keyboard_straight.py` |
| [03_keyboard_left.py](03_keyboard_left.py) | 직진 후 왼쪽으로 꺾이는 통로 | `left_corner_basic.xml` | `python examples/03_keyboard_left.py` | `mjpython examples/03_keyboard_left.py` |
| [04_keyboard_right.py](04_keyboard_right.py) | 직진 후 오른쪽으로 꺾이는 통로 | `right_corner_basic.xml` | `python examples/04_keyboard_right.py` | `mjpython examples/04_keyboard_right.py` |
| [05_route_left.py](05_route_left.py) | 시간으로 기둥 왼쪽 우회 | `pillar_basic.xml` | `python examples/05_route_left.py` | `mjpython examples/05_route_left.py` |
| [06_route_right.py](06_route_right.py) | 시간으로 기둥 오른쪽 우회 | `pillar_basic.xml` | `python examples/06_route_right.py` | `mjpython examples/06_route_right.py` |
| [07_ultrasonic.py](07_ultrasonic.py) | 초음파 값과 GUI 관찰 | `pillar_sonic.xml` | `python examples/07_ultrasonic.py` | `mjpython examples/07_ultrasonic.py` |
| [08_lidar.py](08_lidar.py) | 라이다 값과 GUI 관찰 | `pillar_lidar.xml` | `python examples/08_lidar.py` | `mjpython examples/08_lidar.py` |
| [09_ultrasonic_route.py](09_ultrasonic_route.py) | 초음파로 판단하며 기둥 우회 | `pillar_sonic.xml` | `python examples/09_ultrasonic_route.py` | `mjpython examples/09_ultrasonic_route.py` |
| [10_lidar_route.py](10_lidar_route.py) | 라이다로 판단하며 기둥 우회 | `pillar_lidar.xml` | `python examples/10_lidar_route.py` | `mjpython examples/10_lidar_route.py` |
| [11_ultrasonic_mapping.py](11_ultrasonic_mapping.py) | 초음파 측정점으로 지도 누적 | `pillar_sonic.xml` | `python examples/11_ultrasonic_mapping.py` | `mjpython examples/11_ultrasonic_mapping.py` |
| [12_lidar_mapping.py](12_lidar_mapping.py) | 라이다 측정점으로 지도 누적 | `pillar_lidar.xml` | `python examples/12_lidar_mapping.py` | `mjpython examples/12_lidar_mapping.py` |
| [13_maze.py](13_maze.py) | 라이다로 작은 미로 탐색 | `라이다 모델로 생성한 3×3 미로 XML` | `python examples/13_maze.py` | `mjpython examples/13_maze.py` |

## 직접 작성할 부분

1. `01_move.py`: 바퀴 움직임을 이해하고 `left`, `right` 계산식을 작성합니다.
2. `05_route_left.py`: 전진·회전·시간을 조합합니다. `06_route_right.py`에서 반대쪽 경로를 비교합니다.
3. `09_ultrasonic_route.py`: `read_front()`로 실제 센서값을 읽고 `choose(front)` 조건문으로 전진·정지를 선택합니다.
4. `10_lidar_route.py`에서는 XML과 읽기 함수가 어떻게 달라졌는지 확인합니다.

전체 코드가 파일에 들어 있습니다. PPT의 줄 번호를 따라 작성하거나 해당 부분을 바꾸고 저장한 뒤 다시 실행합니다.
`01_move.py`의 move를 이후 운전·경로·지도 실습이 실제로 재사용합니다.
`runtime.py`, `world.py`, `maze_policy.py`는 제공 코드입니다. 복잡한 물리·GUI·위치 추정·탐색기를 전부 새로 작성하지 않습니다.

## 맵과 XML

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
W/S 전진·후진, Q/E 좌·우 회전이며 A/D는 쓰지 않습니다. 키를 놓거나 다른 창을 클릭하면 정지합니다.
카메라 조작 뒤에는 GUI를 다시 클릭하세요.

## 센서와 지도

초음파는 전방 두 거리값(m), 라이다는 360방향 거리값(m)을 읽으며 반사가 없는 방향은 `inf`입니다.
초음파는 이 모델에서 이상적인 단일 광선으로 구현되며 실제 음파 확산·잡음은 재현하지 않습니다.
09·10번은 전진/정지를 센서로 판단하고 우회 단계·엔코더/IMU 이동량 추정은 제공합니다.
고정된 방의 우회이며 모든 장애물 배치에서 성공하는 범용 회피는 아닙니다.
11번은 초음파 측정점만, 12번은 라이다 측정점만 엔코더+IMU 추정 좌표에 누적합니다.
주행 뒤 실제 결과 그래프가 열리고 `outputs/examples/ultrasonic_map.png`, `lidar_map.png`와 `.npz`를 저장합니다.
정답 좌표를 쓰지 않으며 누적 오차가 있습니다. SLAM·루프 폐쇄는 구현하지 않습니다.
13번은 라이다 모델로 3×3셀·seed7 미로를 탐색합니다. 시작 배속을 입력하고 실행 중 [ / ]로 조절합니다.
GUI 미로에는 주행 제한시간이 없으며 화면 없는 검증 모드에는 180 시뮬레이션 초의 한도를 둡니다.

## 강사 실행·검증

```bash
python examples/05_route_left.py --headless
python examples/06_route_right.py --headless
python examples/09_ultrasonic_route.py --headless
python examples/10_lidar_route.py --headless
python examples/11_ultrasonic_mapping.py --headless
python examples/12_lidar_mapping.py --headless
python examples/13_maze.py --headless
```

비교 경로와 대체 센서는 선택 실행입니다. 지도·미로는 제공 코드 데모로 마무리합니다.
`examples_legacy/`의 이전 실습은 로컬 보관용이며 Git에는 포함하지 않습니다.

[설치·환경 활성화](../README.md) · [공용 함수 안내](../docs/api.md)
