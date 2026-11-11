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
from module.motion.commands import FORWARD_SPEED, TURN_SPEED


def lesson(name):
    # Inspect reusable definitions without importing an intentionally executable script.
    filename = Path(__file__).resolve().parents[1] / 'examples' / f'{name}.py'
    tree = ast.parse(filename.read_text(encoding="utf-8"))
    values = {'sensor': sensor, 'sector': sector, 'FORWARD_SPEED': FORWARD_SPEED, 'TURN_SPEED': TURN_SPEED}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            key = node.targets[0].id
            if key == 'XML':
                values[key] = filename.parent / 'scenes' / ast.literal_eval(node.value.right)
            elif key in ('ACTIONS', 'STOP_DISTANCE'):
                values[key] = ast.literal_eval(node.value)
        elif isinstance(node, ast.FunctionDef) and node.name in ('choose', 'read_front', 'keyboard_control'):
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(filename), 'exec'), values)
    return SimpleNamespace(**values)


class ExamplesCourseTest(unittest.TestCase):
    def test_scripts_have_no_main_guard_and_use_the_public_move(self):
        root = Path(__file__).resolve().parents[1]
        for filename in (root / 'examples').glob('[0-9][0-9]_*.py'):
            source = filename.read_text(encoding="utf-8")
            self.assertNotIn('__main__', source)
            self.assertNotIn('args', source)
            self.assertNotIn('arguments', source)
            self.assertNotIn('import_module', source)
            if filename.name[:2] not in ('01', '11'):
                tree = ast.parse(source)
                self.assertTrue(any(isinstance(n, ast.ImportFrom) and n.module == 'module.move'
                                    and any(a.name == 'move' for a in n.names) for n in tree.body), filename)

    def test_keyboard_callback_matches_shared_mapping(self):
        from module.motion.keyboard import keyboard_control
        custom = lesson('02_keyboard').keyboard_control
        for keys in [set(), {'w'}, {'s'}, {'q'}, {'e'}, {'w', 'q'}, {'w', 's'}, {'q', 'e'}]:
            pressed = lambda key: key in keys
            self.assertEqual(custom(pressed), keyboard_control(pressed))

    def test_students_can_change_keyboard_letters(self):
        filename = Path(__file__).resolve().parents[1] / 'examples/02_keyboard.py'
        source = filename.read_text(encoding="utf-8")
        for original, replacement in [('w', 'i'), ('s', 'k'), ('q', 'j'), ('e', 'l')]:
            source = source.replace(f'pressed("{original}")', f'pressed("{replacement}")')
        function = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef))
        namespace = {}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(filename), 'exec'), namespace)
        control = namespace['keyboard_control']
        for key, expected in [('i', (.35, 0)), ('k', (-.35, 0)), ('j', (0, 2)), ('l', (0, -2)), ('w', (0, 0))]:
            self.assertEqual(control(lambda pressed: pressed == key), expected)

    def test_middle_pillar_requires_and_allows_both_detours(self):
        xml = world('obstacle', 'basic')
        with Robot(xml) as robot:
            self.assertAlmostEqual(robot.model.geom('workshop_pillar').pos[0], 1.75)
            self.assertAlmostEqual(robot.model.geom('workshop_pillar').size[0], .14)
        for sign in (1, -1):
            lab = Lab(xml_path=xml, move=move)
            try:
                lab.forward(1.05)
                lab.turn(sign * np.pi / 2)
                lab.forward(.42)
                lab.turn(-sign * np.pi / 2)
                lab.forward(1.25)
                lab.turn(-sign * np.pi / 2)
                lab.forward(.42)
                lab.turn(sign * np.pi / 2)
                lab.forward(1.2)
                lab.stop()
                result = lab.result()
                self.assertTrue(result['goal_reached'], result)
                self.assertEqual(result['obstacle_contacts'], 0, result)
            finally:
                lab.close()

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

    def test_sensor_output_types_shapes_and_missing_values(self):
        with Robot(world('pillar', 'sonic')) as robot:
            distances = sensor.ultrasonic.read(robot)
            self.assertIsInstance(distances, float)
            self.assertTrue(np.isfinite(distances))
        with Robot('sonic') as robot:
            self.assertTrue(np.isinf(sensor.ultrasonic.read(robot)))
        with Robot(world('pillar', 'lidar')) as robot:
            scan = sensor.lidar.read(robot)
            shapes = {'angles_rad': (360,), 'ranges_m': (360,), 'points_xy_m': (360, 2),
                      'origin_world_m': (3,), 'directions_world': (360, 3), 'geom_ids': (360,)}
            self.assertEqual(set(scan), set(shapes))
            for key, shape in shapes.items():
                self.assertEqual(scan[key].shape, shape)
            np.testing.assert_allclose(scan['angles_rad'][[0, 90, 180, 270]], np.deg2rad([0, 90, 180, 270]))
            valid = np.isfinite(scan['ranges_m'])
            expected = scan['ranges_m'][valid, None] * np.column_stack((np.cos(scan['angles_rad'][valid]), np.sin(scan['angles_rad'][valid])))
            np.testing.assert_allclose(scan['points_xy_m'][valid], expected)
        with Robot('lidar') as robot:
            scan = sensor.lidar.read(robot)
            self.assertTrue(np.isinf(scan['ranges_m']).all())
            self.assertTrue(np.isnan(scan['points_xy_m']).all())
            self.assertTrue((scan['geom_ids'] == -1).all())

    def test_files_select_actual_sensor_xml(self):
        assignments = {
            '01_move':'basic','02_keyboard':'basic',
            '03_route_left':'basic','04_route_right':'basic',
            '05_ultrasonic':'sonic','06_lidar':'lidar','07_ultrasonic_route':'sonic',
            '08_lidar_route':'lidar','09_ultrasonic_mapping':'sonic','10_lidar_mapping':'lidar'}
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
        for name in ['03_route_left','04_route_right']:
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
        for name,kind in [('07_ultrasonic_route','ultrasonic'),('08_lidar_route','lidar')]:
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

    def test_lidar_accepts_old_and_new_mujoco_signatures(self):
        def older(m, d, pnt, vec, geomgroup, flg_static, bodyexclude, geomid, dist, nray, cutoff):
            geomid[:] = 0
            dist[:] = .5
        def newer(m, d, pnt, vec, geomgroup, flg_static, bodyexclude, geomid, dist, normal, nray, cutoff):
            """normal: optional output array in newer MuJoCo bindings."""
            self.assertIsNone(normal)
            older(m, d, pnt, vec, geomgroup, flg_static, bodyexclude, geomid, dist, nray, cutoff)
        with Robot(world('pillar', 'lidar')) as robot:
            for binding in (older, newer):
                with self.subTest(binding=binding.__name__), patch('mujoco.mj_multiRay', binding):
                    scan = sensor.lidar.read(robot, num_rays=4)
                    np.testing.assert_allclose(scan['ranges_m'], [.5, .5, .5, .5])
                    np.testing.assert_allclose(scan['points_xy_m'], [[.5,0], [0,.5], [-.5,0], [0,-.5]], atol=1e-15)

    def test_macos_map_saves_then_opens_without_matplotlib_window(self):
        import examples.runtime as runtime
        import matplotlib.pyplot as plt
        with TemporaryDirectory() as folder:
            lab = SimpleNamespace(lidar_points=[], sonar_points=[(1., 2.)], path=[(0., 0.), (.2, 0.)])
            with patch.object(runtime, '__file__', str(Path(folder)/'examples/runtime.py')), \
                 patch.object(runtime.sys, 'platform', 'darwin'), \
                 patch.object(runtime.subprocess, 'run') as opened, patch.object(plt, 'show') as show:
                filename = runtime.save_map(lab, show=True, name='regression_map')
                self.assertTrue(filename.is_file())
                np.testing.assert_array_equal(np.load(filename.with_suffix('.npz'))['ultrasonic'], [[1., 2.]])
                opened.assert_called_once_with(['open', str(filename)], check=True)
                show.assert_not_called()

    def test_lidar_maze(self):
        result=run(square_maze('lidar',size=3,seed=7),Policy(),max_sim_time=90,
                   trace_name='test_examples_maze')
        self.assertTrue(result['finished'],result)
        self.assertEqual(result['wall_contacts'],0)


if __name__=='__main__':unittest.main()
