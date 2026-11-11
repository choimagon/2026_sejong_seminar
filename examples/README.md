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

## MuJoCo 화면과 로봇 조작 방법

실행하면 **MuJoCo 3D 창**과 직접 만든 **Motion Controls / Sensor Monitor GUI 창**이 열립니다.
3D 창에서 카메라를 움직이고, GUI 창에서 로봇에 주행 명령을 보냅니다.
`show.py`는 모델 확인용이므로 별도의 조작 GUI는 열리지 않습니다.

### 3D 화면의 카메라 조작

마우스 포인터를 MuJoCo 3D 장면 위에 두고 조작합니다. Windows·Mac·Linux에서 공통으로 사용합니다.

| 마우스 입력 | 화면 동작 |
| --- | --- |
| 왼쪽 버튼을 누른 채 드래그 | 카메라 회전 |
| 오른쪽 버튼을 누른 채 드래그 | 시점 이동: 수직 평면 |
| Shift + 오른쪽 버튼을 누른 채 드래그 | 시점 이동: 수평 평면 |
| 휠 스크롤 또는 가운데 버튼 드래그 | 확대 / 축소 |

Mac 트랙패드는 보조 클릭을 누른 채 드래그하고, 두 손가락 스크롤로 확대·축소합니다.
보조 클릭 설정을 확인하고, 드래그가 불편하면 마우스를 사용합니다.
GUI가 있는 실습에서는 F로 로봇 추적 / 전체 보기를 전환하고 H로 전체 보기로 돌아갑니다.
카메라 조작은 [MuJoCo 공식 안내](https://mujoco.readthedocs.io/en/stable/programming/samples.html#basic)를 참고하세요.

### 주행 전에 직접 만든 GUI 창을 클릭

1. **Motion Controls / Sensor Monitor 창의 Controls 탭이나 빈 공간을 클릭**해 키보드 포커스를 줍니다.
2. W/S로 전진·후진, Q/E로 제자리 좌회전·우회전합니다. 키를 누르는 동안 주행하고 놓으면 제동합니다.
3. 3D 창에서 카메라를 조작했거나 터미널을 클릭했다면, **GUI 창을 다시 클릭한 뒤** 주행 키를 누릅니다.

현재 실습의 주행 키는 **W/S/Q/E**입니다. WASD 방식의 A/D 회전은 사용하지 않습니다.
GUI가 포커스를 잃으면 정지 명령을 보냅니다. 명령 입력 중에는 Enter로 입력을 마친 뒤 주행합니다.
실습 06에서 `GUI 클릭 → W로 전진 → 키 놓고 정지 → Q/E로 회전`을 먼저 확인하세요.

## 실습별 실행 명령어

프로젝트 루트에서 해당 파일의 본문을 끝까지 작성하고 저장한 뒤 실행합니다.
`-m examples.파일명`은 `module` 라이브러리를 찾을 수 있게 모듈로 실행하는 옵션이며 `.py`는 붙이지 않습니다.

| 실습 파일 | Windows PowerShell | Mac 터미널 |
| --- | --- | --- |
| `01_move.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.01_move` | `seminar_mujoco/bin/mjpython -m examples.01_move` |
| `02_imu.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.02_imu` | `seminar_mujoco/bin/python -m examples.02_imu` |
| `03_encoders.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.03_encoders` | `seminar_mujoco/bin/python -m examples.03_encoders` |
| `04_ultrasonic.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.04_ultrasonic` | `seminar_mujoco/bin/python -m examples.04_ultrasonic` |
| `05_lidar.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.05_lidar` | `seminar_mujoco/bin/python -m examples.05_lidar` |
| `06_keyboard_gui.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.06_keyboard_gui` | `seminar_mujoco/bin/mjpython -m examples.06_keyboard_gui` |
| `07_move_algorithm.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.07_move_algorithm` | `seminar_mujoco/bin/python -m examples.07_move_algorithm` |
| `08_lidar_straight.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.08_lidar_straight` | `seminar_mujoco/bin/mjpython -m examples.08_lidar_straight` |
| `09_ultrasonic_straight.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.09_ultrasonic_straight` | `seminar_mujoco/bin/mjpython -m examples.09_ultrasonic_straight` |
| `10_lidar_corner.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.10_lidar_corner` | `seminar_mujoco/bin/mjpython -m examples.10_lidar_corner` |
| `11_ultrasonic_corner.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.11_ultrasonic_corner` | `seminar_mujoco/bin/mjpython -m examples.11_ultrasonic_corner` |
| `12_lidar_junction.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.12_lidar_junction` | `seminar_mujoco/bin/mjpython -m examples.12_lidar_junction` |
| `13_ultrasonic_junction.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.13_ultrasonic_junction` | `seminar_mujoco/bin/mjpython -m examples.13_ultrasonic_junction` |
| `14_lidar_cross.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.14_lidar_cross` | `seminar_mujoco/bin/mjpython -m examples.14_lidar_cross` |
| `15_ultrasonic_cross.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.15_ultrasonic_cross` | `seminar_mujoco/bin/mjpython -m examples.15_ultrasonic_cross` |
| `16_maze_escape.py` | `.\seminar_mujoco\Scripts\python.exe -m examples.16_maze_escape` | `seminar_mujoco/bin/mjpython -m examples.16_maze_escape` |

학생용 파일은 import만 있으므로 본문 작성 전 바로 종료되는 것이 정상입니다.

### 가상환경 활성화와 Windows 오류 해결

가상환경 폴더 이름은 **`seminar_mujoco`**로 통일합니다.
이전 환경 폴더의 이름만 바꾸지 말고, 위 생성 명령으로 새 환경을 만든 뒤 패키지를 설치합니다.

Windows PowerShell에서 활성화합니다.

```powershell
.\seminar_mujoco\Scripts\Activate.ps1
```

“이 시스템에서 스크립트를 실행할 수 없습니다”, `PSSecurityException` 또는 `UnauthorizedAccess` 오류가 나오면
**같은 PowerShell 창에서** 아래 두 줄을 순서대로 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\seminar_mujoco\Scripts\Activate.ps1
```

`-Scope Process`는 현재 PowerShell 창에만 적용되며 창을 닫으면 해제됩니다.
관리자 권한은 필요 없습니다. 조직의 그룹 정책으로 차단되면 활성화 대신 아래의 실행 파일 직접 지정 방식을 사용합니다.
[Microsoft 실행 정책 안내](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy#example-6-set-the-execution-policy-for-the-current-powershell-session)

Mac / Linux에서는 다음 명령으로 활성화합니다.

```bash
source seminar_mujoco/bin/activate
```

활성화 후 프롬프트에 `(seminar_mujoco)`가 표시됩니다. Windows / Linux에서는 `python show.py`,
Mac에서는 `mjpython show.py`로 설치를 확인합니다. 새 터미널을 열면 다시 활성화합니다.
환경을 종료하려면 `deactivate`를 입력합니다.
아래 실습별 명령처럼 `seminar_mujoco` 안의 실행 파일을 직접 지정하면 활성화 없이도 실행할 수 있습니다.
