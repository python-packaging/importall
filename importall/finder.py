import sys
from pathlib import Path
from typing import Generator, Optional, Set


def find_importable_names(
    path: Path, prefix: str, exclude: Set[str]
) -> Generator[str, None, None]:
    patterns = [f"**/*.py"]
    if sys.platform == "win32":
        patterns.append(f"**/*.dll")
    else:
        # mac does not check dylib?
        patterns.append(f"**/*.*.so")

    for pat in patterns:
        for x in (path / prefix).rglob(pat):
            x = x.relative_to(path)
            if exclude & set(x.parts):
                continue
            name = to_importable_name(x)
            if name is not None:
                yield name


def to_importable_name(path: Path) -> Optional[str]:
    parts = list(path.parts)
    parts[-1] = parts[-1].split(".")[0]
    if parts[-1] == "__init__":
        del parts[-1]
    if parts[-1] == "__main__":
        return None
    return ".".join(parts)
