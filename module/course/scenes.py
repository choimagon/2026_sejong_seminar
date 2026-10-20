"""Shared robot/clearance conditions for courses and seeded practice mazes."""

from dataclasses import dataclass
from pathlib import Path
import random
import secrets
import xml.etree.ElementTree as ET

from ..models import resolve_xml

OUTPUT = Path(__file__).resolve().parents[2] / "outputs"
CASES = ("straight", "corner", "junction", "cross")
GOAL_RADIUS_M = 0.25  # Provisional local goal zone, inside one 0.8 m cell.


@dataclass(frozen=True)
class World:
    path: Path
    name: str
    seed: int | None
    start: tuple
    goal: tuple
    cell_size: float
    openings: frozenset


def _edge(a, b):
    return tuple(sorted((a, b)))


def _build(name, kind, width, height, openings, start, goal, *, seed=None, cell_size=0.8,
           wall_thickness=0.04, goal_radius=GOAL_RADIUS_M, tiles=False, center_axle=False,
           merge_walls=False):
    root = ET.parse(resolve_xml(kind)).getroot()
    world = root.find("worldbody")
    robot = world.find("body[@name='base']")
    axle_offset = (sum(float(robot.find(f"body[@name='{side}_wheel']").get("pos").split()[0])
                       for side in ("left", "right")) / 2 if center_axle else 0.0)
    robot.set("pos", f"{start[0] * cell_size - axle_offset} {start[1] * cell_size} 0")
    # Existing decorative housing geoms are non-colliding. This invisible box
    # gives every course scene the same chassis/wall collision footprint.
    ET.SubElement(robot, "geom", name="course_chassis_collision", type="box",
                  pos="0 0 0.10", size="0.068 0.064 0.045", rgba="0 0 0 0",
                  contype="1", conaffinity="1")
    wall_id = 0
    def wall(x, y, sx, sy):
        nonlocal wall_id
        ET.SubElement(world, "geom", name=f"course_wall_{wall_id}", type="box",
                      pos=f"{x} {y} 0.15", size=f"{sx} {sy} 0.15", rgba="0.36 0.46 0.57 1")
        wall_id += 1
    half, thickness = cell_size / 2, wall_thickness / 2
    if tiles:
        floor = world.find("geom[@name='floor']")
        floor.set("pos", f"{(width-1)*half} {(height-1)*half} 0")
        floor.set("size", f"{width*half+1} {height*half+1} 0.1")
        if width*height <= 100:
            for x in range(width):
                for y in range(height):
                    shade = "0.86 0.89 0.92 1" if (x+y) % 2 else "0.96 0.97 0.98 1"
                    ET.SubElement(world, "geom", name=f"course_tile_{x}_{y}", type="box",
                                  pos=f"{x*cell_size} {y*cell_size} 0.0001",
                                  size=f"{half} {half} 0.0001", rgba=shade, contype="0", conaffinity="0")
        else:
            # Two sets of grid lines mark the same exact cell pitch without
            # thousands of visual-only floor bodies in the large maze.
            for axis, count in ((0, width), (1, height)):
                for line in range(count+1):
                    pos = [(width-1)*half, (height-1)*half, 0.0001]
                    size = [width*half, height*half, 0.0001]
                    pos[axis] = (line-0.5)*cell_size
                    size[axis] = 0.0005
                    ET.SubElement(world, "geom", name=f"course_grid_{axis}_{line}", type="box",
                                  pos=" ".join(map(str, pos)), size=" ".join(map(str, size)),
                                  rgba="0.72 0.76 0.80 1", contype="0", conaffinity="0")

    def runs(present):
        start = None
        for index, exists in enumerate([*present, False]):
            if exists and start is None:
                start = index
            if start is not None and (not exists or not merge_walls):
                end = index if not exists else index+1
                yield start, end
                start = None
    for x in range(width + 1):
        present = [_edge((x-1, y), (x, y)) not in openings for y in range(height)]
        for first, end in runs(present):
            wall((x-.5)*cell_size, (first+end-1)*half, thickness, (end-first)*half+thickness)
    for y in range(height + 1):
        present = [_edge((x, y-1), (x, y)) not in openings for x in range(width)]
        for first, end in runs(present):
            wall((first+end-1)*half, (y-.5)*cell_size, (end-first)*half+thickness, thickness)
    for label, cell, rgba in (("start", start, "0.1 0.4 0.95 0.5"), ("goal", goal, "0.1 0.8 0.3 0.5")):
        ET.SubElement(world, "site", name=f"course_{label}", type="cylinder",
                      pos=f"{cell[0] * cell_size} {cell[1] * cell_size} 0.002",
                      size=f"{goal_radius if label == 'goal' else min(0.14, cell_size*0.3)} 0.002", rgba=rgba)
    ET.SubElement(root, "statistic", center=f"{(width-1)*half} {(height-1)*half} 0.1",
                  extent=str(max(width, height) * cell_size / 2 + 0.3))
    folder = OUTPUT / "scenes"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}_{resolve_xml(kind).stem}_{seed if seed is not None else 'fixed'}.xml"
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return World(path, name, seed, start, goal, cell_size, frozenset(openings))


