"""Wheel velocity feedback and direct left/right motor torque access."""

import numpy as np

MAX_MOTOR_TORQUE = 0.24
MAX_DRIVE_EFFORT = 0.04
LINEAR_ACCELERATION = 0.40  # m/s^2
ANGULAR_ACCELERATION = 2.40  # rad/s^2


def set_torques(robot, left, right):
    """Set left/right motor torques in N m (the supplied XML uses gear=1).

    This bypasses velocity control and cancels queued movement. Values must
    fit each XML actuator's ctrlrange. Then call robot.step/run_for to move.
    """
    robot._check_open()
    values = np.array([left, right], dtype=float)
    ids = [robot.model.actuator(f"{side}_motor").id for side in ("left", "right")]
    limits = robot.model.actuator_ctrlrange[ids]
    limited = robot.model.actuator_ctrllimited[ids].astype(bool)
    if not np.isfinite(values).all() or np.any(limited & ((values < limits[:, 0]) | (values > limits[:, 1]))):
        raise ValueError("Torques must be finite and inside the XML motor ctrlrange")
    if robot._controller is not None:
        robot._controller.cancel("Direct motor torque control")
        robot._driver.reset()
    if robot._wheel_controller is not None:
        robot._wheel_controller.cancel("Direct motor torque control")
    robot._manual = (0.0, 0.0)
    robot._mode = "torque"
    robot.data.ctrl[ids] = values


def read_torques(robot):
    """Return a copy of applied left/right control torques in N m (gear=1)."""
    robot._check_open()
    ids = [robot.model.actuator(f"{side}_motor").id for side in ("left", "right")]
    return robot.data.ctrl[ids].copy()


class WheelDrive:
    """Convert chassis velocity into motor torques with wheel speed feedback."""

    def __init__(self, model):
        self.dt = float(model.opt.timestep)
        self.radius = float(model.geom("drive_left_tire").size[0])
        self.track = float(model.body("left_wheel").pos[1] - model.body("right_wheel").pos[1])
        self.dofs = [int(model.joint(f"{side}_wheel_joint").dofadr[0]) for side in ("left", "right")]
        self.motors = [model.actuator(f"{side}_motor").id for side in ("left", "right")]
        self.damping = model.dof_damping[self.dofs].copy()
        self.command = np.zeros(2)

    def reset(self):
        self.command[:] = 0

    def apply(self, data, target):
        """Translate chassis m/s and rad/s into the shared wheel drive."""
        self.apply_wheels(data, self.wheel_velocities(*target))

    def wheel_velocities(self, linear, angular):
        """Return left/right wheel rad/s for a chassis velocity."""
        return (linear + np.array([-1, 1]) * angular * self.track / 2) / self.radius

    def apply_wheels(self, data, target):
        """Track left/right wheel rad/s with the same acceleration limits."""
        left, right = target
        chassis = np.array([self.radius * (left + right) / 2,
                            self.radius * (right - left) / self.track])
        limits = np.array([LINEAR_ACCELERATION, ANGULAR_ACCELERATION]) * self.dt
        self.command += np.clip(chassis - self.command, -limits, limits)
        wheel_targets = self.wheel_velocities(*self.command)
        measured = data.qvel[self.dofs]
        # Compensate measured viscous damping. Limit the additional traction
        # torque so a stalled wheel cannot apply the full high-speed budget.
        effort = np.clip(0.04 * (wheel_targets - measured), -MAX_DRIVE_EFFORT, MAX_DRIVE_EFFORT)
        torques = self.damping * measured + effort
        data.ctrl[self.motors] = np.clip(torques, -MAX_MOTOR_TORQUE, MAX_MOTOR_TORQUE)

