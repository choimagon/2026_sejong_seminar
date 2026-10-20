"""Small teaching baselines. Students improve these decisions for unseen maps."""

from collections import deque

from . import actions
from .runtime import front_distance, sector


class LidarPolicy:
    """Left-hand exploration with short moves; no map, seed, or truth access."""

    def __init__(self):
        self.pending = deque()
        self.wait_for_left_wall = False

    def decide(self, observation):
        if self.pending:
            return self.pending.popleft()
        front = front_distance(observation)
        left = sector(observation.lidar, 90, 14)
        right = sector(observation.lidar, -90, 14)
        if left < 0.50:
            self.wait_for_left_wall = False
        if left > 0.60 and not self.wait_for_left_wall:
            self.wait_for_left_wall = True
            # Advance slightly past the side opening before turning.
            self.pending.extend([actions.left(), actions.forward(0.18)])
            return actions.forward(0.16) if front > 0.30 else self.pending.popleft()
        # Keep room for the next step and the chassis swept during a turn.
        if front > 0.35:
            return actions.forward(0.18)
        if right > 0.60:
            self.pending.append(actions.forward(0.18))
            return actions.right()
        return actions.left(180)


class SonicPolicy:
    """Physically turn to measure left/right, then restore the original heading."""

    def __init__(self):
        self.phase = "front"
        self.pending = deque()
        self.wait_for_left_wall = False

    def decide(self, observation):
        if self.pending:
            return self.pending.popleft()
        if observation.ultrasonic is None:
            raise ValueError("SonicPolicy requires the ultrasonic sensor")
        distance = float(min(observation.ultrasonic))
        if self.phase == "front":
            self.front = distance
            self.phase = "left"
            return actions.left()
        if self.phase == "left":
            self.left = distance
            self.phase = "right"
            return actions.right(180)
        if self.phase == "right":
            self.right = distance
            self.phase = "choose"
            return actions.left()
        self.phase = "front"
        if self.left < 0.50:
            self.wait_for_left_wall = False
        if self.left > 0.60 and not self.wait_for_left_wall:
            self.wait_for_left_wall = True
            self.pending.extend([actions.left(), actions.forward(0.18)])
            return actions.forward(0.16) if self.front > 0.30 else self.pending.popleft()
        if self.front > 0.35:
            return actions.forward(0.20)
        if self.right > 0.60:
            self.pending.append(actions.forward(0.18))
            return actions.right()
        return actions.left(180)
