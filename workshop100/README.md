# 100분 로봇 실습: 직접 운전에서 센서 기반 주행까지

대학교 2학년·기초 Python 기준입니다. **50분 수업 → 10분 휴식 → 50분 수업**이며 설치는 사전에 마칩니다.
필수 목표는 학생이 작성한 `move`로 운전하고 센서값으로 기둥 앞에서 멈춘 뒤 제공 우회 실행기로 목표에 도착하는 것입니다.
지도·미로는 제공 코드를 실행하고 설정을 바꾸는 마무리 데모입니다.
기존 `examples/`의 16개 실습은 심화 자료로 유지합니다.

## 시작하기

프로젝트 루트에서 최초 한 번 환경을 만듭니다.

Windows PowerShell:

```powershell
py -3.12 -m venv seminar_mujoco
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\seminar_mujoco\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python show.py
```

Mac:

```bash
python3.12 -m venv seminar_mujoco
source seminar_mujoco/bin/activate
python -m pip install -r requirements.txt
python show.py
```

새 터미널에서는 환경 생성·설치를 반복하지 않고 환경 활성화부터 진행합니다.
Windows 실행 정책은 현재 창에만 적용됩니다. Linux는 Mac과 같이 활성화한 뒤 MuJoCo 창도 `python`으로 실행합니다.

## 진행표

| 구간 | 분 | 내용 | 학생 작성 범위 |
| --- | --- | --- | --- |
| 전반 | 5 | show.py와 카메라 조작 확인 | 없음 |
| 전반 | 10 | move 함수 만들기 | my_move.py의 left/right 두 줄 |
| 전반 | 10 | W/S/Q/E로 직접 운전·맵 바꾸기 | 없음 |
| 전반 | 20 | 센서 없이 기둥 뒤 목표로 이동 | my_route.py의 ACTIONS 목록 |
| 전반 | 5 | 비교·진도 맞추기 | 기둥 위치가 바뀌면? |
| 휴식 | 10 | 쉬는 시간 | |
| 후반 | 8 | 초음파·라이다 설명 | 없음 |
| 후반 | 7 | 거리값·라이다 스캔 직접 확인 | 04_sensors.py의 읽기·출력 확인 |
| 후반 | 20 | 센서로 전진/정지 판단하고 우회 | my_sensor.py의 choose 함수 |
| 후반 | 8 | 누적 2D 지도 데모 | 제공 코드 실행·센서별 점 비교 |
| 후반 | 7 | 작은 미로 데모·정리 | 제공 코드 실행·속도 한 가지 변경 |

설치가 안 된 학생은 짝과 진행하고 수업 중 개별 설치에 전체 진도를 멈추지 않습니다.
전반 40분까지 경로가 안 풀리면 강사가 `--answer` 결과를 보여주고 센서 필요성으로 넘어갑니다.
후반 35분에 센서 주행을 마무리하고 지도·미로는 강사 화면으로 진행해도 됩니다.

## 실행 명령

모든 명령은 환경 활성화 후 프로젝트 루트에서 실행합니다. `-m`은 필요 없습니다.

| 단계 | Windows / Linux | Mac |
| --- | --- | --- |
| 모델 확인 | `python show.py` | `python show.py` |
| 1. move 확인 | `python workshop100/01_move.py` | `mjpython workshop100/01_move.py` |
| 2. GUI 운전 | `python workshop100/02_keyboard.py` | `mjpython workshop100/02_keyboard.py` |
| 3. 시간 기반 경로 | `python workshop100/03_route.py` | `mjpython workshop100/03_route.py` |
| 4. 센서 관찰 | `python workshop100/04_sensors.py` | `mjpython workshop100/04_sensors.py` |
| 5. 센서 주행 | `python workshop100/05_sensor_route.py` | `mjpython workshop100/05_sensor_route.py` |
| 6. 지도 데모 | `python workshop100/06_mapping.py` | `mjpython workshop100/06_mapping.py` |
| 7. 미로 데모 | `python workshop100/07_maze.py` | `mjpython workshop100/07_maze.py` |

1–5번은 `my_move.py`에서 만든 함수를 실제로 사용합니다. 수정 후 파일을 저장하고 실행 창을 닫아 다시 실행합니다.
작성을 마치기 전에는 로봇이 움직이지 않습니다. 5번은 미작성 상태를 감지하면 안내와 함께 종료합니다.
6–7번은 수업 시간에 맞추기 위해 제공 완성 코드를 사용합니다.

## 1. move 함수: 학생이 채울 두 줄

`my_move.py`에 필요한 반지름과 바퀴 간격을 제공합니다.

```python
left = (linear - angular * track / 2) / radius
right = (linear + angular * track / 2) / radius
```

`linear`는 m/s, `angular`는 rad/s, 좌우 바퀴 명령은 rad/s입니다.
양의 angular는 왼쪽 회전입니다. `move`는 목표 속도를 설정하고 실행기가 물리 시간을 진행합니다.
로봇은 옆으로 바로 이동하지 않으므로 좌회전·전진·우회전으로 옆 통로로 이동합니다.
PID·토크 제어·모터 물리는 제공하며 학생이 다시 구현하지 않습니다.

## 2. 직접 운전과 맵 선택

```powershell
python workshop100/02_keyboard.py --map shifted
python workshop100/02_keyboard.py --map offset
```

