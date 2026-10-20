"""Student actions: distances in metres and left/right turns in degrees."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Action:
    kind: str
    amount: float = 0.0
    radius: float = 0.0

    def __post_init__(self):
        if self.kind not in ("forward", "backward", "left", "right", "arc_left", "arc_right", "stop"):
            raise ValueError("Use forward, backward, left, right, arc_left, arc_right, or stop")
        if not math.isfinite(self.amount) or self.amount < 0:
            raise ValueError("Action amount must be finite and nonnegative")
        if not math.isfinite(self.radius) or self.radius < 0:
            raise ValueError("Radius must be finite and nonnegative")
        if self.kind.startswith("arc_") and self.radius <= 0:
            raise ValueError("An arc requires a positive radius in metres")


def forward(metres=0.1):
    return Action("forward", float(metres))


def backward(metres=0.1):
    return Action("backward", float(metres))


def left(degrees=90):
    return Action("left", float(degrees))


def right(degrees=90):
    return Action("right", float(degrees))


def arc(radius=0.26, degrees=90):
    """Forward curve: radius in m, positive degrees left / negative right."""
    degrees = float(degrees)
    return Action("arc_left" if degrees >= 0 else "arc_right", abs(degrees), float(radius))


def stop():
    return Action("stop")
