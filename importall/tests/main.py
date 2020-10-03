import io
import sys
import unittest
from pathlib import Path
from typing import List, Optional, Tuple

import volatile

from importall.main import main


class MainTest(unittest.TestCase):
    def do_run(self, args: List[str]) -> Tuple[str, Optional[Exception]]:
        buf = io.StringIO()
        exc = None
        try:
            old_stdout = sys.stdout
            sys.stdout = buf
            sys.stderr = buf
            main(args)
        except Exception as e:
            exc = e
        finally:
            for k in list(sys.modules.keys()):
                if k.startswith("fake_module"):
                    del sys.modules[k]
            sys.stdout = old_stdout
        return (buf.getvalue(), exc)

    def test_initial_import_fail(self) -> None:
        output, err = self.do_run(["fake_module"])
        # TODO message
        self.assertIsInstance(err, ImportError)

    def test_no_single_module(self) -> None:
        output, err = self.do_run(["os"])
        # TODO message
        self.assertIsInstance(err, AssertionError)

    def test_no_root(self) -> None:
        output, err = self.do_run(["importall"])
        self.assertEqual(
            """\
importall ok
importall.finder ok
importall.main ok
""",
            output,
        )

    def test_ok(self) -> None:
        with volatile.dir() as d:
            pd = Path(d)
            (pd / "fake_module").mkdir()
            (pd / "fake_module" / "__init__.py").write_text("")
            (pd / "fake_module" / "__main__.py").write_text("")
            (pd / "fake_module" / "tests").mkdir()
            (pd / "fake_module" / "tests" / "__init__.py").write_text("")
            (pd / "fake_module" / "tests" / "x.py").write_text("")
            (pd / "fake_module" / "x.py").write_text("")

            output, err = self.do_run([f"--root={d}", "fake_module"])

        self.assertEqual(
            """\
fake_module ok
fake_module.x ok
""",
            output,
        )
        self.assertEqual(None, err)

    def test_fail(self) -> None:
        with volatile.dir() as d:
            pd = Path(d)
            (pd / "fake_module").mkdir()
            (pd / "fake_module" / "__init__.py").write_text("")
            (pd / "fake_module" / "x.py").write_text("x x")

            output, err = self.do_run([f"--root={d}", "fake_module"])
        self.assertEqual(
            """\
fake_module ok
""",
            output,
        )
        # TODO message
        self.assertIsInstance(err, SyntaxError)