Mac은 `python`을 `mjpython`으로 바꿉니다. 기본 맵은 `pillar`입니다.
모두 약 3.4m × 3m 방에 외벽 네 개와 반지름 22cm 기둥 한 개를 배치합니다.
`shifted`는 기둥을 앞으로 옮기고 `offset`은 옆으로 옮깁니다. 파란 출발점에서 초록 목표로 갑니다.
**Motion Controls / Sensor Monitor 창의 Controls 탭을 먼저 클릭**한 다음 W/S로 전후진, Q/E로 회전합니다.
키를 놓거나 다른 창으로 포커스를 옮기면 정지합니다. 카메라를 움직인 뒤에는 GUI를 다시 클릭합니다.
MuJoCo 3D 창에서 왼쪽 드래그는 회전, 오른쪽 드래그는 시점 이동, Shift+오른쪽 드래그는 수평 이동, 휠은 확대/축소입니다.

## 3. 센서 없이 경로 작성

`my_route.py`에 `(linear, angular, seconds)` 목록을 작성합니다.
직진 → 왼쪽 통로로 이동 → 기둥을 지나기 → 오른쪽으로 돌아오기 → 목표에서 정지를 만듭니다.
시간과 속도로 거리를 예상하지만 가속·제동 때문에 `거리 = 속도 × 시간`과 실제 이동은 차이가 납니다.
정확한 90도 회전도 보장되지 않으므로 직접 관찰하고 시간을 조절합니다.
같은 코드를 `--map shifted`에 실행해 차이를 비교합니다. 모든 배치에서 실패한다는 의미는 아닙니다.
**질문: 기둥 위치를 모르면 몇 초, 몇 m 전진해야 할까요?**

## 4. 초음파·라이다 읽기

```python
from module import sensor
print(sensor.ultrasonic.read(robot))
scan = sensor.lidar.read(robot)
print(scan["ranges_m"][0])
```

초음파는 전방의 두 거리값(m)을 읽습니다. 이 모델은 이상적인 단일 광선 거리 측정이며 실제 음파 확산·잡음은 재현하지 않습니다.
라이다는 전방 0도부터 왼쪽으로 도는 360방향 거리값입니다. 거리가 없는 방향은 `inf`입니다.
GUI의 Ultrasonic / LiDAR 탭을 바꾸고 로봇을 회전시켜 같은 기둥을 어떻게 보는지 확인합니다.

## 5. 센서로 전진·정지 판단

`my_sensor.py`의 `choose(front)`에 조건문을 작성합니다.

```python
if front > STOP_DISTANCE:
    return 0.25, 0.0
return 0.0, 0.0
```

```powershell
python workshop100/05_sensor_route.py
python workshop100/05_sensor_route.py --sensor lidar
python workshop100/05_sensor_route.py --map shifted
```

학생이 작성한 조건으로 전진하다가 기둥 앞에서 정지합니다.
이후 좌회전 → 0.8m 측면 이동 → 1.35m 우회 → 복귀 → 앞벽 거리로 최종 정지는 제공 실행기가 처리합니다.
이동량은 엔코더, 회전량은 IMU로 추정합니다. 실행기는 실측 위치를 정답처럼 사용하지 않습니다.
**이 실습은 고정된 방의 기둥 우회이며 임의의 장애물·모든 맵에서 동작하는 범용 회피 알고리즘은 아닙니다.**
실패하면 임계거리·회전 방향·기둥과의 여유를 확인합니다.

## 6. 누적 2D 지도와 7. 미로

지도 데모는 엔코더+IMU의 추정 위치·방향으로 초음파/라이다 측정점을 같은 2D 좌표계로 옮깁니다.
센서 원점 오프셋을 반영하며 실제 좌표나 미로 지도를 가져오지 않습니다.
주행 후 `outputs/workshop100/sensor_map.png`와 `.npz`를 저장하고 그래프를 엽니다.
기록한 점으로 만든 지도이며 점유격자·SLAM·루프 폐쇄는 구현하지 않습니다. 명령만 누적하는 방식보다 낫지만 미끄러짐·센서 오차로 누적 오차가 생깁니다.
미로는 제공 정책으로 3×3셀·seed 7 배치를 실행합니다. 시작 배속을 터미널에 입력하고 실행 중 `[`/`]`로 조절합니다.
GUI 실행에 주행 제한시간은 없으며 `maze_policy.py`의 속도·판단을 바꿔 비교합니다.
이 예시의 성공이 모든 미로에서의 성공을 보장하지는 않습니다.

## 강사 확인·복구

1–5번에 `--answer`를 붙이면 학생 파일을 덮어쓰지 않고 제공 답안을 사용합니다.

```bash
python workshop100/05_sensor_route.py --answer --headless
python workshop100/05_sensor_route.py --answer --headless --sensor lidar --map shifted
python workshop100/06_mapping.py --headless
python workshop100/07_maze.py --headless
```

`--headless`는 화면 없이 빠르게 검증하는 강사용 옵션입니다. `02_keyboard.py`는 GUI가 필수입니다.
지도 저장은 창 없이 가능하며, 미로 검증 모드만 180 시뮬레이션 초의 안전 한도를 둡니다.

`show.py`는 자체 MuJoCo 창을 여는 모델 확인 도구이므로 Mac도 `python show.py`로 실행합니다.
Mac의 나머지 GUI 실습 파일은 `mjpython`을 사용합니다.
