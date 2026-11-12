# 센서와 수동 지도 실습 참고

실행 명령은 [README](../README.md)의 Windows/Mac 표를 따릅니다.
01번 이후에는 기존 `from module.move import move`를 사용합니다.

## 03: ACTIONS 배열로 직선 주행 연습

PPT의 가리지 않은 예제를 보고 `03_route_straight.py`를 작성합니다. 기둥이 없는 `straight_basic.xml` 코스를 사용합니다.

각 행은 **(선속도, 각속도, 유지 시간)**입니다. 단위는 차례로 **m/s, rad/s, s**입니다.

| 자리 | 넣는 값 | 뜻 |
| --- | --- | --- |
| 첫 번째 | 양수 / 0 / 음수 | 전진 / 정지 / 후진 속도 |
| 두 번째 | 0 / 양수 / 음수 | 직진 / 왼쪽 회전 / 오른쪽 회전 속도 |
| 세 번째 | 0보다 큰 초 | 해당 속도를 유지하는 시간 |

`(0.25, 0.0, 6.0)`은 초속 0.25m로 회전 없이 6초 전진, `(0.0, 0.0, 1.0)`은 1초 정지입니다.
`for linear, angular, seconds in ACTIONS:`가 위에서부터 한 행씩 꺼내 `lab.run_for(...)`로 실행합니다.
직진 거리는 속도×시간으로 대략 예상할 수 있지만 실제로는 가속·마찰 때문에 차이가 납니다.
03번 배열은 PPT에 전부 공개하며, 다음 04·05번 기둥 우회 과제의 숫자만 가려둡니다.

## 초음파: 송신부 + 수신부 = 센서 모듈 하나

HC-SR04 앞의 둥근 두 부품은 송신부(TX)와 수신부(RX)입니다. 왼쪽·오른쪽 거리 센서 두 개가 아닙니다.
Trig에 10µs 이상의 신호를 주면 초음파를 내보내고 반사파를 받습니다. Echo 펄스 폭으로 왕복 시간을 측정합니다.

```text
송신부 ───── 초음파 ─────> 물체
수신부 <──── 반사파 ────── 물체

거리 = 음속 × 왕복 시간 ÷ 2
```

예를 들어 음속을 340m/s로 두면 왕복 약 5.88ms는 약 1m입니다.
실제 아두이노에서는 Echo 시간을 읽어 거리를 계산합니다. 이 실습의 Python API는 이미 계산된 미터 단위 거리 하나를 반환합니다.
[HC-SR04 데이터시트](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)

```python
distance = sensor.ultrasonic.read(robot)
print(distance)       # 예: 0.886, 단위 m
print(type(distance)) # float
```

XML에는 중앙 전방을 보는 rangefinder **하나**가 있습니다. 원형 부품 두 개는 한 모듈의 송신·수신 외형입니다.
시뮬레이터는 이상적인 단일 광선으로 거리를 읽습니다. 실제 음파의 퍼짐·왕복 지연·잡음·재질별 반사는 재현하지 않습니다.
기본 최대 거리는 4m이며, 범위 안에 반사점이 없으면 `inf`입니다. XML에 센서가 없으면 읽기 오류입니다.
[MuJoCo rangefinder 설명](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder)

## 라이다: 각도마다 거리 하나

기본 한 스캔에는 360개 방향의 거리값이 들어 있습니다. 센서 기준 X는 전방, Y는 왼쪽입니다.

| 배열 | 기본 크기 | 뜻 |
| --- | --- | --- |
| `angles_rad` | `(360,)` | 각 광선의 상대 각도(rad) |
| `ranges_m` | `(360,)` | 같은 인덱스 광선의 거리(m) |
| `points_xy_m` | `(360, 2)` | 같은 인덱스 측정점의 센서 기준 `[x, y]`(m) |

기본 360개 광선에서는 0번=전방, 90번=왼쪽, 180번=뒤, 270번=오른쪽입니다.
각도는 rad이며 마지막 인덱스 359는 359°입니다. 360°를 중복으로 넣지 않습니다.

```python
scan = sensor.lidar.read(robot)
angle = scan["angles_rad"][90]  # 약 1.571 rad = 90°
distance = scan["ranges_m"][90]
point = scan["points_xy_m"][90]
```

`point = distance × [cos(angle), sin(angle)]`입니다.
기본 최대 거리는 5m입니다. 미반사는 거리 `inf`, 좌표 `[NaN, NaN]`, 물체 번호 `-1`입니다.
나머지 `origin_world_m (3,)`, `directions_world (360,3)`, `geom_ids (360,)`는 부가 검증 정보입니다.
이 실제 세계 좌표·물체 번호를 지도나 주행의 정답으로 사용하지 않습니다.

## 10·11: 내가 운전하면 지도가 누적됩니다

자동으로 정해진 경로를 달리는 실습이 아닙니다. 두 파일 모두 **Windows와 Mac에서 `python`**으로 실행합니다.

```bash
python examples/10_ultrasonic_mapping.py
python examples/11_lidar_mapping.py
```

