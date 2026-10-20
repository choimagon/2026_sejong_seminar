"""XML selection and the optional sensor test environment."""

from pathlib import Path
import xml.etree.ElementTree as ET

import mujoco


def resolve_xml(xml_kind="all"):
    """Resolve built-in model names independently of the caller's directory."""
    text = str(xml_kind)
    kind = text.lower().removesuffix(".xml").removeprefix("model_")
    if kind in ("all", "basic", "lidar", "sonic"):
        path = Path(__file__).resolve().parent.parent / "model_xml" / f"model_{kind}.xml"
    else:
        path = Path(xml_kind).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"XML not found: {xml_kind!r}. Use all, basic, lidar, sonic, or an existing XML path.")
    return path


def load_sensor_scene(xml_kind="all", *, demo=True):
    """Load the selected XML and add a test area only to this runtime scene."""
    path = resolve_xml(xml_kind)
    root = ET.parse(path).getroot()
    if not demo:
        return mujoco.MjModel.from_xml_path(str(path))
    world = root.find("worldbody")
    obstacles = [
        ("wall_front", "2 0 0.25", "0.025 2 0.25"),
        ("wall_back", "-2 0 0.25", "0.025 2 0.25"),
        ("wall_left", "0 2 0.25", "2 0.025 0.25"),
        ("wall_right", "0 -2 0.25", "2 0.025 0.25"),
        ("front_box", "0.9 0.2 0.2", "0.12 0.3 0.2"),
        ("side_box", "-0.7 -0.8 0.25", "0.18 0.25 0.25"),
    ]
    for name, pos, size in obstacles:
        ET.SubElement(world, "geom", name=name, type="box", pos=pos, size=size,
                      rgba="0.52 0.62 0.73 1", friction="1 0.006 0.0001")
    return mujoco.MjModel.from_xml_string(ET.tostring(root, encoding="unicode"))

