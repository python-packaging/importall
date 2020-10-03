import sys
from pathlib import Path

import click

from .finder import find_importable_names


@click.command()
@click.option(
    "--exclude", default="tests", help="comma-separated directories to ignore"
)
@click.option("--root", help="Search under this dir")
@click.argument("package")
def main(package: str, exclude: str, root: str) -> None:
    assert "." not in package, "give top level package name"
    if root:
        sys.path.insert(0, root)

    filename = __import__(package).__file__
    assert filename is not None, "namespace packages not supported"
    assert filename.endswith("__init__.py"), "single modules not supported"

    exclude_set = set(exclude.split(","))
    base_path = Path(filename).parent.parent
    for name in sorted(find_importable_names(base_path, package, exclude_set)):
        __import__(name)
        print(f"{name} ok")
