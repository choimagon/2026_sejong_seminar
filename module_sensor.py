"""Compatibility entry point; reusable implementations live in module/.

import module_sensor
from module.motion.commands import forward, backward, rotate
module_sensor.view("all", commands=[forward(0.3), rotate(90), backward(0.2)])
"""

from module.models import load_sensor_scene, resolve_xml
from module.motion.commands import backward, forward, rotate
from module.sensor import (
    SENSOR_LABELS, available_sensors, read_encoders, read_imu, read_lidar,
    read_ultrasonic, sensor_snapshot,
)
from module.simulation import run_simulation, start_simulation
from module.sensor import view
from module.viewer import sensor_tab_at

__all__ = [
    "view", "forward", "backward", "rotate", "read_imu", "read_encoders",
    "read_ultrasonic", "read_lidar",
]


