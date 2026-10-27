"""Application configuration.

The only place where environment variables are interpreted. Business modules
must import values from this module instead of calling ``os.environ``.
"""
from datetime import timedelta
from pathlib import Path

from utils.base_utils.env_util import get_env, get_env_bool, get_env_int

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = (
    BACKEND_DIR.parents[1]
    if BACKEND_DIR.name == "backend" and BACKEND_DIR.parent.name == "src"
    else BACKEND_DIR
)

DATA_DIR = Path(get_env("DATA_DIR", str(PROJECT_ROOT / "data")))
LOG_DIR = Path(get_env("LOG_DIR", str(PROJECT_ROOT / "logs")))
RUNTIME_DIR = Path(get_env("RUNTIME_DIR", str(PROJECT_ROOT / "runtime")))
GATEWAY_DYNAMIC_DIR = Path(get_env("GATEWAY_DYNAMIC_DIR", str(RUNTIME_DIR / "nginx")))
GATEWAY_HOSTS_FILE = GATEWAY_DYNAMIC_DIR / "hosts.conf"
GATEWAY_PATHS_FILE = GATEWAY_DYNAMIC_DIR / "paths.conf"

DATABASE_URI = get_env(
    "DATABASE_URL",
    f"sqlite:///{(DATA_DIR / 'serverswitchmanagesystem.db').as_posix()}",
)

if DATABASE_URI.startswith("sqlite"):
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False, "timeout": 30},
    }
else:
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": get_env_int("DB_POOL_RECYCLE", 3600),
        "pool_size": get_env_int("DB_POOL_SIZE", 10),
    }

SITE_NAME = get_env("SITE_NAME", "矽励科技服务网关管理系统")
SITE_VERSION = "1.0.0"

SECRET_KEY = get_env("SECRET_KEY", "xiliserverswitchmanagesystem-dev-secret-change-me-32chars")
JWT_SECRET_KEY = get_env("JWT_SECRET_KEY", "xiliserverswitchmanagesystem-dev-jwt-secret-change-me-32chars")
JWT_ACCESS_TOKEN_EXPIRES_HOURS = get_env_int("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 12)
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=JWT_ACCESS_TOKEN_EXPIRES_HOURS)