def scenario(name="straight", kind="all"):
    """Load a prepared exercise XML without generating or writing a scene."""
    cases = {
        "straight": (4, 1, [(0,0), (1,0), (2,0), (3,0)], (0,0), (3,0), []),
        "corner": (3, 3, [(0,0), (1,0), (2,0), (2,1), (2,2)], (0,0), (2,2), []),
        "junction": (3, 3, [(0,1), (1,1), (2,1), (2,2)], (0,1), (2,2), [((2,1),(2,0))]),
        "cross": (4, 3, [(0,1), (1,1), (2,1), (2,2)], (0,1), (2,2), [((2,1),(2,0)), ((2,1),(3,1))]),
    }
    if name not in cases:
        raise ValueError(f"Choose one of {CASES}")
    width, height, path, start, goal, extra = cases[name]
    openings = {_edge(a, b) for a, b in zip(path, path[1:])} | {_edge(a,b) for a,b in extra}
    prepared = Path(__file__).resolve().parents[2] / "scenes" / f"{name}_{resolve_xml(kind).stem}.xml"
    if not prepared.is_file():
        raise FileNotFoundError(f"Prepared scene not found: {prepared}")
    return World(prepared, name, None, start, goal, 0.8, frozenset(openings))


def _carve(width, height, seed):
    rng = random.Random(seed)
    visited, stack, openings = {(0,0)}, [(0,0)], set()
    while stack:
        x, y = stack[-1]
        choices = [(x+dx, y+dy) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))
                   if 0 <= x+dx < width and 0 <= y+dy < height and (x+dx,y+dy) not in visited]
        if not choices:
            stack.pop()
            continue
        following = rng.choice(choices)
        openings.add(_edge(stack[-1], following))
        visited.add(following)
        stack.append(following)
    return openings


def random_maze(kind="all", *, seed=None, width=3, height=3, cell_size=0.8):
    """Generate a connected perfect maze; seed=None produces a new local seed."""
    if not isinstance(width, int) or not isinstance(height, int) or width < 2 or height < 2:
        raise ValueError("width and height must be integers >= 2")
    if cell_size < 0.5:
        raise ValueError("cell_size must be at least 0.5 m")
    seed = secrets.randbits(32) if seed is None else int(seed)
    openings = _carve(width, height, seed)
    return _build("random", kind, width, height, openings, (0,0), (width-1,height-1),
                  seed=seed, cell_size=cell_size)


def square_maze(kind="all", *, size=10, seed=None):
    """Square maze with 30 cm cells, 1 cm walls and an actual east-side exit.

    The blue start is inside (0, 0). The green goal is one cell beyond the
    upper-right exit. Center the wheel axle for clearance during in-place turns.
    The policy receives sensors, not these openings or the exit coordinates.
    """
    if isinstance(size, bool) or not isinstance(size, int) or size < 2:
        raise ValueError("size must be an integer >= 2")
    seed = secrets.randbits(32) if seed is None else int(seed)
    openings = _carve(size, size, seed)
    openings.add(_edge((size-1, size-1), (size, size-1)))
    return _build(f"square_30cm_{size}x{size}", kind, size, size, openings,
                  (0, 0), (size, size-1), seed=seed, cell_size=0.30,
                  wall_thickness=0.01, goal_radius=0.06, tiles=True, center_axle=True,
                  merge_walls=True)
