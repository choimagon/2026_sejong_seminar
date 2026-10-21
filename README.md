# MuJoCo 로봇 시뮬레이터 실습

차동구동 로봇으로 이동 명령, 센서 측정, 그래프, 센서 기반 주행을 배우는 2시간 실습 자료입니다.
구동 바퀴 2개와 볼 캐스터를 사용하며 IMU·휠 엔코더·초음파·360도 2D 라이다를 다룹니다.

**`examples/`의 실습 파일 16개는 필요한 import만 들어 있는 학생 작성용 파일입니다.**
수업을 따라 실행 본문을 직접 작성합니다. 작성 전에는 실행해도 창이나 그래프가 뜨지 않고 종료됩니다.

## 폴더 구성

```text
.
├── README.md            설치·실행·배포 범위
├── requirements.txt     실행에 필요한 Python 패키지
├── .gitignore           가상환경·캐시·생성 결과 제외
├── examples/            01–16번 실습: import만 제공
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

Python **3.12** 환경에서 확인했습니다. 모든 명령은 이 README가 있는 폴더에서 실행합니다.
Python·MuJoCo만으로 실습하며 ROS·Isaac Sim 설치는 필요하지 않습니다.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

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
mjpython -m examples.01_move
mjpython -m examples.06_keyboard_gui
mjpython -m examples.08_lidar_straight
mjpython -m examples.16_maze_escape

# 센서 측정과 Matplotlib 실습
python -m examples.02_imu
python -m examples.03_encoders
python -m examples.04_ultrasonic
python -m examples.05_lidar
python -m examples.07_move_algorithm
```

Windows / Linux에서는 위의 `mjpython`을 `python`으로 바꿉니다.
`python examples/01_move.py` 대신 프로젝트 루트에서 `-m examples.01_move` 형식으로 실행합니다.
그래야 `module` 라이브러리를 같은 폴더에서 찾을 수 있습니다.

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
| import만 있는 실습 16개 | 완성 코드가 포함된 코드북 웹사이트 |
| 모델 확인·키보드·센서 GUI 도구 | PPT·PDF·발표 대본·동영상·미리보기 |
| README·실습 목표·함수 안내·설치 목록 | `.venv`·캐시·실행 결과·로컬 설정 |

프로젝트 전체를 올리는 대신 이 폴더의 파일만 사용합니다.
기존 강사용 완성 코드와 발표 자료는 원본 프로젝트에 보관되어 있습니다.
