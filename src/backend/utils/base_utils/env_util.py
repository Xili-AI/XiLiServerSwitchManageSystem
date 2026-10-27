"""Environment variable parsing helpers.

All runtime configuration is read through ``app.config``. This module is the
single low-level entry used by that configuration layer.
"""
import os


def get_env(name: str, default: str = "") -> str:
    """Return a trimmed environment value or the provided default."""
    value = os.environ.get(name)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


def get_env_int(name: str, default: int) -> int:
    """Return an integer environment value, falling back on invalid input."""
    value = get_env(name, "")
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_env_bool(name: str, default: bool = False) -> bool:
    """Return a boolean environment value."""
    value = get_env(name, "").lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default
