"""Prepared XML scenes; sensor model and route are selected by the numbered file."""
if __package__ in (None, ""):
    import _bootstrap

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
from module.models import resolve_xml

SCENES = Path(__file__).resolve().parent / "scenes"
MAPS = ("pillar", "straight", "left_corner", "right_corner", "obstacle", "maze")
MODELS = ("basic", "sonic", "lidar", "all")


def build_world(name="pillar", kind="all"):
    """Instructor preparation only. Students use the saved XML files."""
    if name not in MAPS or kind not in MODELS:
        raise ValueError("Unknown route or model")
    SCENES.mkdir(exist_ok=True)
    path = SCENES / f"{name}_{kind}.xml"
    if name == "maze":
        from module.course import random_maze
        prepared = random_maze(kind, seed=7, width=3, height=3, cell_size=.8)
        maze = ET.parse(prepared.path)
        for label in ("start", "goal"):
            marker = maze.getroot().find(f"worldbody/site[@name='course_{label}']")
            marker.set("type", "box")
            marker.set("size", ".12 .12 .002")
        ET.indent(maze)
        maze.write(path, encoding="utf-8", xml_declaration=True)
        return path
    if name != "pillar":
        root = ET.parse(resolve_xml(kind)).getroot()
        root.set("model", f"examples_{name}_{kind}")
        body = root.find("worldbody")
        floor = body.find("geom[@name='floor']")
        floor.set("rgba", ".48 .52 .56 1")
        robot = body.find("body[@name='base']")
        ET.SubElement(robot, "geom", name="course_chassis_collision", type="box",
                      pos="0 0 .10", size=".068 .064 .045", rgba="0 0 0 0")
        half, start_x, turn_x, end_y = (.7 if name == "obstacle" else .45), -.55, 2.8, 1.8
        def wall(label, x1, y1, x2, y2):
            ET.SubElement(body, "geom", name=f"course_wall_{label}", type="box",
                          pos=f"{(x1+x2)/2} {(y1+y2)/2} .16",
                          size=f"{abs(x2-x1)/2+.02} {abs(y2-y1)/2+.02} .16",
                          rgba=".25 .34 .43 1")
        if name in ("straight", "obstacle"):
            end_x = 4.05
            wall("lower",start_x,-half,end_x,-half)
            wall("upper",start_x,half,end_x,half)
            wall("start",start_x,-half,start_x,half)
            wall("end",end_x,-half,end_x,half)
            goal=(3.5,0)
            center=(1.75,0);extent=2.5
            segments=[(0,0,3.5,0)]
            if name == "obstacle":
                ET.SubElement(body,"geom",name="workshop_pillar",type="cylinder",
                              pos="1.75 0 .22",size=".14 .22",rgba=".72 .51 .24 1")
        else:
            sign=1 if name=="left_corner" else -1
            def mirrored(label,x1,y1,x2,y2):wall(label,x1,sign*y1,x2,sign*y2)
            mirrored("outer_lower",start_x,-half,turn_x+half,-half)
            mirrored("start",start_x,-half,start_x,half)
            mirrored("inner_upper",start_x,half,turn_x-half,half)
            mirrored("inner_side",turn_x-half,half,turn_x-half,end_y+half)
            mirrored("outer_side",turn_x+half,-half,turn_x+half,end_y+half)
            mirrored("end",turn_x-half,end_y+half,turn_x+half,end_y+half)
            goal=(turn_x,sign*end_y)
            center=(1.35,sign*.9);extent=2.4
            segments=[(0,0,turn_x,0),(turn_x,0,turn_x,sign*end_y)]
        # A subtle dashed lane guide is part of the real rendered XML, not a slide drawing.
        import math
        for section,(x1,y1,x2,y2) in enumerate(segments):
            length=math.hypot(x2-x1,y2-y1)
            for i in range(int(length/.28)):
                ratio=(i+.5)*.28/length
                x,y=x1+(x2-x1)*ratio,y1+(y2-y1)*ratio
                if name == "obstacle" and abs(x-1.75) < .3:continue
                size=".065 .012 .001" if x1!=x2 else ".012 .065 .001"
                ET.SubElement(body,"geom",name=f"lane_{section}_{i}",type="box",
                              pos=f"{x} {y} .002",size=size,rgba=".64 .68 .72 1",
                              contype="0",conaffinity="0")
        for label,(x,y),rgba in [("start",(0,0),".18 .42 .67 .6"),("goal",goal,".2 .6 .4 .6")]:
            ET.SubElement(body,"site",name=f"course_{label}",type="box",
                          pos=f"{x} {y} .004",size=".12 .12 .002",rgba=rgba)
        statistic=root.find("statistic")
        if statistic is None:statistic=ET.SubElement(root,"statistic")
        statistic.set("center",f"{center[0]} {center[1]} .1")
        statistic.set("extent",str(extent))
        ET.indent(root)
        ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)
        return path
    root = ET.parse(resolve_xml(kind)).getroot()
    root.set("model", f"examples_pillar_{kind}")
    body = root.find("worldbody")
    robot = body.find("body[@name='base']")
    ET.SubElement(robot, "geom", name="workshop_chassis", type="box",
                  pos="0 0 0.10", size="0.068 0.064 0.045", rgba="0 0 0 0")
    for label, x, y, sx, sy in [("west", -.6, 0, .025, 1.5), ("east", 2.8, 0, .025, 1.5),
                                ("north", 1.1, 1.5, 1.7, .025), ("south", 1.1, -1.5, 1.7, .025)]:
        ET.SubElement(body, "geom", name=f"workshop_wall_{label}", type="box",
                      pos=f"{x} {y} .2", size=f"{sx} {sy} .2", rgba=".4 .5 .6 1")
    ET.SubElement(body, "geom", name="workshop_pillar", type="cylinder",
                  pos="1.1 0 .22", size=".14 .22", rgba=".95 .5 .12 1")
    for label, x, rgba in [("start", 0, ".1 .4 .95 .6"), ("goal", 2.2, ".1 .8 .3 .6")]:
        ET.SubElement(body, "site", name=f"workshop_{label}", type="cylinder",
                      pos=f"{x} 0 .003", size=".28 .003", rgba=rgba)
    statistic = root.find("statistic")
    if statistic is None:statistic = ET.SubElement(root, "statistic")
    statistic.set("center", "1.1 0 .1");statistic.set("extent", "2.2")
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def world(name="pillar", kind="all"):
    if name not in MAPS or kind not in MODELS:raise ValueError("Unknown route or model")
    path = SCENES / f"{name}_{kind}.xml"
    if not path.is_file():raise FileNotFoundError(f"Prepared XML not found: {path}")
    return path


if __name__ == "__main__":
    for name in MAPS:
        for kind in MODELS:print(build_world(name, kind))
