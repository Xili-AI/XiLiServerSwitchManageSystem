"""Atomic text file writes."""
import os
import tempfile
from pathlib import Path


def write_text_atomic(file_path: Path, content: str, mode: int = 0o644) -> None:
    """Write a UTF-8 text file atomically in its destination directory."""
    target = Path(file_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temp_path = tempfile.mkstemp(
        prefix=f".{target.name}.",
        dir=str(target.parent),
        text=True,
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.chmod(temp_path, mode)
        os.replace(temp_path, target)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
