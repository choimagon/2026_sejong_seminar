# MuJoCo 로봇 실습

Git과 Python 3.12를 설치한 뒤, 아래 순서대로 실행하세요.

## Windows에서 `git` 또는 `py`가 안 될 때

`git` 명령이 없으면 Git을 설치합니다.

```powershell
winget install --id Git.Git -e --source winget
```

`py` 명령이 없으면 Python 3.12를 설치합니다.

```powershell
winget install --id Python.Python.3.12 -e --source winget
```

설치 후 **PowerShell을 닫고 새로 열어** 아래 순서로 진행하세요.

## 1. 다운로드

```bash
git clone https://github.com/choimagon/2026_sejong_seminar.git
cd 2026_sejong_seminar
```

## 2. 설치하고 화면 확인

### Windows — PowerShell

```powershell
py -3.12 -m venv seminar_mujoco
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\seminar_mujoco\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python show.py
```

### Mac — 터미널

```bash
python3.12 -m venv seminar_mujoco
source seminar_mujoco/bin/activate
python -m pip install -r requirements.txt
python show.py
```

## 3. 새 터미널에서 환경 켜기

프로젝트 폴더로 이동한 뒤 실행하세요. 설치는 반복하지 않습니다.

**Windows**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\seminar_mujoco\Scripts\Activate.ps1
```

**Mac**

```bash
source seminar_mujoco/bin/activate
```

## 4. 실습 실행

번호 파일에는 상단 `if`·`import`·`from` 제공 코드만 있습니다. **PPT를 보고 아래 실습 코드를 채운 뒤 실행하세요.** 작성 전에는 실행해도 창이 뜨지 않습니다.

프로젝트 폴더에서, 사용하는 운영체제 열의 명령을 실행하세요.

| 번호 | 실습 | Windows PowerShell | Mac 터미널 |
| --- | --- | --- | --- |
| 01 | move 함수 만들기 | `python examples/01_move.py` | `mjpython examples/01_move.py` |
| 02 | 키 연결·직접 운전 | `python examples/02_keyboard.py` | `python examples/02_keyboard.py` |
| 03 | ACTIONS 배열로 직선 주행 | `python examples/03_route_straight.py` | `mjpython examples/03_route_straight.py` |
| 04 | 기둥 왼쪽 우회 | `python examples/04_route_left.py` | `mjpython examples/04_route_left.py` |
| 05 | 기둥 오른쪽 우회 | `python examples/05_route_right.py` | `mjpython examples/05_route_right.py` |
| 06 | 초음파 출력 확인 | `python examples/06_ultrasonic.py` | `python examples/06_ultrasonic.py` |
| 07 | 라이다 출력 확인 | `python examples/07_lidar.py` | `python examples/07_lidar.py` |
| 08 | 초음파로 주행 판단 | `python examples/08_ultrasonic_route.py` | `mjpython examples/08_ultrasonic_route.py` |
| 09 | 라이다로 주행 판단 | `python examples/09_lidar_route.py` | `mjpython examples/09_lidar_route.py` |
| 10 | 직접 운전·초음파 지도 | `python examples/10_ultrasonic_mapping.py` | `python examples/10_ultrasonic_mapping.py` |
| 11 | 직접 운전·라이다 지도 | `python examples/11_lidar_mapping.py` | `python examples/11_lidar_mapping.py` |
| 12 | 초음파 if문 미로 주행 | `python examples/12_ultrasonic_maze.py` | `mjpython examples/12_ultrasonic_maze.py` |
| 13 | 라이다 if문 미로 주행 | `python examples/13_lidar_maze.py` | `mjpython examples/13_lidar_maze.py` |

## 키로 운전하기

> **직접 만든 Motion Controls / Sensor Monitor 창의 Controls 탭을 먼저 클릭하세요.**
> MuJoCo 3D 창이 선택되어 있으면 MuJoCo 단축키가 작동합니다. 카메라 조작 후에도 Controls 탭을 다시 클릭하세요.

- W: 전진 / S: 후진 / Q: 좌회전 / E: 우회전. 키를 놓으면 정지합니다.
- 02번의 `pressed("w")`에서 문자를 바꾸면 조작 키가 바뀝니다. 저장 후 다시 실행하세요.
- 10·11번은 직접 운전하며 지도를 만듭니다. **M: 지도 보기 / P: 저장 / R: 초기화**. 창을 닫아도 저장됩니다.

[실습 참고 설명](docs/practice_reference.md)
