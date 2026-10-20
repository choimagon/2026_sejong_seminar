# 학생용 실습 01–16

각 Python 파일에는 해당 실습에 필요한 **import만** 있습니다.
변수 설정, 반복문, 센서 측정, 그래프, 주행 판단과 실행 코드는 수업에서 직접 작성합니다.
본문 작성 전 실행하면 import 후 바로 종료되는 것이 정상입니다.

| 번호 | 파일 | 작성할 내용 |
| --- | --- | --- |
| 01 | [01_move.py](01_move.py) | 모델·MuJoCo 창 열기, move의 선속도·각속도와 실행 시간 |
| 02 | [02_imu.py](02_imu.py) | IMU 측정 → NumPy 배열 → Matplotlib 그래프 |
| 03 | [03_encoders.py](03_encoders.py) | 엔코더 측정 → NumPy 배열 → Matplotlib 그래프 |
| 04 | [04_ultrasonic.py](04_ultrasonic.py) | 초음파 측정 → NumPy 배열 → Matplotlib 그래프 |
| 05 | [05_lidar.py](05_lidar.py) | 라이다 측정 → NumPy 배열 → Matplotlib 그래프 |
| 06 | [06_keyboard_gui.py](06_keyboard_gui.py) | W/S/Q/E 조작, 이후 센서 GUI 확인 |
| 07 | [07_move_algorithm.py](07_move_algorithm.py) | 센서값에 따른 move 명령과 직접 그린 그래프 |
| 08 | [08_lidar_straight.py](08_lidar_straight.py) | 라이다 기반 직선 주행 |
| 09 | [09_ultrasonic_straight.py](09_ultrasonic_straight.py) | 초음파 기반 직선 주행 |
| 10 | [10_lidar_corner.py](10_lidar_corner.py) | 라이다 기반 ㄱ자 주행·제자리/곡선 회전 |
| 11 | [11_ultrasonic_corner.py](11_ultrasonic_corner.py) | 초음파 기반 ㄱ자 주행·제자리/곡선 회전 |
| 12 | [12_lidar_junction.py](12_lidar_junction.py) | 라이다 기반 T자 주행 |
| 13 | [13_ultrasonic_junction.py](13_ultrasonic_junction.py) | 초음파 기반 T자 주행 |
| 14 | [14_lidar_cross.py](14_lidar_cross.py) | 라이다 기반 +자 주행 |
| 15 | [15_ultrasonic_cross.py](15_ultrasonic_cross.py) | 초음파 기반 +자 주행 |
| 16 | [16_maze_escape.py](16_maze_escape.py) | 매번 새로운 10×10 미로·직접 선택하는 배속·탈출 판단 |

파일을 작성한 뒤 이 폴더의 상위, 즉 저장소 루트에서 실행합니다.

```bash
# macOS: MuJoCo 창을 사용하는 경우
mjpython -m examples.01_move

# 센서 측정과 Matplotlib만 사용하는 경우
python -m examples.02_imu

# Windows / Linux
python -m examples.01_move
```

01·06·08–16번처럼 macOS에서 MuJoCo 창을 여는 실습은 `mjpython`을 사용합니다.
02–05·07번의 측정·그래프 실습은 `python`으로 실행할 수 있습니다.

[설치·실행](../README.md) · [실습 목표·시간표](../docs/practice.md) · [함수·반환값 안내](../docs/api.md)
