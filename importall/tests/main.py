import sys
import unittest
from pathlib import Path

import volatile
from click.testing import CliRunner

from importall.main import main


class MainTest(unittest.TestCase):
    def test_initial_import_fail(self):
        runner = CliRunner()
        result = runner.invoke(main, ["fake_module"])
        self.assertEqual(result.exit_code, 1)
        # TODO message
        self.assertIsInstance(result.exception, ImportError)

    def test_ok(self):
        with volatile.dir() as d:
            pd = Path(d)
            (pd / "fake_module").mkdir()
            (pd / "fake_module" / "__init__.py").write_text("")
            (pd / "fake_module" / "__main__.py").write_text("")
            (pd / "fake_module" / "tests").mkdir()
            (pd / "fake_module" / "tests" / "__init__.py").write_text("")
            (pd / "fake_module" / "tests" / "x.py").write_text("")
            (pd / "fake_module" / "x.py").write_text("")

            try:
                runner = CliRunner()
                result = runner.invoke(main, [f"--root={d}", "fake_module"])
            finally:
                sys.path.pop()
                for k in list(sys.modules.keys()):
                    if k.startswith("fake_module"):
                        del sys.modules[k]
        self.assertEqual(
            """\
fake_module ok
fake_module.x ok
""",
            result.output,
        )
        self.assertEqual(result.exit_code, 0)

    def test_fail(self):
        with volatile.dir() as d:
            pd = Path(d)
            (pd / "fake_module").mkdir()
            (pd / "fake_module" / "__init__.py").write_text("")
            (pd / "fake_module" / "x.py").write_text("x x")

            try:
                runner = CliRunner()
                result = runner.invoke(main, [f"--root={d}", "fake_module"])
            finally:
                sys.path.pop()
                for k in list(sys.modules.keys()):
                    if k.startswith("fake_module"):
                        del sys.modules[k]
        self.assertEqual(
            """\
fake_module ok
""",
            result.output,
        )
        self.assertEqual(result.exit_code, 1)
        # TODO message
        self.assertIsInstance(result.exception, SyntaxError)
