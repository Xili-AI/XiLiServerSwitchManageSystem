"""Shared model helpers."""
from datetime import datetime, timezone
from typing import Optional


def to_local_iso(value: Optional[datetime]) -> Optional[str]:
    """Convert a naive UTC datetime to a local ISO-8601 string."""
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc).astimezone().isoformat()
