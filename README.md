# MuJoCo 로봇 시뮬레이터 실습

기초 Python으로 이동 함수를 만들고 직접 운전한 뒤 초음파·라이다로 주행을 판단합니다.
01번은 move 함수 만들기 연습이며, 뒤 실습은 기존 공용 구현을 `from module.move import move`로 사용합니다.
번호 파일은 다른 실습에서 import하지 않고 직접 실행합니다.
새 실습 코드는 **`examples/`**에 있습니다. [번호별 실행·XML 안내](examples/README.md)를 따라 진행하세요.
이전 16개 실습은 로컬 `examples_legacy/`에 보존하고 `.gitignore`로 제외했습니다.

## 클론·설치·환경 활성화

Git과 Python 3.12를 먼저 설치하고 터미널에서 실행합니다.

```bash
git clone https://github.com/choimagon/2026_sejong_seminar.git
cd 2026_sejong_seminar
```

Windows PowerShell에서 최초 한 번 환경을 만들고 설치합니다.

```powershell
py -3.12 -m venv seminar_mujoco
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\seminar_mujoco\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python show.py
```

새 PowerShell 창에서는 환경 생성·설치를 반복하지 않고 다음 순서로 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\seminar_mujoco\Scripts\Activate.ps1
python show.py
```

실행 정책은 현재 PowerShell 창에만 적용됩니다.

Mac에서 최초 설치합니다.

```bash
python3.12 -m venv seminar_mujoco
source seminar_mujoco/bin/activate
python -m pip install -r requirements.txt
python show.py
```

새 Mac 터미널은 `source seminar_mujoco/bin/activate`로 환경을 켭니다.
`show.py`는 자체 MuJoCo 창을 여는 도구이므로 Mac도 `python show.py`입니다.
Windows/Linux는 모두 `python`으로 실행합니다. Mac은 01·03·04·07~10은 `mjpython`, 02·05·06·11은 `python`입니다. 아래 번호별 표의 명령을 따르세요.
Linux는 Mac처럼 환경을 활성화한 뒤 모든 실습을 `python`으로 실행합니다.
`(seminar_mujoco)` 표시를 확인하고 프로젝트 루트에서 파일 경로로 실행하세요. `-m`은 필요 없습니다.

## 먼저 실행

```powershell
# Windows / Linux
python examples/01_move.py
python examples/02_keyboard.py
python examples/05_ultrasonic.py
python examples/07_ultrasonic_route.py
```

```bash
# Mac
mjpython examples/01_move.py
python examples/02_keyboard.py
python examples/05_ultrasonic.py
mjpython examples/07_ultrasonic_route.py
```

## 실습 파일과 XML

센서와 경로는 실행 옵션 대신 **서로 다른 번호 파일**로 선택합니다.
각 파일의 `XML = SCENES / "...xml"`에 실제 불러올 장면을 명시했습니다.

| 파일 | 내용 | 실제 XML (`examples/scenes/`) |
| --- | --- | --- |
| [01_move.py](examples/01_move.py) | move 함수와 전진·후진·회전·정지 | `pillar_basic.xml` |
| [02_keyboard.py](examples/02_keyboard.py) | 중앙 기둥 통로 운전·조작 키 직접 변경 | `obstacle_basic.xml` |
| [03_route_left.py](examples/03_route_left.py) | 시간으로 넓은 방 기둥 왼쪽 우회 | `pillar_basic.xml` |
| [04_route_right.py](examples/04_route_right.py) | 시간으로 넓은 방 기둥 오른쪽 우회 | `pillar_basic.xml` |
| [05_ultrasonic.py](examples/05_ultrasonic.py) | 초음파 배열 출력과 GUI 관찰 | `pillar_sonic.xml` |
| [06_lidar.py](examples/06_lidar.py) | 라이다 딕셔너리·거리/좌표 배열과 GUI 관찰 | `pillar_lidar.xml` |
| [07_ultrasonic_route.py](examples/07_ultrasonic_route.py) | 초음파 거리로 판단하며 우회 | `pillar_sonic.xml` |
| [08_lidar_route.py](examples/08_lidar_route.py) | 라이다 거리로 판단하며 우회 | `pillar_lidar.xml` |
| [09_ultrasonic_mapping.py](examples/09_ultrasonic_mapping.py) | 초음파 측정점 누적 지도 | `pillar_sonic.xml` |
| [10_lidar_mapping.py](examples/10_lidar_mapping.py) | 라이다 측정점 누적 지도 | `pillar_lidar.xml` |
| [11_maze.py](examples/11_maze.py) | 라이다로 작은 미로 탐색 | `라이다 모델로 생성한 미로 XML` |

`basic`은 IMU·엔코더, `sonic`은 basic+초음파, `lidar`는 basic+라이다입니다.
05·07·09는 초음파 XML을, 06·08·10은 라이다 XML을 사용합니다.
02번은 중앙 기둥이 있는 통로 하나에서 운전합니다. `pressed("w")`의 문자를 바꾸면 조작 키가 바뀝니다.
01·03·04와 센서 실습은 벽 네 개와 반지름 14cm 기둥이 있는 방을 사용합니다.
번호 파일에는 `args`나 실행 옵션이 없습니다. 저장한 뒤 파일을 바로 실행합니다.

키 연결과 센서 반환 배열의 자세한 설명은 [실습 안내](examples/README.md)를 참고하세요.

## 조작 방법

`show.py` 실행 후 실제 3D 창에서 카메라를 먼저 조작해 봅니다.
왼쪽 드래그는 회전, 오른쪽 드래그는 시점 이동, Shift+오른쪽 드래그는 수평 이동, 휠은 확대·축소입니다.
`show.py`에는 별도 Motion Controls 창이 뜨지 않습니다.

02·05·06에서는 **Motion Controls / Sensor Monitor의 Controls 탭을 클릭한 뒤** W/S로 전후진, Q/E로 회전합니다.
키를 놓거나 다른 창으로 포커스를 옮기면 정지합니다. 3D 창에서 카메라를 조작했다면 GUI를 다시 클릭합니다.
F는 로봇 추적/전체 보기 전환, H는 전체 보기입니다.

## 구성과 검증

- `examples/`: 01–11 실습, 제공 실행기, 센서별 정적 XML
- `module/`: 공용 로봇·센서·GUI·제어 라이브러리
- `model_xml/`: 원본 basic / sonic / lidar / all 모델
- `docs/`: 함수·그래프·수업 진행 안내
- `tests/`: 파일 실행, 실제 XML 센서 구성, 경로·미로 검증
- `outputs/`: 주행 결과와 지도 저장 위치 (Git 제외)

```bash
python -m unittest discover -s tests -v
```

Windows 파이프 전달 오류 수정과 Mac/Linux 실행 방식을 공통 GUI 실행기에 반영했습니다.
GitHub Actions는 Windows·Mac·Linux에서 화면 없는 테스트를 실행합니다. 실제 GUI 검증은 데스크톱에서 별도로 진행합니다.
