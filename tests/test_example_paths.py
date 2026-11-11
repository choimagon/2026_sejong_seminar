"""Run unchanged student scripts with desktop adapters replaced in the test harness."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = '''
import sys, runpy
from pathlib import Path
from unittest.mock import patch
script = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(script.parent))
import _bootstrap
from examples.runtime import Lab
class TestLab(Lab):
    def __init__(self, *a, **kw):
        kw['show'] = False
        super().__init__(*a, **kw)
with patch('examples.runtime.Lab', TestLab), patch('module.viewer.view') as view, patch('module.course.view'), patch('module.playback.ask_speed', return_value=1), patch('examples.runtime.save_map'):
    runpy.run_path(str(script), run_name='__main__')
'''

class ExamplePathsTest(unittest.TestCase):
    def run_file(self, script, cwd):
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        env['MPLBACKEND'] = 'Agg'
        result = subprocess.run([sys.executable, '-c', HARNESS, str(script)], cwd=cwd,
                                env=env, capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_all_eleven_scripts_run_without_arguments(self):
        scripts = sorted((ROOT/'examples').glob('[0-9][0-9]_*.py'))
        self.assertEqual([int(p.name[:2]) for p in scripts], list(range(1, 12)))
        for script in scripts:
            with self.subTest(file=script.name):
                self.run_file(script.relative_to(ROOT), ROOT)

    def test_routes_reach_goal_without_arguments(self):
        for name in ['03_route_left', '04_route_right', '07_ultrasonic_route', '08_lidar_route']:
            with self.subTest(file=name):
                output = self.run_file(Path('examples')/f'{name}.py', ROOT)
                self.assertIn("'goal_reached': True", output)
                self.assertIn("'obstacle_contacts': 0", output)

    def test_from_examples_and_unrelated_folder(self):
        script = ROOT/'examples/06_lidar.py'
        self.run_file(Path(script.name), script.parent)
        with tempfile.TemporaryDirectory(prefix='lesson path with spaces ') as folder:
            self.run_file(script, folder)
