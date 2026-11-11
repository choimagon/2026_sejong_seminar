"""Numbered exercise files run directly, without -m or PYTHONPATH."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class ExamplePathsTest(unittest.TestCase):
    def run_file(self,script,cwd,*flags):
        env=os.environ.copy();env.pop('PYTHONPATH',None);env['MPLBACKEND']='Agg'
        result=subprocess.run([sys.executable,str(script),*flags],cwd=cwd,env=env,
                              capture_output=True,text=True,timeout=45)
        self.assertEqual(result.returncode,0,result.stderr)
        return result.stdout

    def test_all_fourteen_files_accept_direct_paths(self):
        scripts=sorted((ROOT/'examples').glob('[0-9][0-9]_*.py'))
        self.assertEqual([int(p.name[:2]) for p in scripts],list(range(1,15)))
        for script in scripts:
            with self.subTest(file=script.name):
                self.run_file(script.relative_to(ROOT),ROOT,'--help')

    def test_default_routes_run_without_selection_flags(self):
        for name in ['06_route_left','07_route_right','10_ultrasonic_route','11_lidar_route']:
            with self.subTest(file=name):
                output=self.run_file(Path('examples')/f'{name}.py',ROOT,'--headless')
                self.assertIn("'goal_reached': True",output)
                self.assertIn("'obstacle_contacts': 0",output)

    def test_from_examples_and_unrelated_folder(self):
        script=ROOT/'examples/09_lidar.py'
        self.run_file(Path(script.name),script.parent,'--headless')
        with tempfile.TemporaryDirectory(prefix='lesson path with spaces ') as folder:
            self.run_file(script,folder,'--headless')


if __name__=='__main__':unittest.main()
