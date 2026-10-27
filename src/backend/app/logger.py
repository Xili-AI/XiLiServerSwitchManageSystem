"""Centralized logging setup."""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app import config


def setup_logging() -> None:
    """Configure console and rotating-file logging once per process."""
    root = logging.getLogger()
    if getattr(root, "xili_configured", False):
        return

    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()

    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    root.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    Path(config.LOG_DIR).mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    root.xili_configured = True
