# 원하는 데이터로 그래프 그리기

`from module import graph`로 가져옵니다. 센서를 읽고 시간을 진행하는 코드는 직접 작성하고,
모은 값 중 원하는 데이터를 그리기 함수에 넣습니다. 내부에서는 Matplotlib을 사용합니다.

## 한 그래프

이미 모은 `times`와 `distances`가 있을 때 다음처럼 그립니다.

```python
from module import graph

chart = graph.plot(times, distances, labels=["Left", "Right"],
                   xlabel="Time (s)", ylabel="Distance (m)")
chart.save("sensor_sampling/ultrasonic.png")
graph.show()
```

X는 1차원 배열이나 리스트입니다. Y는 아래 세 가지 방식으로 넣습니다.

| 입력 | 예 | 표시 |
| --- | --- | --- |
| 한 열 | `gyro[:, 2]` | 자이로 Z 한 선 |
| 여러 열 | `distances` | 열마다 한 선 |
| 이름과 배열 | `{"Left": distances[:, 0], "Right": distances[:, 1]}` | 이름이 자동으로 범례가 됨 |

Y의 표본 수는 X의 길이와 같아야 합니다. `labels`는 한 선이면 문자열, 여러 선이면 이름 목록입니다.
`inf`와 `NaN`은 빈 구간으로 표시하며 원본 배열은 바꾸지 않습니다.

## 여러 패널

```python
chart = graph.figure(rows=2, xlabel="Time (s)")
chart.plot(times, acceleration, labels=["X", "Y", "Z"], ylabel="m/s²")
chart.plot(times, gyro, labels=["X", "Y", "Z"], ylabel="rad/s")
chart.save("sensor_sampling/imu.png")
graph.show()
```

`rows`와 `cols`로 행·열 수를 고릅니다. `chart.plot`은 다음 빈 패널을 사용합니다.
`panel=1`처럼 번호를 지정하면 같은 패널에 선을 추가합니다. 번호는 1부터 시작합니다.

## 원하는 열과 모양

```python
chart = graph.plot(times, gyro[:, 2], labels="Gyro Z",
                   xlabel="Time (s)", ylabel="rad/s", color="red")
chart.plot(times, other_gyro, labels="Other", panel=1, style="--")
graph.show()
```

`title`, `xlabel`, `ylabel`, `labels`로 이름과 단위를 정합니다.
`style="."`는 점, `style="--"`는 점선입니다. `color`, `linewidth`, `alpha` 등 Matplotlib의 선 옵션도 전달할 수 있습니다.
전체 제목은 `graph.figure(title="My experiment")`로 지정합니다.

## 라이다도 같은 명령

```python
chart = graph.figure(cols=2)
chart.plot(times, distances, labels=["Front", "Left", "Right", "Back"],
           xlabel="Time (s)", ylabel="Distance (m)")
chart.plot(scan["angles_rad"], scan["ranges_m"], polar=True, style=".")
chart.save("sensor_sampling/lidar.png")
graph.show()
```

`polar=True`이면 X는 각도(rad), Y는 반지름입니다. 0도는 오른쪽이고 반시계 방향으로 증가합니다.
일반 좌표의 X·Y 축 비율을 같게 보려면 `equal=True`를 사용합니다.

## 저장과 표시

`chart.save("my_plot.png")`는 저장소의 `outputs/my_plot.png`에 저장합니다.
하위 폴더는 자동으로 만들고, 절대 경로를 넣으면 그 위치에 저장합니다.
확장자를 `.svg`나 `.pdf`로 바꾸어 저장할 수도 있습니다.
`graph.show()`는 만든 그래프 창을 엽니다. 센서 측정과 물리 진행은 수행하지 않습니다.

[설치·실습 안내](../README.md)
