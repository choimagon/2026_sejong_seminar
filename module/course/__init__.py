"""Seminar helpers: observe -> drive -> decide -> local random-maze practice."""

from .actions import Action, arc, backward, forward, left, right, stop
from .odometry import Estimate, Odometry
from .scenes import CASES, World, random_maze, scenario, square_maze
from .runtime import Observation, Session, front_distance, load_policy, run, sector
from .lab import practice


def view(world, *, policy=None, commands=None, max_sim_time=600, sensors=None, playback_speed=1.0,
         motor_speed=0.35, playback_controls=False):
    """Native MuJoCo + sensor monitor. policy is an import spec.

    Without policy, hold W/S/Q/E or use estimated-distance/turn commands.
    With policy, the same motor primitives run automatically; manual keys
    cancel automatic decisions. Reset starts the policy from scratch.
    motor_speed sets actual chassis speed in m/s; Motor and +/- change it live.
    playback_speed defaults to 1, keeping the simulator clock at real time.
    playback_controls enables the speed command and [/] playback shortcuts.
    max_sim_time=None runs without a time limit.
    """
    from ..viewer import view as open_monitor
    return open_monitor(world.path, demo=False, sensors=sensors, commands=commands,
                        course=True, policy=policy, max_sim_time=max_sim_time,
                        playback_speed=playback_speed, motor_speed=motor_speed,
                        playback_controls=playback_controls)


__all__ = ["Action", "forward", "backward", "left", "right", "arc", "stop", "Odometry",
           "Estimate", "Observation", "Session", "front_distance", "sector", "scenario",
           "random_maze", "square_maze", "run", "view", "practice", "load_policy", "World", "CASES"]
