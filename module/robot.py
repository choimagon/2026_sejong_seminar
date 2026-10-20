"""One shared simulation state, with no GUI or sensor polling on import."""

import math
import operator
import time

import mujoco

from .models import load_sensor_scene


class Robot:
    """Load an XML without opening windows or starting background threads.

    xml_kind is all/basic/lidar/sonic or an XML path. demo=True adds the
    optional sensor test obstacles. The default uses the unmodified XML.
    step() advances physics; sensors read this same model/data pair.
    Context-manager use closes the robot even when an example raises.
    """

    def __init__(self, xml_kind="all", *, demo=False, motor_speed=None):
        from .motion.commands import FORWARD_SPEED
        from .motion.speed import validate_motor_speed
        self._motor_speed = validate_motor_speed(FORWARD_SPEED if motor_speed is None else motor_speed)
        self.model = load_sensor_scene(xml_kind, demo=demo)
        self.data = mujoco.MjData(self.model)
        self._controller = self._driver = None
        self._wheel_controller = None
        self._manual = (0.0, 0.0)
        self._mode = "idle"
        self._closed = False
        self._viewer = None
        mujoco.mj_forward(self.model, self.data)

    @property
    def motor_speed(self):
        """Selected chassis speed target, m/s; change with motion.set_speed()."""
        return self._motor_speed

    @property
    def time(self):
        """Elapsed simulation time in seconds."""
        return float(self.data.time)

    def _check_open(self):
        if self._closed:
            raise RuntimeError("Robot is closed; create a new Robot")

    def _ensure_drive(self):
        self._check_open()
        if self._controller is None:
            from .motion.controller import MotionController
            from .motion.motors import WheelDrive
            self._controller = MotionController(self.model)
            self._driver = WheelDrive(self.model)

    def _enable_motion(self):
        self._ensure_drive()
        if self._mode == "wheels":
            self._wheel_controller.cancel("Chassis control")
        self._mode = "velocity"

    def _enable_wheels(self):
        self._ensure_drive()
        if self._wheel_controller is None:
            from .motion.wheels import WheelController
            self._wheel_controller = WheelController(self.model)
        if self._mode != "wheels":
            self._controller.cancel("Wheel control")
        self._manual = (0.0, 0.0)
        self._mode = "wheels"

    def view(self):
        """Open this robot's native MuJoCo window; step/run_for display at 1x.

        The viewer shares this exact model and data. On macOS, run the
        calling script with mjpython. Closing the Robot closes its viewer.
        """
        self._check_open()
        if self._viewer is not None and self._viewer.is_running():
            return self._viewer
        from mujoco import viewer
        self._viewer = viewer.launch_passive(self.model, self.data)
        self._viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        self._viewer.cam.trackbodyid = self.model.body("base").id
        self._viewer.cam.distance = 1.1
        self._viewer.cam.azimuth = 135
        self._viewer.cam.elevation = -35
        self._viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_RANGEFINDER] = False
        self._viewer.sync()
        return self._viewer

    def step(self, steps=1):
        """Advance an integer number of physics steps; display at 1x if viewed.

        Chassis and wheel commands apply motor torque before each step. Direct
        torque mode preserves the torque set by motion.motors.set_torques().
        All sensor positions and readings are refreshed before returning.
        """
        self._check_open()
        if isinstance(steps, bool):
            raise ValueError("steps must be a nonnegative integer")
        try:
            count = operator.index(steps)
        except TypeError as error:
            raise ValueError("steps must be a nonnegative integer") from error
        if count < 0:
            raise ValueError("steps must be a nonnegative integer")
        deadline = time.perf_counter() if self._viewer is not None else 0
        for _ in range(count):
            if self._mode == "velocity":
                target = self._controller.update(self.data, self._manual)
                self._driver.apply(self.data, target)
            elif self._mode == "wheels":
                target = self._wheel_controller.update(self.data)
                self._driver.apply_wheels(self.data, target)
            mujoco.mj_step(self.model, self.data)
            if self._viewer is not None:
                if self._viewer.is_running():
                    self._viewer.sync()
                    deadline += self.model.opt.timestep
                    time.sleep(max(0, deadline - time.perf_counter()))
                else:
                    self._viewer.close()
                    self._viewer = None
        mujoco.mj_forward(self.model, self.data)

    def run_for(self, seconds):
        """Advance simulation seconds, rounded up to a whole physics step."""
        seconds = float(seconds)
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("seconds must be finite and nonnegative")
        self.step(math.ceil(seconds / self.model.opt.timestep))

    def reset(self):
        """Restore the XML pose, stop motors, and clear queued commands."""
        self._check_open()
        mujoco.mj_resetData(self.model, self.data)
        if self._controller is not None:
            self._controller.reset()
            self._driver.reset()
        if self._wheel_controller is not None:
            self._wheel_controller.reset()
        self._manual = (0.0, 0.0)
        mujoco.mj_forward(self.model, self.data)

    def close(self):
        """Release this session; safe to call more than once."""
        self.data.ctrl[:] = 0
        if self._controller is not None:
            self._controller.cancel("Robot closed")
        if self._wheel_controller is not None:
            self._wheel_controller.cancel("Robot closed")
        if self._viewer is not None:
            self._viewer.close()
            self._viewer = None
        self._closed = True

    def __enter__(self):
        self._check_open()
        return self

    def __exit__(self, *_exception):
        self.close()
