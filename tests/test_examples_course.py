"""Numbered files, actual XML sensor selection, routes and mapping."""
import ast
from types import SimpleNamespace
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
from unittest.mock import patch
import numpy as np
from module import Robot, sensor
from module.course import run, square_maze
from examples.world import world
from examples.runtime import Lab, sensor_route
from examples.maze_policy import Policy

from module.move import move
from module.course import sector


def lesson(name):
    # Inspect reusable definitions without importing an intentionally executable script.
    filename = Path(__file__).resolve().parents[1] / 'examples' / f'{name}.py'
    tree = ast.parse(filename.read_text())
    values = {'sensor': sensor, 'sector': sector}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            key = node.targets[0].id
            if key == 'XML':
                values[key] = filename.parent / 'scenes' / ast.literal_eval(node.value.right)
            elif key in ('ACTIONS', 'STOP_DISTANCE'):
                values[key] = ast.literal_eval(node.value)
        elif isinstance(node, ast.FunctionDef) and node.name in ('choose', 'read_front'):
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(filename), 'exec'), values)
    return SimpleNamespace(**values)


class ExamplesCourseTest(unittest.TestCase):
    def test_scripts_have_no_main_guard_and_use_the_public_move(self):
        root = Path(__file__).resolve().parents[1]
        for filename in (root / 'examples').glob('[0-9][0-9]_*.py'):
            source = filename.read_text()
            self.assertNotIn('__main__', source)
            self.assertNotIn('import_module', source)
            if filename.name[:2] not in ('01', '13'):
                tree = ast.parse(source)
                self.assertTrue(any(isinstance(n, ast.ImportFrom) and n.module == 'module.move'
                                    and any(a.name == 'move' for a in n.names) for n in tree.body), filename)

    def test_policy_file_can_import_sibling_helper_and_restores_path(self):
        from module.course import load_policy
        before = list(sys.path)
        with TemporaryDirectory() as folder:
            directory = Path(folder)
            (directory / '_path_policy_helper.py').write_text('VALUE = 7\n')
            policy = directory / 'policy.py'
            policy.write_text('from _path_policy_helper import VALUE\nclass Policy:\n    value = VALUE\n')
            try:
                self.assertEqual(load_policy(policy).value, 7)
                self.assertEqual(sys.path, before)
            finally:
                sys.modules.pop('_path_policy_helper', None)

    def test_files_select_actual_sensor_xml(self):
        assignments = {
            '01_move':'basic','02_keyboard_straight':'basic','03_keyboard_left':'basic',
            '04_keyboard_right':'basic','05_route_left':'basic','06_route_right':'basic',
            '07_ultrasonic':'sonic','08_lidar':'lidar','09_ultrasonic_route':'sonic',
            '10_lidar_route':'lidar','11_ultrasonic_mapping':'sonic','12_lidar_mapping':'lidar'}
        for name, model in assignments.items():
            with self.subTest(file=name):
                xml=lesson(name).XML
                self.assertTrue(xml.is_file())
                self.assertTrue(xml.stem.endswith(model))
                with Robot(xml) as robot:
                    groups=set(sensor.available_sensors(robot.model))
                    self.assertEqual('ultrasonic' in groups, model=='sonic')
                    self.assertEqual('lidar' in groups, model=='lidar')

    def test_corridors_start_with_a_straight_leg(self):
        for name, sign in [('left_corner',1),('right_corner',-1)]:
            with Robot(world(name,'basic')) as robot:
                start=robot.model.site('course_start').pos[:2]
                goal=robot.model.site('course_goal').pos[:2]
                self.assertGreater(goal[0]-start[0],2.0)
                self.assertGreater(sign*(goal[1]-start[1]),1.0)
                before=robot.data.qpos[:2].copy()
                move(robot,.2,0);robot.run_for(2)
                delta=robot.data.qpos[:2]-before
                self.assertGreater(delta[0],.25)
                self.assertLess(abs(delta[1]),.02)

    def test_timed_left_and_right_reach_goal(self):
        for name in ['05_route_left','06_route_right']:
            module=lesson(name)
            lab=Lab(xml_path=module.XML,move=move)
            try:
                for v,w,t in module.ACTIONS:lab.run_for(v,w,t)
                lab.stop();result=lab.result()
                self.assertTrue(result['goal_reached'],result)
                self.assertEqual(result['obstacle_contacts'],0,result)
                self.assertFalse(lab.lidar_points)
                self.assertFalse(lab.sonar_points)
            finally:lab.close()

    def test_sensor_routes_and_mapping_only_use_present_sensor(self):
        for name,kind in [('09_ultrasonic_route','ultrasonic'),('10_lidar_route','lidar')]:
            module=lesson(name)
            lab=Lab(xml_path=module.XML,move=move)
            try:
                result=sensor_route(lab,module.choose,kind,read_front=module.read_front)
                self.assertTrue(result['goal_reached'],result)
                self.assertEqual(result['obstacle_contacts'],0,result)
                self.assertEqual(bool(lab.lidar_points),kind=='lidar')
                self.assertEqual(bool(lab.sonar_points),kind=='ultrasonic')
                missing=sensor.lidar if kind=='ultrasonic' else sensor.ultrasonic
                with self.assertRaises(ValueError):missing.read(lab.robot)
            finally:lab.close()

    def test_gui_wheel_velocity_status(self):
        from module import guide
        latest={'motion':{'state':'running','kind':'wheel_velocity','target_rad_s':[1.,2.]}}
        with patch.object(guide.mujoco,'mjr_overlay') as overlay, \
             patch.object(guide.mujoco,'mjr_rectangle'),patch.object(guide.mujoco,'mjr_label'):
            guide.draw_guide(1040,800,1,object(),latest,'',False,'')
        self.assertTrue(any('1.000 / 2.000 rad/s' in str(c) for c in overlay.call_args_list))

    def test_lidar_maze(self):
        result=run(square_maze('lidar',size=3,seed=7),Policy(),max_sim_time=90,
                   trace_name='test_examples_maze')
        self.assertTrue(result['finished'],result)
        self.assertEqual(result['wall_contacts'],0)


if __name__=='__main__':unittest.main()
