"""Wall-clock playback rate; physics timestep and motor settings stay fixed."""

import math

SPEEDS = (1.0, 2.0, 4.0, 8.0)


def validate_speed(value):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("playback_speed must be finite and positive")
    return value


def ask_speed():
    """Ask for a multiplier without selecting a default for the user."""
    while True:
        try:
            return validate_speed(input("미로 재생 배속 입력 (양수, 1=실시간, 소수 가능): "))
        except (ValueError, TypeError):
            print("0보다 큰 유한한 숫자를 입력하세요.", flush=True)


def next_speed(current, direction=1, *, wrap=False):
    current = validate_speed(current)
    if direction > 0:
        return next((speed for speed in SPEEDS if speed > current), SPEEDS[0] if wrap else current*2)
    return next((speed for speed in reversed(SPEEDS) if speed < current), current/2)
