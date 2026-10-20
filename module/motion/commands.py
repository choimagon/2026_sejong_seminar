"""Command descriptions only; use module.motion.forward(robot, metres) to execute."""

from dataclasses import asdict, dataclass
import math

FORWARD_SPEED = 0.35
TURN_SPEED = 2.0


@dataclass(frozen=True)
class MotionCommand:
    kind: str
    amount: float
    speed: float

    def __post_init__(self):
        if self.kind not in ("forward", "backward", "rotate"):
            raise ValueError("Use forward, backward, or rotate")
        if not math.isfinite(self.amount) or not math.isfinite(self.speed) or self.speed <= 0:
            raise ValueError("Amount must be finite and speed must be positive")
        if self.kind != "rotate" and self.amount < 0:
            raise ValueError("Distance must be nonnegative; use backward() to reverse")

    def to_dict(self):
        return asdict(self)



def forward(metres, speed=FORWARD_SPEED):
    """Create a command to travel forward by metres, at up to speed m/s."""
    return MotionCommand("forward", float(metres), float(speed))



def backward(metres, speed=FORWARD_SPEED):
    """Create a command to travel backward by metres, at up to speed m/s."""
    return MotionCommand("backward", float(metres), float(speed))



def rotate(degrees, speed=TURN_SPEED):
    """Create a signed-degree turn: +left / -right; speed is in rad/s."""
    return MotionCommand("rotate", float(degrees), float(speed))



def parse_command(text):
    """Parse 'forward 0.3', 'backward 0.2', or 'rotate -90'."""
    parts = text.strip().split()
    if len(parts) not in (2, 3):
        raise ValueError("Use: forward <m>, backward <m>, or rotate <degrees>")
    name = parts[0].lower()
    if name not in ("forward", "backward", "rotate"):
        raise ValueError("Unknown command; use forward, backward, or rotate")
    expected_unit = "deg" if name == "rotate" else "m"
    if len(parts) == 3 and parts[2].lower() != expected_unit:
        raise ValueError(f"The unit for {name} is {expected_unit}")
    try:
        amount = float(parts[1])
    except ValueError as error:
        raise ValueError("Enter a numeric distance or angle") from error
    return {"forward": forward, "backward": backward, "rotate": rotate}[name](amount)



def normalize_commands(commands):
    """Accept command objects or command strings for view(commands=[...])."""
    result = []
    for command in commands or ():
        if isinstance(command, str):
            command = parse_command(command)
        if not isinstance(command, MotionCommand):
            raise TypeError("commands must contain MotionCommand objects or command strings")
        result.append(command)
    return result

