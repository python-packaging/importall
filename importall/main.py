import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .finder import find_importable_names


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exclude", default="tests", help="comma-separated directories to ignore"
    )
    parser.add_argument("--root", help="Search under this dir")
    parser.add_argument("package", nargs='+', metavar="PACKAGE", help="Name of package(s) to test")
    args = parser.parse_args(argv)

    if args.root:
        sys.path.insert(0, args.root)

    exclude_set = set(args.exclude.split(","))

    for package in args.package:
        assert "." not in package, f"{package}: give top level package name"

        filename = __import__(package).__file__
        assert filename is not None, f"{package}: namespace packages not supported"
        assert filename.endswith("__init__.py"), f"{package}: single modules not supported"

        base_path = Path(filename).parents[1]
        for name in sorted(find_importable_names(base_path, package, exclude_set)):
            __import__(name)
            print(f"{name} ok")
