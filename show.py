import mujoco
import mujoco.viewer

model = mujoco.MjModel.from_xml_path("model_xml/model_all.xml")
data = mujoco.MjData(model)

model.stat.center[:] = (0.0, 0.0, 0.1)
model.stat.extent = 0.5
model.vis.global_.azimuth = 45
model.vis.global_.elevation = -25

mujoco.viewer.launch(model=model, data=data)
