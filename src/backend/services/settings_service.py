"""Runtime gateway settings."""
from datetime import datetime
from typing import Optional

from flask import current_app

from app.extensions import db
from models.setting import AppSetting
from models.user import User
from services.audit_service import AuditService
from utils.base_utils.validation_util import normalize_settings_payload

SETTING_KEYS = {
    "base_domain",
    "public_scheme",
    "public_port",
    "health_interval",
    "skip_tls_verify",
    "site_name",
}


def config_defaults() -> dict:
    """Build default settings from the application configuration."""
    return {
        "base_domain": current_app.config["BASE_DOMAIN"],
        "public_scheme": current_app.config["PUBLIC_SCHEME"],
        "public_port": current_app.config["PUBLIC_PORT"],
        "health_interval": current_app.config["HEALTH_INTERVAL_SECONDS"],
        "skip_tls_verify": current_app.config["SKIP_TLS_VERIFY"],
        "site_name": current_app.config["SITE_NAME"],
    }


def decode_setting(key: str, value: str):
    """Convert a persisted string into its typed value."""
    if key == "health_interval":
        try:
            return int(value)
        except (TypeError, ValueError):
            return current_app.config["HEALTH_INTERVAL_SECONDS"]
    if key == "skip_tls_verify":
        return str(value).lower() == "true"
    return value


def encode_setting(value) -> str:
    """Convert a typed setting value into its stored string."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class SettingsService:
    """Read and update persisted runtime settings."""

    @classmethod
    def get_settings(cls) -> dict:
        """Return defaults overlaid with database overrides."""
        settings = config_defaults()
        for row in AppSetting.query.all():
            if row.key in SETTING_KEYS:
                settings[row.key] = decode_setting(row.key, row.value)
        return settings

    @classmethod
    def get_public_settings(cls) -> dict:
        """Return the settings safe to expose before login."""
        settings = cls.get_settings()
        return {
            "site_name": settings["site_name"],
            "version": current_app.config["SITE_VERSION"],
            "base_domain": settings["base_domain"],
            "public_scheme": settings["public_scheme"],
            "public_port": settings["public_port"],
        }

    @classmethod
    def update_settings(
        cls,
        payload: dict,
        operator: User,
        ip_address: str = "",
    ) -> dict:
        """Validate, persist and return updated settings."""
        normalized = normalize_settings_payload(payload)
        for key, value in normalized.items():
            row = db.session.get(AppSetting, key)
            if row is None:
                row = AppSetting(key=key, value=encode_setting(value))
                db.session.add(row)
            else:
                row.value = encode_setting(value)
                row.updated_at = datetime.utcnow()
        AuditService.record(
            action="settings.update",
            resource_type="settings",
            detail=",".join(sorted(normalized.keys())),
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        return cls.get_settings()
