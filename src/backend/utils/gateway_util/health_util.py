"""HTTP health probes for registered services."""
import time

import requests


def probe_http(target_url: str, timeout_seconds: int, verify_tls: bool) -> dict:
    """Probe an HTTP target and return a normalized status dictionary.

    Any response below HTTP 500 means the service process is reachable. A 401
    or 403 still proves the application is alive, so it counts as online.
    """
    started_at = time.perf_counter()
    try:
        response = requests.get(
            target_url,
            timeout=max(1, timeout_seconds),
            verify=verify_tls,
            allow_redirects=False,
            stream=True,
            headers={"User-Agent": "XiLiServerSwitchManageSystem/1.0 health-check"},
        )
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        is_online = response.status_code < 500
        response.close()
        return {
            "is_online": is_online,
            "latency_ms": latency_ms,
            "last_error": None if is_online else f"HTTP {response.status_code}",
        }
    except requests.RequestException as error:
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        return {
            "is_online": False,
            "latency_ms": latency_ms,
            "last_error": str(error)[:255],
        }
