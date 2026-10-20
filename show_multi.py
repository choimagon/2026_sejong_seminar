from pathlib import Path
import xml.etree.ElementTree as ET

import mujoco
import mujoco.viewer

folder = Path(__file__).resolve().parent / "model_xml"
scene = ET.parse(folder / "model_all.xml").getroot()
scene.set("model", "turtlebot_comparison")
world = scene.find("worldbody")
world.remove(world.find("body"))
actuators = scene.find("actuator")
sensors = scene.find("sensor")
actuators.clear()
sensors.clear()

for name, y in zip(("basic", "lidar", "sonic", "all"), (-0.48, -0.16, 0.16, 0.48)):
    robot = ET.parse(folder / f"model_{name}.xml").getroot()
    # Give each robot its own names and references in the shared scene.
    for element in robot.iter():
        for attribute in ("name", "joint", "site"):
            if attribute in element.attrib:
                element.set(attribute, f"{name}_{element.get(attribute)}")

    body = robot.find("worldbody/body")
    body.set("pos", f"0 {y} 0")
    world.append(body)
    actuators.extend(robot.find("actuator"))
    sensors.extend(robot.find("sensor"))

model = mujoco.MjModel.from_xml_string(ET.tostring(scene, encoding="unicode"))
data = mujoco.MjData(model)

model.stat.center[:] = (0.0, 0.0, 0.1)
model.stat.extent = 1.1
model.vis.global_.azimuth = 180
model.vis.global_.elevation = -30

mujoco.viewer.launch(model=model, data=data)
