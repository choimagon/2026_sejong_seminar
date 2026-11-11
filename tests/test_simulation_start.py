"""Regression checks for Windows HANDLE vs POSIX fd inheritance."""

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

from module import simulation


class SimulationStartTest(unittest.TestCase):
    def launch(self, platform, *, failure=False):
        parent, child = Mock(), Mock()
        child.fileno.return_value = 123
        child.__class__.__name__ = "PipeConnection" if platform == "win32" else "Connection"
        popen = Mock(side_effect=OSError("launch failed") if failure else None)
        with patch.object(simulation, "Pipe", return_value=(parent, child)), \
             patch.object(simulation.sys, "platform", platform), \
             patch.object(simulation.subprocess, "Popen", popen), \
             patch.object(simulation.subprocess, "STARTUPINFO", create=True) as startup, \
             patch.object(simulation.os, "set_handle_inheritable", create=True) as inherit:
            if failure:
                with self.assertRaisesRegex(OSError, "launch failed"):
                    simulation.start_simulation()
                parent.close.assert_called_once()
            else:
                process, connection = simulation.start_simulation()
                self.assertIs(connection, parent)
                self.assertIs(process, popen.return_value)
                parent.close.assert_not_called()
            child.close.assert_called_once()
            args, kwargs = popen.call_args
            self.assertTrue(kwargs["close_fds"])
            if platform == "win32":
                self.assertNotIn("pass_fds", kwargs)
                startup.assert_called_once_with(lpAttributeList={"handle_list": [123]})
                self.assertEqual([c.args for c in inherit.call_args_list], [(123, True), (123, False)])
                self.assertIn("run_simulation(PipeConnection(123)", args[0][2])
            else:
                self.assertEqual(kwargs["pass_fds"], (123,))
                self.assertNotIn("startupinfo", kwargs)
                inherit.assert_not_called()
                self.assertIn("run_simulation(Connection(123)", args[0][2])
            expected = "mjpython" if platform == "darwin" else Path(sys.executable).name
            self.assertEqual(Path(args[0][0]).name, expected)

    def test_platform_launch_and_cleanup(self):
        for platform in ("win32", "darwin", "linux"):
            for failure in (False, True):
                with self.subTest(platform=platform, failure=failure):
                    self.launch(platform, failure=failure)

    def test_real_subprocess_bidirectional_pipe(self):
        # Exercise real inheritance and endpoint reconstruction without a display.
        real_popen = subprocess.Popen
        def launch(args, **kwargs):
            args = list(args)
            args[2] = args[2].replace(
                "from module.simulation import run_simulation; ",
                "def_placeholder; ")
            args[2] = args[2].replace("def_placeholder; ",
                "exec('def run_simulation(c, *a, **kw):\\n"
                " c.send(c.recv())\\n c.close()'); ")
            return real_popen(args, **kwargs)
        with patch.object(simulation.subprocess, "Popen", side_effect=launch):
            process, connection = simulation.start_simulation(sensors=(), demo=False)
        try:
            message = {"action": "drive", "value": (0.2, 0.0), "label": "로봇"}
            connection.send(message)
            self.assertTrue(connection.poll(15), "child did not reply")
            self.assertEqual(connection.recv(), message)
            process.wait(timeout=10)
            self.assertEqual(process.returncode, 0)
            # A closed Windows named pipe can report EOF from poll itself.
            with self.assertRaises((EOFError, BrokenPipeError)):
                self.assertTrue(connection.poll(2))
                connection.recv()
        finally:
            connection.close()
            if process.poll() is None:
                process.kill()
                process.wait()


if __name__ == "__main__":
    unittest.main()
