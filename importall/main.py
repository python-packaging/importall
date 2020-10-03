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
    parser.add_argument("package", metavar="PACKAGE", help="Name of package to test")
    args = parser.parse_args(argv)

    assert "." not in args.package, "give top level package name"
    if args.root:
        sys.path.insert(0, args.root)

    filename = __import__(args.package).__file__
    assert filename is not None, "namespace packages not supported"
    assert filename.endswith("__init__.py"), "single modules not supported"

    exclude_set = set(args.exclude.split(","))
    base_path = Path(filename).parent.parent
    for name in sorted(find_importable_names(base_path, args.package, exclude_set)):
        __import__(name)
        print(f"{name} ok")
