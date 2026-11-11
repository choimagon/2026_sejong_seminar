# MuJoCo 로봇 시뮬레이터 실습

## 기본 수업: 100분 실습

**전반 50분 → 휴식 10분 → 후반 50분**으로 진행합니다. 대학교 2학년·기초 Python 기준입니다.
[100분 실습 안내와 실행 명령](workshop100/README.md)을 먼저 확인하세요.

`show.py` 확인 → move 함수 두 줄 작성 → W/S/Q/E 운전 → 센서 없는 기둥 우회 → 초음파·라이다 → 센서로 우회 → 누적 2D 지도·미로 데모 순서입니다.
직접 작성은 `workshop100/my_move.py`, `my_route.py`, `my_sensor.py` 세 파일입니다.
기존 `examples/`의 16개 실습과 상세 설명은 심화·추가 과제로 유지합니다.


차동구동 로봇의 이동·센서·센서 기반 주행을 배우는 자료입니다. 아래의 16개 상세 실습은 심화 과정입니다.
구동 바퀴 2개와 볼 캐스터를 사용하며 IMU·휠 엔코더·초음파·360도 2D 라이다를 다룹니다.

**`examples/`의 실습 파일 16개는 라이브러리 import와 실행 경로 설정이 들어 있는 학생 작성용 파일입니다.**
수업을 따라 실행 본문을 직접 작성합니다. 작성 전에는 실행해도 창이나 그래프가 뜨지 않고 종료됩니다.

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

Windows PowerShell에서 환경 생성 → 실행 정책 설정 → 활성화 → 설치 → 테스트 순서로 진행합니다.

```powershell
py -3.12 -m venv seminar_mujoco
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\seminar_mujoco\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python show.py
```

Mac 터미널에서 설치하고 테스트합니다. Python 3.12를 사용합니다.

```bash
python3.12 -m venv seminar_mujoco
source seminar_mujoco/bin/activate
python -m pip install -r requirements.txt
mjpython show.py
```

`venv`는 프로젝트 전용 Python 환경을 만들고, `pip install -r requirements.txt`는 필요한 패키지를 설치합니다.
`show.py`를 실행해 MuJoCo 3D 창에 로봇이 보이면 설치 테스트 성공입니다. 창을 닫은 뒤 실습을 시작합니다.
파일을 찾지 못하면 `cd 2026_sejong_seminar`로 이동했는지 확인합니다.
Mac에서 MuJoCo 창을 여는 실습은 `mjpython`, 측정·그래프만 사용하는 실습은 `python`을 씁니다.
새 터미널에서는 저장소 루트로 이동하고 환경을 활성화한 뒤 아래 명령을 실행합니다.

### 환경 활성화 후 실행하기

환경 이름은 **`seminar_mujoco`**입니다. 아래 명령은 저장소 루트에서 실행합니다.
새 터미널을 열 때마다 환경을 다시 활성화한 뒤 실습을 실행합니다.

