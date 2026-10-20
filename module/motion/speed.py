"""Actual chassis speed presets shared by keyboard and motor controllers."""

import math

from .commands import FORWARD_SPEED, TURN_SPEED

MOTOR_SPEEDS = (0.10, 0.20, 0.35, 0.50)


def validate_motor_speed(value):
    value = float(value)
    if not math.isfinite(value) or not 0 < value <= MOTOR_SPEEDS[-1]:
        raise ValueError("motor_speed must be finite, positive, and at most 0.50 m/s")
    return value


def angular_speed(linear_speed):
    return TURN_SPEED * validate_motor_speed(linear_speed) / FORWARD_SPEED


def next_motor_speed(current, direction=1, *, wrap=False):
    current = validate_motor_speed(current)
    if direction > 0:
        return next((speed for speed in MOTOR_SPEEDS if speed > current), MOTOR_SPEEDS[0] if wrap else MOTOR_SPEEDS[-1])
    return next((speed for speed in reversed(MOTOR_SPEEDS) if speed < current), min(current, MOTOR_SPEEDS[0]))
