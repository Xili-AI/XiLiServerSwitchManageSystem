"""Nginx routing table generation and synchronization."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import current_app

from models.base import to_local_iso
from models.service import Service
from services.settings_service import SettingsService
from utils.base_utils.atomic_file_util import write_text_atomic
from utils.gateway_util.nginx_config_util import build_hosts_config, build_paths_config

logger = logging.getLogger(__name__)

LAST_SYNC_AT: Optional[datetime] = None


class GatewayService:
    """Own the Nginx snippets that expose registered services."""

    @classmethod
    def dynamic_dir(cls) -> Path:
        """Return the shared dynamic configuration directory."""
        return Path(current_app.config["GATEWAY_DYNAMIC_DIR"])

    @classmethod
    def hosts_file(cls) -> Path:
        """Return the generated host-routing file path."""
        return Path(current_app.config["GATEWAY_HOSTS_FILE"])

    @classmethod
    def paths_file(cls) -> Path:
        """Return the generated path-routing file path."""
        return Path(current_app.config["GATEWAY_PATHS_FILE"])

    @classmethod
    def sync(cls) -> dict:
        """Regenerate both Nginx snippets from the current database state."""
        global LAST_SYNC_AT

        settings = SettingsService.get_settings()
        services = (
            Service.query.order_by(Service.sort_order.asc(), Service.created_at.asc()).all()
        )
        hosts_config = build_hosts_config(services, settings)
        paths_config = build_paths_config(services, settings)

        cls.dynamic_dir().mkdir(parents=True, exist_ok=True)
        write_text_atomic(cls.hosts_file(), hosts_config)
        write_text_atomic(cls.paths_file(), paths_config)
        LAST_SYNC_AT = datetime.utcnow()
        enabled_count = len([service for service in services if service.is_enabled])
        logger.info("网关配置已生成，启用服务 %s 个", enabled_count)
        return {
            "synced": True,
            "service_count": enabled_count,
            "synced_at": to_local_iso(LAST_SYNC_AT),
            "hosts_file": str(cls.hosts_file()),
            "paths_file": str(cls.paths_file()),
        }

    @classmethod
    def sync_safe(cls) -> dict:
        """Generate the routing table and return a status without raising."""
        try:
            return cls.sync()
        except Exception as error:
            logger.exception("网关配置生成失败: %s", error)
            return {
                "synced": False,
                "message": str(error),
                "synced_at": to_local_iso(LAST_SYNC_AT) if LAST_SYNC_AT else None,
            }

    @classmethod
    def get_status(cls) -> dict:
        """Return the current gateway synchronization status."""
        hosts_file = cls.hosts_file()
        paths_file = cls.paths_file()
        return {
            "synced": hosts_file.exists() and paths_file.exists(),
            "synced_at": to_local_iso(LAST_SYNC_AT) if LAST_SYNC_AT else None,
            "hosts_file": str(hosts_file),
            "paths_file": str(paths_file),
            "service_count": Service.query.filter_by(is_enabled=True).count(),
        }

    @classmethod
    def get_generated_config(cls) -> dict:
        """Return the generated snippets for the admin settings page."""
        hosts_path = cls.hosts_file()
        paths_path = cls.paths_file()
        return {
            "hosts": hosts_path.read_text(encoding="utf-8") if hosts_path.exists() else "",
            "paths": paths_path.read_text(encoding="utf-8") if paths_path.exists() else "",
        }
