"""Request metadata helpers."""


def get_client_ip(request) -> str:
    """Resolve the client IP, honoring the gateway's forwarding headers."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.headers.get("X-Real-IP", "") or request.remote_addr or ""