Windows PowerShell에서는 아래 세 줄을 순서대로 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\seminar_mujoco\Scripts\Activate.ps1
python show.py
```

실행 정책 설정은 현재 PowerShell 창에만 적용되며 창을 닫으면 해제됩니다.
[Microsoft 실행 정책 안내](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy#example-6-set-the-execution-policy-for-the-current-powershell-session)

Mac 터미널에서는 환경을 활성화하고 MuJoCo 창을 엽니다.

```bash
source seminar_mujoco/bin/activate
mjpython show.py
```

Linux도 `source seminar_mujoco/bin/activate`로 활성화하며 모델 확인은 `python show.py`입니다.
프롬프트의 `(seminar_mujoco)`를 확인한 뒤 아래 실습별 명령을 실행합니다.
Windows / Linux는 `python`, Mac에서 MuJoCo 창을 여는 실습은 `mjpython`을 사용합니다.
Mac의 센서 측정·그래프 실습은 `python`으로 실행합니다. 환경을 종료하려면 `deactivate`를 입력합니다.
기존 환경 폴더는 이름만 바꾸지 말고 처음 한 번 `seminar_mujoco`로 새로 생성하고 패키지를 설치합니다.

## 실습별 실행 명령어

프로젝트 루트에서 `seminar_mujoco` 환경을 먼저 활성화합니다. 해당 파일의 본문을 끝까지 작성하고 저장한 뒤 아래 명령을 실행합니다.
`python examples/파일명.py`처럼 파일 경로를 입력합니다. 실습 파일이 프로젝트 라이브러리를 자동으로 찾으므로 `-m`은 필요 없습니다.

| 실습 파일 | Windows PowerShell | Mac 터미널 |
| --- | --- | --- |
| `01_move.py` | `python examples/01_move.py` | `mjpython examples/01_move.py` |
| `02_imu.py` | `python examples/02_imu.py` | `python examples/02_imu.py` |
| `03_encoders.py` | `python examples/03_encoders.py` | `python examples/03_encoders.py` |
| `04_ultrasonic.py` | `python examples/04_ultrasonic.py` | `python examples/04_ultrasonic.py` |
| `05_lidar.py` | `python examples/05_lidar.py` | `python examples/05_lidar.py` |
| `06_keyboard_gui.py` | `python examples/06_keyboard_gui.py` | `mjpython examples/06_keyboard_gui.py` |
| `07_move_algorithm.py` | `python examples/07_move_algorithm.py` | `python examples/07_move_algorithm.py` |
| `08_lidar_straight.py` | `python examples/08_lidar_straight.py` | `mjpython examples/08_lidar_straight.py` |
| `09_ultrasonic_straight.py` | `python examples/09_ultrasonic_straight.py` | `mjpython examples/09_ultrasonic_straight.py` |
| `10_lidar_corner.py` | `python examples/10_lidar_corner.py` | `mjpython examples/10_lidar_corner.py` |
| `11_ultrasonic_corner.py` | `python examples/11_ultrasonic_corner.py` | `mjpython examples/11_ultrasonic_corner.py` |
| `12_lidar_junction.py` | `python examples/12_lidar_junction.py` | `mjpython examples/12_lidar_junction.py` |
| `13_ultrasonic_junction.py` | `python examples/13_ultrasonic_junction.py` | `mjpython examples/13_ultrasonic_junction.py` |
| `14_lidar_cross.py` | `python examples/14_lidar_cross.py` | `mjpython examples/14_lidar_cross.py` |
| `15_ultrasonic_cross.py` | `python examples/15_ultrasonic_cross.py` | `mjpython examples/15_ultrasonic_cross.py` |
| `16_maze_escape.py` | `python examples/16_maze_escape.py` | `mjpython examples/16_maze_escape.py` |

학생용 파일은 import와 실행 경로 설정만 있으므로 본문 작성 전 바로 종료되는 것이 정상입니다.

## 폴더 구성

```text
.
├── README.md            설치·실행·배포 범위
├── requirements.txt     실행에 필요한 Python 패키지
├── .gitignore           가상환경·캐시·생성 결과 제외
├── examples/            01–16번 실습: import·실행 경로 설정 제공
├── module/              이동·센서·GUI·코스 실행 라이브러리
│   ├── move.py          선속도·각속도 제어
│   ├── graph.py         원하는 X·Y 입력으로 그래프 그리기
│   ├── motion/          모터·바퀴·거리·회전·키보드 제어
│   ├── sensor/          센서별 측정 함수
│   └── course/          준비된 코스·랜덤 미로·주행 실행기
├── model_xml/           basic / lidar / sonic / all 로봇 XML 4종
├── scenes/              직선·ㄱ자·T자·+자 × 로봇 4종: XML 16개
├── docs/                실습 목표·라이브러리 함수 안내
├── show.py              all 모델 확인
├── show_multi.py        한 MuJoCo 화면에서 모델 4종 비교
├── move.py              키보드 주행 창
├── sensor_view.py       MuJoCo 창과 센서 GUI
└── module_sensor.py     기존 module_sensor.view 호출 호환
```

## 설치

Python 3.12와 Git을 설치한 뒤 위의 **저장소 클론과 설치 후 테스트** 순서대로 진행합니다.
환경 이름은 `seminar_mujoco`이며, PowerShell 활성화 오류는 **환경 활성화 후 실행하기**을 참고하세요.
Python·MuJoCo만 사용하므로 ROS·Isaac Sim 설치는 필요하지 않습니다.

## 먼저 실행해 보기

다음 도구는 실습 파일을 작성하기 전에도 실행할 수 있습니다.

| 확인할 내용 | macOS | Windows / Linux |
| --- | --- | --- |
| all 로봇 모델 | `mjpython show.py` | `python show.py` |
| 네 로봇 모델 비교 | `mjpython show_multi.py` | `python show_multi.py` |
| 키보드 주행 | `mjpython move.py` | `python move.py` |
| 센서 GUI | `mjpython sensor_view.py` | `python sensor_view.py` |

macOS에서 MuJoCo 창을 여는 코드는 `mjpython`으로 실행합니다.
GUI에는 MuJoCo 3D 화면과 별도의 조작·센서 창이 있습니다.
조작·센서 창에 포커스를 두고 키를 누릅니다.

| 조작 | 동작 |
| --- | --- |
| W / S | 전진 / 후진 |
| Q / E | 제자리 좌회전 / 우회전 |
| 키 놓기 | 정지 목표로 제동 |
| Space | 일시정지 / 재개 |
| R | 초기화 |
| Motor 버튼, `+` / `-` | 실제 모터 속도 설정 변경 |

처음에는 Controls 탭이 열립니다. 모델에 장착된 센서만 다른 탭에 표시합니다.
GUI에는 오도메트리 탭을 넣지 않았습니다.

## 실습 순서와 실행

파일별 목표와 실행 방법은 [실습 목록](examples/README.md),
시간 배분은 [2시간 실습 안내](docs/practice.md)를 참고하세요.
함수 이름·단위·센서 반환값은 [라이브러리 안내](docs/api.md)에 정리했습니다.
그래프는 `graph.plot(x, y, ...)`에 원하는 열·범례·단위를 넣습니다.
여러 패널·선 겹치기·극좌표 입력은 [그래프 안내](docs/graphs.md)에 있습니다.

실습 본문을 작성한 뒤 번호와 파일 이름으로 실행합니다.

```bash
# macOS: MuJoCo 창을 사용하는 실습
mjpython examples/01_move.py
mjpython examples/06_keyboard_gui.py
mjpython examples/08_lidar_straight.py
mjpython examples/16_maze_escape.py

