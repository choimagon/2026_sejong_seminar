"""Four walls, one pillar, and a visible goal; generated outside source files."""
from pathlib import Path
import xml.etree.ElementTree as ET

from module.models import resolve_xml

MAPS = {"pillar": (1.1, 0.0), "shifted": (1.35, 0.0), "offset": (1.1, -0.35)}


def world(name="pillar"):
    if name not in MAPS:
        raise ValueError(f"Choose one of {tuple(MAPS)}")
    root = ET.parse(resolve_xml("all")).getroot()
    root.set("model", f"workshop100_{name}")
    body = root.find("worldbody")
    robot = body.find("body[@name='base']")
    ET.SubElement(robot, "geom", name="workshop_chassis", type="box",
                  pos="0 0 0.10", size="0.068 0.064 0.045", rgba="0 0 0 0")
    for name_, x, y, sx, sy in [("west", -.6, 0, .025, 1.5), ("east", 2.8, 0, .025, 1.5),
                                ("north", 1.1, 1.5, 1.7, .025), ("south", 1.1, -1.5, 1.7, .025)]:
        ET.SubElement(body, "geom", name=f"workshop_wall_{name_}", type="box",
                      pos=f"{x} {y} .2", size=f"{sx} {sy} .2", rgba=".4 .5 .6 1")
    x, y = MAPS[name]
    ET.SubElement(body, "geom", name="workshop_pillar", type="cylinder",
                  pos=f"{x} {y} .22", size=".22 .22", rgba=".95 .5 .12 1")
    for label, x, rgba in [("start", 0, ".1 .4 .95 .6"), ("goal", 2.2, ".1 .8 .3 .6")]:
        ET.SubElement(body, "site", name=f"workshop_{label}", type="cylinder",
                      pos=f"{x} 0 .003", size=".28 .003", rgba=rgba)
    statistic = root.find("statistic")
    if statistic is None:
        statistic = ET.SubElement(root, "statistic")
    statistic.set("center", "1.1 0 .1")
    statistic.set("extent", "2.2")
    folder = Path(__file__).resolve().parents[1] / "outputs/workshop100"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.xml"
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path
