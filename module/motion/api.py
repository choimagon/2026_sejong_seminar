"""Execute movement on an existing Robot, without sensor reads or windows."""

import math

from . import commands
from .speed import angular_speed, validate_motor_speed


def set_speed(robot, metres_per_second):
    """Set actual motor speed for primitives and distance/turn commands.

    The simulator clock is unchanged. Existing queued commands scale with the
    setting; explicit drive(linear=..., angular=...) keeps its requested units.
    """
    robot._check_open()
    speed = validate_motor_speed(metres_per_second)
    ratio = speed / robot.motor_speed
    robot._motor_speed = speed
    controller = robot._controller
    if controller is not None:
        def scaled(command):
            return commands.MotionCommand(command.kind, command.amount, command.speed * ratio)
        if controller.active is not None:
            controller.active["command"] = scaled(controller.active["command"])
        controller.queue = type(controller.queue)(scaled(command) for command in controller.queue)
    if robot._wheel_controller is not None:
        robot._wheel_controller.scale_speed(ratio)
    return speed


class MotionError(RuntimeError):
    """A blocked or timed-out command, including the controller's result."""

    def __init__(self, result):
        self.result = result
        super().__init__(result["message"])


def execute(robot, command, *, wait=True):
    """Execute a command object or text such as 'rotate -90'.

    By default, advance physics until completion and return the result dict.
    wait=False queues the command and returns its description; call
    robot.step(), robot.run_for(), or motion.wait(robot) to advance it.
    Distances are metres; positive angles turn left, negative angles right.
    """
    if isinstance(command, str):
        command = commands.parse_command(command)
        speed = angular_speed(robot.motor_speed) if command.kind == "rotate" else robot.motor_speed
        command = commands.MotionCommand(command.kind, command.amount, speed)
    if not isinstance(command, commands.MotionCommand):
        raise TypeError("Expected a motion.commands command or command string")
    robot._enable_motion()
    robot._manual = (0.0, 0.0)
    robot._controller.enqueue(command)
    if wait:
        return wait_until_done(robot)
    return command


def wait_until_done(robot):
    """Advance physics through the queue; raise MotionError on failure."""
    robot._check_open()
    if robot._mode == "wheels":
        from .wheels import wait
        return wait(robot)
    if robot._controller is None:
        return status(robot)
    while robot._controller.active is not None or robot._controller.queue:
        robot.step()
    result = status(robot)
    if result["state"] in ("failed", "cancelled"):
        raise MotionError(result)
    return result


def forward(robot, metres, speed=None, *, wait=True):
    """Drive forward by metres using motor torque; block by default."""
    return execute(robot, commands.forward(metres, robot.motor_speed if speed is None else speed), wait=wait)


def backward(robot, metres, speed=None, *, wait=True):
    """Drive backward by metres using motor torque; block by default."""
    return execute(robot, commands.backward(metres, robot.motor_speed if speed is None else speed), wait=wait)


def rotate(robot, degrees, speed=None, *, wait=True):
    """Rotate by signed degrees (+left / -right); block by default."""
    return execute(robot, commands.rotate(degrees, angular_speed(robot.motor_speed) if speed is None else speed), wait=wait)


def drive(robot, linear=0.0, angular=0.0):
    """Set chassis velocity targets: m/s forward and rad/s counterclockwise.

    Cancels the command queue. Then advance time with robot.step/run_for.
    Acceleration and torque limits mean the target may not be reached.
    """
    linear, angular = float(linear), float(angular)
    if not math.isfinite(linear) or not math.isfinite(angular):
        raise ValueError("linear and angular must be finite")
    robot._enable_motion()
    robot._controller.cancel("Velocity control")
    robot._manual = (linear, angular)


def stop(robot):
    """Clear the queue and target zero speed; step physics to brake to rest."""
    robot._enable_motion()
    robot._controller.cancel("Stop requested")
    robot._manual = (0.0, 0.0)
    robot.data.ctrl[robot._driver.motors] = 0


def status(robot):
    """Return task state and progress without advancing physics."""
    robot._check_open()
    if robot._mode == "wheels":
        from .wheels import status as wheel_status
        return wheel_status(robot)
    if robot._controller is None:
        return {"state": "idle", "pending": 0, "message": "Ready"}
    return robot._controller.status()
