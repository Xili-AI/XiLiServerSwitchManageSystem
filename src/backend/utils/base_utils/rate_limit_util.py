"""In-memory login rate limiting.

The product runs as a single backend instance, so a process-local sliding
window is sufficient and keeps the deployment dependency-free.
"""
import threading
import time
from collections import defaultdict

from app.errors import RateLimitError


class LoginRateLimiter:
    """Track failed login attempts per account/IP key."""

    attempts = defaultdict(list)
    lock = threading.Lock()

    @classmethod
    def prune(cls, key: str, window_seconds: int) -> None:
        """Drop timestamps outside the current window."""
        cutoff = time.monotonic() - window_seconds
        cls.attempts[key] = [stamp for stamp in cls.attempts[key] if stamp >= cutoff]
        if not cls.attempts[key]:
            cls.attempts.pop(key, None)

    @classmethod
    def check(cls, key: str, max_attempts: int, window_seconds: int) -> None:
        """Raise when the key has exceeded the allowed attempts."""
        with cls.lock:
            cls.prune(key, window_seconds)
            if len(cls.attempts.get(key, [])) >= max_attempts:
                raise RateLimitError("登录尝试过于频繁，请稍后再试")

    @classmethod
    def record_failure(cls, key: str, window_seconds: int) -> None:
        """Record a failed attempt."""
        with cls.lock:
            cls.prune(key, window_seconds)
            cls.attempts[key].append(time.monotonic())

    @classmethod
    def reset(cls, key: str) -> None:
        """Clear attempts after a successful login."""
        with cls.lock:
            cls.attempts.pop(key, None)
