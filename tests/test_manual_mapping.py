"""One ultrasonic module and manual, odometry-based endpoint accumulation."""
import ast
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mujoco
import numpy as np

from module import Robot, sensor, course
from module.mapping import MappingSession
from module.plotting import make_figure
from examples.world import world

ROOT = Path(__file__).resolve().parents[1]


def callback(name):
    tree = ast.parse((ROOT/'examples'/name).read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'add_points')
    namespace = {'cos': math.cos, 'sin': math.sin, 'isfinite': math.isfinite}
    exec(compile(ast.Module(body=[function], type_ignores=[]), name, 'exec'), namespace)
    return namespace['add_points']


def packet(moment=1., reading=1., x=0., y=0., yaw=0., kind='ultrasonic'):
    return {'time': moment, kind: reading, 'odometry': {
        'estimated_x_m': x, 'estimated_y_m': y, 'estimated_yaw_rad': yaw,
        'truth_x_m': 9000., 'truth_y_m': -9000., 'truth_yaw_rad': 2000.}}


class ManualMappingTest(unittest.TestCase):
    def test_one_transmitter_receiver_module_has_one_float_reading(self):
        with Robot(world('pillar', 'sonic')) as robot:
            ranges = [robot.model.sensor(i).name for i in range(robot.model.nsensor)
                      if robot.model.sensor_type[i] == mujoco.mjtSensor.mjSENS_RANGEFINDER]
            self.assertEqual(ranges, ['front_ultrasonic_ray'])
            self.assertIsInstance(sensor.ultrasonic.read(robot), float)
            self.assertLess(sensor.ultrasonic.read(robot), 1.)
            self.assertGreaterEqual(robot.model.geom('ultra_tx_eye').id, 0)
            self.assertGreaterEqual(robot.model.geom('ultra_rx_eye').id, 0)
        with Robot('sonic') as robot:
            self.assertTrue(math.isinf(sensor.ultrasonic.read(robot)))

    def test_student_callbacks_transform_and_skip_missing_returns(self):
        points = []
        sonar = callback('09_ultrasonic_mapping.py')
        sonar(2., 1., 3., math.pi/2, points)
        sonar(math.inf, 1., 3., 0., points)
        np.testing.assert_allclose(points, [(1., 5.)])
        points = []
        scan = {'angles_rad': np.array([0., math.pi/2, math.pi]),
                'ranges_m': np.array([2., 1., math.inf])}
        callback('10_lidar_mapping.py')(scan, 1., 3., math.pi/2, points)
        np.testing.assert_allclose(points, [(1., 5.), (0., 3.)], atol=1e-14)

    def test_mapping_uses_estimated_sensor_pose_and_handles_reset_pause(self):
        with Robot(world('pillar', 'sonic')) as robot:
            mapper = MappingSession(robot.model, 'ultrasonic', callback('09_ultrasonic_mapping.py'))
            mapper.update(packet(x=1., y=2., yaw=math.pi/2))
            np.testing.assert_allclose(mapper.points, [(1.03, 3.044)], atol=1e-12)
            mapper.update(packet(x=1., y=2., yaw=math.pi/2))
            self.assertEqual(len(mapper.points), 1)  # paused/duplicate telemetry
            mapper.update(packet(moment=1.2, x=2., y=2.))
            self.assertEqual(len(mapper.points), 2)
            mapper.update(packet(moment=.1, x=0., y=0.))
            np.testing.assert_allclose(mapper.points, [(1.074, 0.)])
            self.assertEqual(len(mapper.path), 1)

    def test_save_keeps_all_points_and_separates_robot_path(self):
        with Robot(world('pillar', 'sonic')) as robot, TemporaryDirectory() as folder:
            mapper = MappingSession(robot.model, 'ultrasonic', callback('09_ultrasonic_mapping.py'))
            mapper.update(packet(reading=2.))
            filename = mapper.save(folder)
            self.assertTrue(filename.is_file())
            arrays = np.load(filename.with_suffix('.npz'))
            np.testing.assert_allclose(arrays['ultrasonic'], [(2.074, 0.)])
            np.testing.assert_allclose(arrays['path'], [(0., 0.)])
            self.assertEqual(arrays['lidar'].shape, (0, 2))

    def test_live_preview_decimates_without_discarding_saved_points(self):
        with Robot(world('pillar', 'lidar')) as robot:
            mapper = MappingSession(robot.model, 'lidar', callback('10_lidar_mapping.py'))
            scan = sensor.lidar.read(robot)
            for index in range(100):
                mapper.update(packet(moment=index*.11, reading=scan, kind='lidar'))
            original_count = len(mapper.points)
            self.assertGreater(original_count, 2000)
            fig = make_figure('Map', ('Endpoints', 'Path', 'Robot'), ((0,1,0),(1,1,1),(1,0,0)))
            mapper.draw(fig)
            self.assertEqual(len(mapper.points), original_count)
            self.assertTrue((fig.linepnt <= fig.linedata.shape[1]//2).all())
            displayed = fig.linedata[0, :2*fig.linepnt[0]].reshape(-1, 2)
            self.assertLess(displayed[:,0].min(), -.4)
            self.assertGreater(displayed[:,0].max(), 2.5)
            self.assertLess(displayed[:,1].min(), -1.)
            self.assertGreater(displayed[:,1].max(), 1.)

    def test_manual_move_physically_changes_sensor_and_map(self):
        with Robot(world('pillar', 'sonic')) as robot:
            robot.run_for(.3)
            session = course.Session(robot, policy=None, max_sim_time=None)
            mapper = MappingSession(robot.model, 'ultrasonic', callback('09_ultrasonic_mapping.py'))
            initial = sensor.ultrasonic.read(robot)
            for _ in range(200):
                session.advance(manual=(.2, 0.))
                mapper.update({'time': robot.time, 'ultrasonic': sensor.ultrasonic.read(robot),
                               'odometry': session.telemetry()})
            self.assertLess(sensor.ultrasonic.read(robot), initial-.08)
            self.assertGreater(len(mapper.points), 5)
            self.assertGreater(mapper.path[-1][0], .08)
            # All endpoints still land on the same front pillar despite robot motion.
            self.assertLess(np.ptp(np.array(mapper.points)[:,0]), .02)
            self.assertIsNone(session.policy)
