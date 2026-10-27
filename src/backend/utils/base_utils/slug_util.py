"""Service slug helpers."""
import re

SLUG_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$")

RESERVED_SLUGS = {
    "api",
    "p",
    "static",
    "assets",
    "health",
    "healthz",
    "login",
    "logout",
    "admin",
    "panel",
    "portal",
    "www",
    "ws",
    "socket",
}


def slugify(value: str) -> str:
    """Convert a display name into a URL-safe slug."""
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:32].rstrip("-")


def is_valid_slug(value: str) -> bool:
    """Return whether a slug matches the public URL contract."""
    return bool(SLUG_PATTERN.match(value or ""))
