"""Flask application factory."""
import logging
import os
from datetime import datetime

from flask import Flask, request
from sqlalchemy import inspect, text

import models  # noqa: F401 - registers all SQLAlchemy models
from app.config import load_flask_config
from app.errors import ValidationError, register_error_handlers
from app.extensions import db, init_extensions, jwt
from app.logger import setup_logging
from app.security import register_jwt_callbacks
from models.service import Service
from models.user import User
from services.gateway_service import GatewayService
from services.health_service import HealthService
from utils.base_utils.validation_util import (
    normalize_service_payload,
    validate_password_strength,
)

logger = logging.getLogger(__name__)


def apply_api_headers(response):
    """Add safe defaults to API responses."""
    if request.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
    return response


def register_blueprints(app) -> None:
    """Register all route groups."""
    from api.auth import auth_bp
    from api.root import root_bp
    from api.services import services_bp
    from api.system import system_bp
    from api.users import users_bp

    app.register_blueprint(root_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(services_bp, url_prefix="/api/services")
    app.register_blueprint(system_bp, url_prefix="/api/system")
    app.register_blueprint(users_bp, url_prefix="/api/users")


def seed_admin(app) -> None:
    """Create the initial administrator if the database is empty."""
    username = app.config["ADMIN_USERNAME"]
    password = app.config["ADMIN_PASSWORD"]
    existing = User.query.filter_by(username=username).first()
    if existing is not None:
        existing.is_admin = True
        db.session.commit()
        return

    try:
        validate_password_strength(password)
    except ValidationError as error:
        logger.warning("管理员初始密码不符合强度要求: %s", error)

    admin = User(
        username=username,
        display_name=app.config["ADMIN_DISPLAY_NAME"],
        email=app.config["ADMIN_EMAIL"],
        is_admin=True,
        is_active=True,
        token_version=0,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    logger.info("已创建初始管理员: %s", username)


def seed_demo_services(app) -> None:
    """Create example Portainer and File Browser entries on first run."""
    if not app.config["SEED_DEMO_SERVICES"]:
        return
    if Service.query.count() > 0:
        return

    demos = [
        {
            "name": "Portainer",
            "slug": "portainer",
            "target_url": "http://portainer:9000",
            "description": "容器启停、日志与终端",
            "color": "#13b5ea",
            "icon": "container",
            "mode": "path",
            "strip_prefix": True,
            "is_enabled": True,
            "sort_order": 10,
        },
        {
            "name": "File Browser",
            "slug": "files",
            "target_url": "http://filebrowser:80",
            "description": "内网文件管理",
            "color": "#22c55e",
            "icon": "folder",
            "mode": "path",
            "strip_prefix": False,
            "is_enabled": True,
            "sort_order": 20,
        },
    ]
    for demo in demos:
        normalized = normalize_service_payload(demo)
        db.session.add(Service(**normalized))
    db.session.commit()
    logger.info("已写入 %s 个示例服务", len(demos))


def apply_schema_updates(app) -> None:
    """Apply additive schema changes for existing installations."""
    with app.app_context():
        inspector = inspect(db.engine)
        if "services" not in inspector.get_table_names():
            return
        columns = {column["name"] for column in inspector.get_columns("services")}
        with db.engine.begin() as connection:
            if "entry_path" not in columns:
                connection.execute(
                    text(
                        "ALTER TABLE services ADD COLUMN entry_path "
                        "VARCHAR(200) NOT NULL DEFAULT ''"
                    )
                )
                logger.info("数据库迁移完成: services.entry_path")
            if "strip_prefix" not in columns:
                connection.execute(
                    text(
                        "ALTER TABLE services ADD COLUMN strip_prefix "
                        "BOOLEAN NOT NULL DEFAULT 1"
                    )
                )
                logger.info("数据库迁移完成: services.strip_prefix")


def initialize_database(app) -> None:
    """Create tables, seed defaults and regenerate the gateway config."""
    with app.app_context():
        db.create_all()
        apply_schema_updates(app)
        seed_admin(app)
        seed_demo_services(app)
        GatewayService.sync_safe()
        logger.info(
            "数据库初始化完成: %s",
            app.config["SQLALCHEMY_DATABASE_URI"].split("://", 1)[0],
        )


def start_background_workers(app) -> None:
    """Start the health worker once, outside the reloader parent process."""
    is_reloader_parent = (
        app.config.get("FLASK_DEBUG")
        and app.config.get("FLASK_USE_RELOADER")
        and os.environ.get("WERKZEUG_RUN_MAIN") is None
    )
    if (
        app.config.get("START_HEALTH_WORKER")
        and not app.config.get("TESTING")
        and not is_reloader_parent
    ):
        HealthService.start_worker(app)


def create_app(test_config=None):
    """Create and configure the Flask application."""
    setup_logging()
    app = Flask(__name__)
    app.json.ensure_ascii = False

    load_flask_config(app)
    if test_config:
        app.config.update(test_config)

    init_extensions(app)
    register_jwt_callbacks(jwt)
    register_blueprints(app)
    register_error_handlers(app)
    app.after_request(apply_api_headers)

    initialize_database(app)
    start_background_workers(app)

    logger.info(
        "矽励科技服务网关管理系统 已启动 (%s) at %s",
        app.config["SITE_VERSION"],
        datetime.utcnow().isoformat(timespec="seconds"),
    )
    return app
