"""Student templates must resolve project imports when run by file path."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExamplePathsTest(unittest.TestCase):
    def run_file(self, script, cwd):
        environment = os.environ.copy()
        environment.pop('PYTHONPATH', None)
        result = subprocess.run([sys.executable, str(script)], cwd=cwd,
                                env=environment, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_student_templates_from_project_root(self):
        scripts = sorted((ROOT / 'examples').glob('[0-9][0-9]_*.py'))
        self.assertEqual(len(scripts), 16)
        for script in scripts:
            with self.subTest(file=script.name):
                self.run_file(script.relative_to(ROOT), ROOT)

    def test_from_examples_folder_and_unrelated_directory(self):
        script = ROOT / 'examples/16_maze_escape.py'
        self.run_file(Path(script.name), script.parent)
        with tempfile.TemporaryDirectory(prefix='seminar path with spaces ') as folder:
            self.run_file(script, folder)


if __name__ == '__main__':
    unittest.main()
