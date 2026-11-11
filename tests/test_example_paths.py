"""Student starters keep only setup/imports until the lesson is filled in."""
import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExamplePathsTest(unittest.TestCase):
    def run_file(self, script, cwd):
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        result = subprocess.run([sys.executable, str(script)], cwd=cwd, env=env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')

    def test_all_eleven_starters_preserve_setup_and_imports_only(self):
        files = sorted((ROOT/'examples').glob('[0-9][0-9]_*.py'))
        self.assertEqual([int(p.name[:2]) for p in files], list(range(1, 12)))
        for path in files:
            with self.subTest(file=path.name):
                tree = ast.parse(path.read_text(encoding='utf-8'))
                guard = tree.body[0]
                self.assertIsInstance(guard, ast.If)
                self.assertEqual(ast.unparse(guard.test), "__package__ in (None, '')")
                self.assertEqual(len(guard.body), 1)
                self.assertIsInstance(guard.body[0], ast.Import)
                self.assertEqual(guard.body[0].names[0].name, '_bootstrap')
                self.assertTrue(tree.body[1:])
                self.assertTrue(all(isinstance(n, (ast.Import, ast.ImportFrom)) for n in tree.body[1:]))

    def test_all_starters_execute_without_opening_a_viewer(self):
        for path in sorted((ROOT/'examples').glob('[0-9][0-9]_*.py')):
            with self.subTest(file=path.name):
                self.run_file(path.relative_to(ROOT), ROOT)

    def test_direct_paths_from_examples_and_an_unrelated_folder(self):
        script = ROOT/'examples/06_lidar.py'
        self.run_file(Path(script.name), script.parent)
        with tempfile.TemporaryDirectory(prefix='student starter path ') as folder:
            self.run_file(script, folder)
