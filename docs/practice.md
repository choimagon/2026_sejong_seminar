# 2시간 실습 안내

학습 목표는 사람이 눈으로 보고 운전하던 판단을 센서값과 코드로 바꾸는 것입니다.
설치는 수업 전에 마칩니다. 16개 파일의 본문은 수업을 따라 직접 작성합니다.

| 경과 시간 | 실습 | 내용 | 소요 |
| --- | --- | --- | --- |
| 00:00–00:05 | 01 | MuJoCo 창·move·run_for | 5분 |
| 00:05–00:35 | 02–06 | 센서 직접 측정·NumPy·Matplotlib·키보드 GUI | 30분 |
| 00:35–00:45 | 07 | 센서 조건으로 move 제어·GUI 그래프와 비교 | 10분 |
| 00:45–01:25 | 08–15 | 직선·ㄱ자·T자·+자 × 라이다/초음파 | 40분 |
| 01:25–01:55 | 16 | 새 10×10 미로·배속 조절·실패 장면 확인 | 30분 |
| 01:55–02:00 | 공유 | 주행 결과와 개선점 정리 | 5분 |

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

## 저장소 클론과 설치 후 테스트

Git과 Python 3.12를 먼저 설치합니다. Windows는 PowerShell, Mac은 터미널을 엽니다.
아래 두 줄은 두 운영체제에서 같습니다. `git clone`은 실습 파일을 내려받고, `cd`는 내려받은 프로젝트 폴더로 이동합니다.

```bash
git clone https://github.com/choimagon/2026_sejong_seminar.git
cd 2026_sejong_seminar
```

Windows PowerShell에서 `seminar_mujoco` 환경을 만들고 설치·테스트합니다. 활성화 오류가 나면 바로 아래 해결 절차를 먼저 실행합니다.

```powershell
py -3.12 -m venv seminar_mujoco
.\seminar_mujoco\Scripts\Activate.ps1
.\seminar_mujoco\Scripts\python.exe -m pip install -r requirements.txt
.\seminar_mujoco\Scripts\python.exe show.py
```

Mac 터미널에서 설치하고 테스트합니다. Python 3.12를 사용합니다.

```bash
python3.12 -m venv seminar_mujoco
source seminar_mujoco/bin/activate
seminar_mujoco/bin/python -m pip install -r requirements.txt
seminar_mujoco/bin/mjpython show.py
```

`venv`는 프로젝트 전용 Python 환경을 만들고, `pip install -r requirements.txt`는 필요한 패키지를 설치합니다.
`show.py`를 실행해 MuJoCo 3D 창에 로봇이 보이면 설치 테스트 성공입니다. 창을 닫은 뒤 실습을 시작합니다.
파일을 찾지 못하면 `cd 2026_sejong_seminar`로 이동했는지 확인합니다.
Mac에서 MuJoCo 창을 여는 실습은 `mjpython`, 측정·그래프만 사용하는 실습은 `python`을 씁니다.
새 터미널에서도 저장소 루트로 이동한 뒤 아래 명령을 실행하면 됩니다.

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

## 01 · 모델과 이동

로봇을 불러오고 MuJoCo 창에서 전진·후진·제자리 회전·곡선·정지를 확인합니다.
선속도(m/s), 각속도(rad/s), 실행 시간(시뮬레이션 초)을 구분합니다.
선속도와 각속도를 함께 주었을 때의 움직임을 설명할 수 있으면 됩니다.

## 02–05 · 센서 측정과 그래프

각 센서의 `read(robot)` 함수를 직접 호출해 값의 구조와 단위를 확인합니다.
반복문으로 시각과 측정값을 모으고 NumPy 배열로 바꾼 뒤 Matplotlib으로 표시합니다.
센서 읽기와 물리 시간 진행을 구분하고, 측정 주기를 바꾸며 표본 수와 그래프를 비교합니다.

| 센서 | 관찰할 내용 |
| --- | --- |
| IMU | 정지·전진·회전에서 가속도와 자이로 각 축의 변화 |
| 엔코더 | 좌우 바퀴 각도·각속도·회전 거리 |
| 초음파 | 벽에 접근하거나 방향을 바꿀 때의 거리 변화 |
| 라이다 | 방향별 거리와 360도 스캔의 좌표 |

## 06–07 · 직접 운전에서 코드로

먼저 GUI의 Controls에서 W/S/Q/E로 직접 운전합니다.
그다음 센서값에 따라 `move`의 선속도·각속도를 선택하는 코드를 작성합니다.
직접 측정해서 그린 그래프를 확인한 뒤 GUI의 센서 탭으로 같은 종류의 정보를 봅니다.
GUI에는 오도메트리 탭을 추가하지 않습니다.

## 08–15 · 네 코스, 두 센서

준비된 XML을 사용하므로 코스 생성 코드는 작성하지 않습니다.
거리 센서는 라이다 또는 초음파를 사용하고, 이동거리·회전량에는 엔코더·IMU를 함께 활용합니다.

| 코스 | 라이다 / 초음파 | 판단할 내용 |
| --- | --- | --- |
| 직선 | 08 / 09 | 전방 거리와 정지 시점 |
| ㄱ자 | 10 / 11 | 회전 시작 위치와 제자리·곡선 회전 |
| T자 | 12 / 13 | 전방 막힘, 좌우 통로와 방향 선택 |
| +자 | 14 / 15 | 앞이 열려 있어도 옆 통로와 교차로 인식 |

라이다의 방향별 거리와 초음파를 몸체 회전으로 측정하는 방법을 비교합니다.
속도·거리 기준·곡선 반지름을 바꾸고 실패한 장면의 센서값을 확인합니다.

## 16 · 매번 새 미로

10×10셀, 셀 간격 30cm인 미로에서 작성한 알고리즘을 시험합니다.
`seed=None`이면 새로 실행할 때마다 다른 미로가 만들어집니다.
같은 배치를 다시 확인할 때는 출력한 seed를 사용하거나 GUI에서 R로 초기화합니다.

주행 제한시간은 두지 않습니다. 시작 배속을 직접 입력하고 실행 중에도 바꿀 수 있도록 작성합니다.
`ask_speed()`는 배속 입력을 받고, `course.view`의 `playback_controls=True`는 배속 조절을 활성화합니다.
배속은 모터 목표와 물리 시간 간격을 바꾸지 않으며, 재생 진행률을 조절합니다.

| 미로 조작 | 기능 |
| --- | --- |
| `speed <배수>` | 원하는 배속 지정 |
| `[` / `]` | 현재 배속 절반 / 두 배 |
| Space | 일시정지 / 재개 |
| R | 현재 미로 초기화 |

알고리즘은 센서 관측으로 판단하고, 미로의 연결 정보나 실제 좌표를 정답 지도처럼 사용하지 않습니다.
다른 배치에서도 작동하는지 반복해서 확인합니다.

[실습 파일 목록](../examples/README.md) · [라이브러리 안내](api.md)
