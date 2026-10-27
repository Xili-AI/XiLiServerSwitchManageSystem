"""Backend entrypoint.

Loads the development or production environment file before importing the
application factory, then exposes ``app`` for WSGI servers.
"""
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

os.environ.setdefault("PYTHONUNBUFFERED", "1")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = (
    BACKEND_DIR.parents[1]
    if BACKEND_DIR.name == "backend" and BACKEND_DIR.parent.name == "src"
    else BACKEND_DIR
)


def load_environment() -> None:
    """Load local env files unless running inside Docker."""
    if Path("/.dockerenv").exists():
        logging.getLogger(__name__).info("Docker 环境，使用容器注入的环境变量")
        return

    env_name = os.environ.get("APP_ENV", "dev")
    debugmode_path = PROJECT_ROOT / "debugmode"
    if debugmode_path.exists():
        env_name = "dev" if debugmode_path.read_text(encoding="utf-8").strip() == "1" else "pro"

    env_path = PROJECT_ROOT / f"{env_name}.backend.env"
    if not env_path.exists():
        raise FileNotFoundError(f"缺少环境配置文件: {env_path}")
    load_dotenv(env_path, override=False)
    logging.getLogger(__name__).info("已加载环境配置: %s", env_path)


load_environment()

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import FLASK_DEBUG, FLASK_HOST, FLASK_PORT, FLASK_USE_RELOADER  # noqa: E402
from app.factory import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG,
        use_reloader=FLASK_USE_RELOADER,
        threaded=True,
    )
