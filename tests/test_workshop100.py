"""Physical checks for the 100-minute workshop's supplied answers."""
import math
import unittest
from unittest.mock import patch

from module import Robot
from module.course import run, square_maze
from workshop100.world import world
from importlib import import_module

move = import_module("workshop100.01_move").move
choose = import_module("workshop100.05_sensor_route").choose
ACTIONS = import_module("workshop100.03_route").ACTIONS
from workshop100.runtime import Lab, sensor_route
from workshop100.maze_policy import Policy


class Workshop100Test(unittest.TestCase):
    def test_gui_accepts_student_wheel_velocity_status(self):
        from module import guide
        latest = {"motion": {"state": "running", "kind": "wheel_velocity",
                             "target_rad_s": [1.0, 2.0], "pending": 0}}
        with patch.object(guide.mujoco, "mjr_overlay") as overlay, \
             patch.object(guide.mujoco, "mjr_rectangle"), \
             patch.object(guide.mujoco, "mjr_label"):
            guide.draw_guide(1040, 800, 1, object(), latest, "", False, "")
        self.assertTrue(any("1.000 / 2.000 rad/s" in str(call) for call in overlay.call_args_list))

    def test_reference_wheels_and_signs(self):
        with Robot(world()) as robot:
            move(robot, .2, 0)
            robot.run_for(1)
            self.assertGreater(robot.data.qpos[0], .10)
            move(robot, 0, 1)
            robot.run_for(1)
            gyro = robot.data.sensor('gyro').data[2]
            self.assertGreater(gyro, .5)
            move(robot, 0, 0)
            robot.run_for(1)
            self.assertLess(abs(robot.data.sensor('gyro').data[2]), .05)

    def test_timed_reference_reaches_goal_without_contacts(self):
        lab = Lab(move=move)
        try:
            for linear, angular, seconds in ACTIONS:
                lab.run_for(linear, angular, seconds)
            lab.stop()
            result = lab.result()
            self.assertTrue(result['goal_reached'], result)
            self.assertEqual(result['obstacle_contacts'], 0)
        finally:
            lab.close()

    def test_sensor_reference_both_sensors_and_shifted_pillar(self):
        for name in ('pillar', 'shifted'):
            for kind in ('ultrasonic', 'lidar'):
                with self.subTest(map=name, sensor=kind):
                    lab = Lab(name, move=move)
                    try:
                        result = sensor_route(lab, choose, kind)
                        self.assertTrue(result['goal_reached'], result)
                        self.assertEqual(result['obstacle_contacts'], 0, result)
                        self.assertGreater(len(lab.lidar_points), 1000)
                        self.assertGreater(len(lab.sonar_points), 10)
                    finally:
                        lab.close()

    def test_small_maze_demo_finishes(self):
        result = run(square_maze('all', size=3, seed=7), Policy(),
                     max_sim_time=90, trace_name='test_workshop100')
        self.assertTrue(result['finished'], result)
        self.assertEqual(result['wall_contacts'], 0)


if __name__ == '__main__':
    unittest.main()
