"""Public URL construction for services."""
from typing import Optional


def format_port(scheme: str, port: str) -> str:
    """Return a ``:port`` suffix unless the port is the scheme default."""
    value = str(port or "").strip()
    if not value:
        return ""
    if scheme == "http" and value == "80":
        return ""
    if scheme == "https" and value == "443":
        return ""
    if not value.isdigit():
        return ""
    return f":{value}"


def build_public_url(
    slug: str,
    base_domain: str,
    scheme: str,
    port: str,
) -> Optional[str]:
    """Build the subdomain URL, or None when no base domain is configured."""
    domain = str(base_domain or "").strip().strip(".")
    if not domain:
        return None
    return f"{scheme}://{slug}.{domain}{format_port(scheme, port)}/"


def build_path_url(slug: str) -> str:
    """Build the path-based fallback URL."""
    return f"/p/{slug}/"