# 센서 측정과 Matplotlib 실습
python examples/02_imu.py
python examples/03_encoders.py
python examples/04_ultrasonic.py
python examples/05_lidar.py
python examples/07_move_algorithm.py
```

Windows / Linux에서는 위의 `mjpython`을 `python`으로 바꿉니다.
`python examples/01_move.py`처럼 프로젝트 루트에서 파일 경로로 실행합니다.
프로젝트 라이브러리 경로는 실습 파일이 자동으로 설정합니다.

## 모델과 코스

| 모델 이름 | 센서 구성 |
| --- | --- |
| `basic` | IMU·휠 엔코더 |
| `lidar` | basic + 2D 라이다 |
| `sonic` | basic + 전방 초음파 |
| `all` | IMU·휠 엔코더·초음파·2D 라이다 |

준비된 코스 이름은 `straight`(직선), `corner`(ㄱ자), `junction`(T자), `cross`(+자)입니다.
`course.scenario(코스, 모델)`은 `scenes/`의 XML을 읽습니다.

마지막 실습은 `course.square_maze("all", size=10, seed=None)`으로 매번 새 10×10 미로를 만듭니다.
한 셀은 30cm×30cm이며 자동 탈출 판단 코드는 학생이 작성합니다.
미로 주행에는 제한시간을 두지 않고, 미로 실습에서만 재생 배속을 직접 선택하도록 구성합니다.
생성된 미로·그래프·기록은 `outputs/`에 저장되며 Git에서 제외합니다.

`move(robot, linear=..., angular=...)`의 단위는 m/s·rad/s입니다.
이 함수는 속도 목표를 정하며, 실제 시간 진행은 `robot.step()` 또는 `robot.run_for(초)`로 합니다.
모터 속도와 시뮬레이션 재생 배속은 서로 다른 설정입니다.

## GitHub에 올릴 범위

**이 폴더 안의 내용을 GitHub 저장소의 루트로 사용합니다.**
`module/`의 라이브러리 구현과 GUI는 그대로 제공하고, 학생용 예제 본문만 비워두었습니다.

| 포함 | 제외 |
| --- | --- |
| 라이브러리·모델·준비된 코스 | 완성된 실습 예제·이전 예제 archive |
| import·실행 경로 설정만 있는 실습 16개 | 완성 코드가 포함된 코드북 웹사이트 |
| 모델 확인·키보드·센서 GUI 도구 | PPT·PDF·발표 대본·동영상·미리보기 |
| README·실습 목표·함수 안내·설치 목록 | `seminar_mujoco`·캐시·실행 결과·로컬 설정 |

프로젝트 전체를 올리는 대신 이 폴더의 파일만 사용합니다.
기존 강사용 완성 코드와 발표 자료는 원본 프로젝트에 보관되어 있습니다.

## Windows·Mac·Linux GUI 호환 수정

조작 창·센서 창·코스 GUI는 공통 시뮬레이터 실행기를 사용합니다.
Windows는 파이프 핸들을 명시적으로 상속하고, Mac·Linux는 파일 디스크립터를 전달합니다.
Windows에서 `AssertionError: pass_fds not supported on Windows`가 발생하는 이전 버전은 최신 `module/simulation.py`로 교체해야 합니다.
실습 06뿐 아니라 센서 GUI와 08–16번 GUI에도 같은 수정이 적용됩니다.

프로젝트 루트에서 연결 회귀 테스트를 실행합니다. 테스트는 실제 자식 프로세스와 양방향 통신하며 화면을 열지 않습니다.

```powershell
# Windows PowerShell
python -m unittest discover -s tests -p test_simulation_start.py -v
```

```bash
# Mac / Linux
python -m unittest discover -s tests -p test_simulation_start.py -v
```

GitHub Actions의 `Desktop platform smoke tests`는 Windows·Mac·Linux에서 이 연결 테스트를 실행합니다.
화면과 키보드 검증은 각 OS의 데스크톱에서 추가로 실행합니다.
Windows는 `python examples/06_keyboard_gui.py`,
Mac은 `mjpython examples/06_keyboard_gui.py`,
Linux는 `python examples/06_keyboard_gui.py`를 사용합니다.
Motion Controls 창에 포커스를 두고 W/S/Q/E 이동, 키를 놓았을 때 정지, 창 닫기를 확인합니다.