ADMIN_USERNAME = get_env("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = get_env("ADMIN_PASSWORD", "ChangeMe_123!")
ADMIN_DISPLAY_NAME = get_env("ADMIN_DISPLAY_NAME", "系统管理员")
ADMIN_EMAIL = get_env("ADMIN_EMAIL", "admin@xili-ai.com")

CORS_ORIGINS = [
    origin.strip()
    for origin in get_env(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8080",
    ).split(",")
    if origin.strip()
]

MAX_CONTENT_LENGTH = get_env_int("MAX_CONTENT_LENGTH_MB", 50) * 1024 * 1024

FLASK_HOST = get_env("FLASK_HOST", "0.0.0.0")
FLASK_PORT = get_env_int("FLASK_PORT", 5000)
FLASK_DEBUG = get_env_bool("FLASK_DEBUG", False)
FLASK_USE_RELOADER = get_env_bool("FLASK_USE_RELOADER", False)

LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
LOG_FILE = Path(get_env("LOG_FILE", str(LOG_DIR / "backend.log")))

BASE_DOMAIN = get_env("BASE_DOMAIN", "localhost")
PUBLIC_SCHEME = get_env("PUBLIC_SCHEME", "http")
PUBLIC_PORT = get_env("PUBLIC_PORT", "8080")
HEALTH_INTERVAL_SECONDS = get_env_int("HEALTH_INTERVAL_SECONDS", 20)
HEALTH_TIMEOUT_SECONDS = get_env_int("HEALTH_TIMEOUT_SECONDS", 4)
SKIP_TLS_VERIFY = get_env_bool("SKIP_TLS_VERIFY", False)
SEED_DEMO_SERVICES = get_env_bool("SEED_DEMO_SERVICES", False)
START_HEALTH_WORKER = get_env_bool("START_HEALTH_WORKER", True)

# Shared secret with the wstunnel client. It authenticates the read-only
# /api/tunnel/endpoints feed (loopback port map) and is the same value the
# gateway uses for --restrict-http-upgrade-path-prefix.
TUNNEL_SECRET = get_env("TUNNEL_SECRET", "")
TUNNEL_LOCAL_PORT_BASE = get_env_int("TUNNEL_LOCAL_PORT_BASE", 18100)

LOGIN_MAX_ATTEMPTS = get_env_int("LOGIN_MAX_ATTEMPTS", 5)
LOGIN_LOCK_MINUTES = get_env_int("LOGIN_LOCK_MINUTES", 15)
LOGIN_RATE_WINDOW_SECONDS = get_env_int("LOGIN_RATE_WINDOW_SECONDS", 300)
LOGIN_RATE_MAX_ATTEMPTS = get_env_int("LOGIN_RATE_MAX_ATTEMPTS", 10)

DEFAULT_SETTINGS = {
    "base_domain": BASE_DOMAIN,
    "public_scheme": PUBLIC_SCHEME,
    "public_port": PUBLIC_PORT,
    "health_interval": HEALTH_INTERVAL_SECONDS,
    "skip_tls_verify": SKIP_TLS_VERIFY,
    "site_name": SITE_NAME,
}


def load_flask_config(app) -> None:
    """Copy module constants into the Flask configuration object."""
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        JWT_SECRET_KEY=JWT_SECRET_KEY,
        JWT_ACCESS_TOKEN_EXPIRES=JWT_ACCESS_TOKEN_EXPIRES,
        JWT_TOKEN_LOCATION=["headers"],
        JWT_HEADER_TYPE="Bearer",
        SQLALCHEMY_DATABASE_URI=DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS=SQLALCHEMY_ENGINE_OPTIONS,
        CORS_ORIGINS=CORS_ORIGINS,
        MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH,
        SITE_NAME=SITE_NAME,
        SITE_VERSION=SITE_VERSION,
        BASE_DOMAIN=BASE_DOMAIN,
        PUBLIC_SCHEME=PUBLIC_SCHEME,
        PUBLIC_PORT=PUBLIC_PORT,
        HEALTH_INTERVAL_SECONDS=HEALTH_INTERVAL_SECONDS,
        HEALTH_TIMEOUT_SECONDS=HEALTH_TIMEOUT_SECONDS,
        SKIP_TLS_VERIFY=SKIP_TLS_VERIFY,
        SEED_DEMO_SERVICES=SEED_DEMO_SERVICES,
        START_HEALTH_WORKER=START_HEALTH_WORKER,
        TUNNEL_SECRET=TUNNEL_SECRET,
        TUNNEL_LOCAL_PORT_BASE=TUNNEL_LOCAL_PORT_BASE,
        LOGIN_MAX_ATTEMPTS=LOGIN_MAX_ATTEMPTS,
        LOGIN_LOCK_MINUTES=LOGIN_LOCK_MINUTES,
        LOGIN_RATE_WINDOW_SECONDS=LOGIN_RATE_WINDOW_SECONDS,
        LOGIN_RATE_MAX_ATTEMPTS=LOGIN_RATE_MAX_ATTEMPTS,
        DATA_DIR=str(DATA_DIR),
        LOG_DIR=str(LOG_DIR),
        LOG_FILE=str(LOG_FILE),
        RUNTIME_DIR=str(RUNTIME_DIR),
        GATEWAY_DYNAMIC_DIR=str(GATEWAY_DYNAMIC_DIR),
        GATEWAY_HOSTS_FILE=str(GATEWAY_HOSTS_FILE),
        GATEWAY_PATHS_FILE=str(GATEWAY_PATHS_FILE),
        ADMIN_USERNAME=ADMIN_USERNAME,
        ADMIN_PASSWORD=ADMIN_PASSWORD,
        ADMIN_DISPLAY_NAME=ADMIN_DISPLAY_NAME,
        ADMIN_EMAIL=ADMIN_EMAIL,
        FLASK_DEBUG=FLASK_DEBUG,
        FLASK_USE_RELOADER=FLASK_USE_RELOADER,
        LOG_LEVEL=LOG_LEVEL,
    )
