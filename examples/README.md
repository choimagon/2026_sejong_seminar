# 실습 실행 명령

번호 파일에는 상단 `if`·`import`·`from` 제공 코드만 있습니다. **PPT를 보고 아래 실습 코드를 채운 뒤 실행하세요.** 작성 전에는 실행해도 창이 뜨지 않습니다.

프로젝트 폴더에서 `seminar_mujoco` 환경을 켠 뒤 실행하세요.
[설치·환경 활성화](../README.md)

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

> **키로 운전하기 전, Motion Controls / Sensor Monitor 창의 Controls 탭을 클릭하세요.**
> MuJoCo 3D 창에서는 MuJoCo 단축키가 작동합니다. 카메라 조작 후 Controls 탭을 다시 클릭하세요.

02번은 중앙 기둥 통로 하나에서 운전합니다. `pressed("w")`의 문자를 바꾸면 조작 키가 바뀝니다.
예: `w`→`i`, `s`→`k`, `q`→`j`, `e`→`l`. 저장 후 창을 닫고 다시 실행하세요.

[코드 작성·센서 출력·XML 참고 설명](../docs/practice_reference.md)
