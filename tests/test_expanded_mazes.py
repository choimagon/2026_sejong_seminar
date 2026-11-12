"""Prepared challenge XMLs: real walls, reachable goals and map-only settings."""
from collections import defaultdict, deque
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

import numpy as np

from module import Robot, sensor
from module.move import move
from examples.runtime import Lab
from examples.world import world


class ExpandedMazeTest(unittest.TestCase):
    def layout(self, path, size):
        root = ET.parse(path).getroot()
        walls = [geom for geom in root.findall('worldbody/geom')
                 if geom.get('name', '').startswith('course_wall_')]
        def blocked(x, y):
            for wall in walls:
                px, py, _ = map(float, wall.get('pos').split())
                sx, sy, _ = map(float, wall.get('size').split())
                if abs(x-px) <= sx+1e-8 and abs(y-py) <= sy+1e-8:
                    return True
            return False
        adjacency = defaultdict(list)
        for x in range(size):
            for y in range(size):
                for dx, dy in ((1, 0), (0, 1)):
                    if x+dx < size and y+dy < size and not blocked((x+dx/2)*.8, (y+dy/2)*.8):
                        a, b = (x, y), (x+dx, y+dy)
                        adjacency[a].append(b)
                        adjacency[b].append(a)
                for px, py in ((-.4,y*.8), ((size-.5)*.8,y*.8),
                               (x*.8,-.4), (x*.8,(size-.5)*.8)):
                    self.assertTrue(blocked(px, py), (path, px, py))
        return adjacency

    def test_saved_walls_form_connected_harder_mazes_and_match_sensor_variants(self):
        for size, expected_path, expected_deadends in ((5, 10, 5), (10, 66, 13)):
            reference = None
            for kind in ('basic', 'sonic', 'lidar', 'all'):
                with self.subTest(size=size, kind=kind):
                    path = world(f'maze_{size}x{size}', kind)
                    graph = self.layout(path, size)
                    edges = {tuple(sorted((a,b))) for a, others in graph.items() for b in others}
                    self.assertEqual(len(edges), size*size-1)
                    if reference is None:
                        reference = edges
                    self.assertEqual(edges, reference)
                    queue = deque([((0,0), 0)])
                    distance = {(0,0): 0}
                    while queue:
                        cell, steps = queue.popleft()
                        for other in graph[cell]:
                            if other not in distance:
                                distance[other] = steps+1
                                queue.append((other, steps+1))
                    self.assertEqual(len(distance), size*size)
                    self.assertEqual(distance[(size-1,size-1)], expected_path)
                    self.assertEqual(sum(len(v)==1 for v in graph.values()), expected_deadends)

    def test_all_xml_models_load_with_correct_sensors_and_same_cell_pitch(self):
        for size in (5, 10):
            for kind in ('basic', 'sonic', 'lidar', 'all'):
                with self.subTest(size=size, kind=kind), Robot(world(f'maze_{size}x{size}',kind)) as robot:
                    groups = sensor.available_sensors(robot.model)
                    self.assertEqual('ultrasonic' in groups, kind in ('sonic','all'))
                    self.assertEqual('lidar' in groups, kind in ('lidar','all'))
                    np.testing.assert_allclose(robot.model.numeric('course_maze_size').data, [size,size])
                    self.assertEqual(robot.model.numeric('course_cell_size').data[0], .8)
                    np.testing.assert_allclose(robot.model.site('course_start').pos[:2], [0,0])
                    np.testing.assert_allclose(robot.model.site('course_goal').pos[:2], [(size-1)*.8]*2)
                    robot.run_for(.3)
                    if 'ultrasonic' in groups:
                        self.assertGreater(sensor.ultrasonic.read(robot), 0)
                    if 'lidar' in groups:
                        self.assertTrue(np.isfinite(sensor.lidar.read(robot)['ranges_m']).all())

    def test_xml_switch_alone_changes_limit_and_camera_without_changing_3x3(self):
        for name, limit in (('maze',240), ('maze_5x5',900), ('maze_10x10',3600)):
            viewer = MagicMock()
            viewer.cam.lookat = np.zeros(3)
            with self.subTest(name=name), patch.object(Robot,'view',return_value=viewer):
                lab = Lab(xml_path=world(name,'lidar'),move=move,show=True)
                lab.robot._viewer = viewer
                try:
                    self.assertEqual(lab.max_sim_time, limit)
                    self.assertEqual(viewer.cam.distance, max(4.8,lab.robot.model.stat.extent*3.2))
                    if limit>240:
                        lab.robot.data.time = 250
                        self.assertTrue(lab.running())
                    lab.robot.data.time = limit+.1
                    with self.assertRaisesRegex(RuntimeError, f'{limit} simulation seconds'):
                        lab.running()
                finally:
                    lab.close()


if __name__ == '__main__':
    unittest.main()