1. 직접 만든 Motion Controls / Sensor Monitor의 **Controls 탭을 먼저 클릭**합니다. MuJoCo 창에서는 MuJoCo 단축키가 작동합니다.
2. W/S로 전후진, Q/E로 회전합니다. 키를 놓거나 다른 창을 선택하면 정지합니다.
3. **M 또는 Map 탭**으로 누적 지도를 봅니다. Map 탭에서도 같은 GUI에 포커스가 있으면 WSQE 운전이 됩니다.
4. **P 또는 Save Map**으로 저장합니다. **R 또는 Reset**은 로봇과 지도를 함께 초기화합니다. 창을 닫아도 저장합니다.

초음파는 읽을 때마다 전방 측정점 하나를, 라이다는 한 스캔의 유효한 방향들을 추가합니다.
초음파로 방 둘레를 보려면 차체를 회전하거나 이동해 여러 방향을 측정해야 합니다.
같은 위치를 계속 읽으면 점이 겹칠 수 있습니다. 로봇 이동 경로와 장애물 측정점은 별개입니다.

## 거리에서 누적 지도 좌표로

엔코더·IMU로 추정한 로봇 자세에서 센서 장착 위치를 보정한 `x, y, yaw`를 제공합니다.
여기서 x/y는 **추정 센서 원점**, yaw는 **센서 전방 방향(rad)**입니다. 실제 시뮬레이터 위치를 가져온 값이 아닙니다.

```python
# 초음파: 센서 전방 한 방향
direction = yaw
point_x = x + distance * cos(direction)
point_y = y + distance * sin(direction)
points.append((point_x, point_y))

# 라이다: 각 광선의 상대 각도를 더함
direction = yaw + angle
point_x = x + distance * cos(direction)
point_y = y + distance * sin(direction)
points.append((point_x, point_y))
```

`isfinite(distance)`로 `inf`를 제외합니다. 초음파는 한 번 append하고, 라이다는 각도·거리를 `zip(...)`으로 묶어 반복합니다.
Map의 측정점은 초록색, 엔코더·IMU 이동 경로는 밝은 선, 현재 로봇 위치는 작은 십자입니다.
센서 측정점과 추정 자세를 계속 누적하므로 오차가 쌓일 수 있습니다. 점 지도이며 SLAM·루프 폐쇄·완성된 점유 격자는 구현하지 않습니다.

저장 파일은 `outputs/examples/ultrasonic_map.png/.npz`, `lidar_map.png/.npz`입니다.
PNG는 그림, NPZ는 측정점 배열과 추정 이동 경로입니다. 실시간 창은 원본 점을 간추려 표시하고 저장에는 누적된 원본 점을 사용합니다.

## 12·13: 센서 읽기 → if 판단 → 이동 반복

12번은 `maze_sonic.xml`, 13번은 같은 모양의 `maze_lidar.xml`을 사용합니다. 0.6m보다 멀리 측정되면 통로가 열린 것으로 판단합니다. 이동은 기존 `move(robot, linear, angular, seconds)`를 직접 호출합니다.
학생이 while·if문을 직접 작성해 **오른쪽 → 전방 → 왼쪽 → 뒤쪽** 순서로 통로를 찾습니다.

- **초음파:** 한 방향 거리만 읽으므로 차체를 오른쪽으로 돌린 뒤 읽습니다. 막혔으면 왼쪽으로 90° 돌려 다음 방향을 다시 읽고, 열렸으면 move로 전진하고 정지한 뒤 다시 측정합니다.
- **라이다:** 스캔의 `ranges_m[0]`은 전방, `[270]`은 오른쪽, `[90]`은 왼쪽입니다. if/elif/else로 방향을 선택하고 move로 회전합니다. 정지 후 전방을 다시 읽어 열렸으면 move로 전진합니다. `pass`는 현재 방향을 유지한다는 뜻입니다.
- `move(lab.robot, 0.25, 0.0, 3.3)`은 전진, `move(lab.robot, 0.0, 1.0, 1.9)`은 좌회전, 각속도 `-1.0`은 우회전입니다.
- 네 번째 값은 실행 시간(s)입니다. `move(lab.robot, 0.0, 0.0, 0.5)`는 정지를 지정하고 0.5초 동안 감속·정지 상태를 진행합니다. 별도 대기 함수는 호출하지 않습니다.
- 실행 시간을 생략한 기존 `move(robot, linear, angular)`는 속도만 지정합니다. 1번에서 작성하는 함수에도 선택적인 `seconds`와 시간 진행 두 줄을 포함합니다.
- `TURN_TIME=1.9`, `DRIVE_TIME=3.3`은 현재 모델에서 약 90° 회전·약 0.8m 전진하는 예시 시간입니다. 속도·마찰·시간을 바꾸면 실제 이동도 달라집니다. 정지 후 센서를 다시 읽어 다음 이동을 결정합니다.
- `lab.finish()`는 도착했을 때 화면에 `SUCCESS! / Goal reached`를 2초간 표시하고, `finally`의 `lab.close()`로 자동 종료합니다. 도착 전에 창을 닫았으면 성공을 표시하지 않습니다.
- `lab.running()`은 창 상태·목표 도착·시간 제한만 확인합니다. 목표 영역은 종료 채점용이며, 통로 판단에는 센서 거리만 사용합니다.

별도 정책 클래스나 경로 탐색기를 실행하지 않습니다. 위 조건문이 로봇의 방향을 직접 선택합니다. 이 간단한 오른손 규칙은 제공된 연결된 미로의 벽을 따라가는 연습이며, 모든 미로에서 최단 경로를 찾는 방식은 아닙니다.
