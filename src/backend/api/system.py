"""System information, settings and audit endpoints."""
from flask import Blueprint, request
from flask_jwt_extended import current_user, jwt_required

from app.errors import GatewayError, ValidationError
from app.security import admin_required
from services.audit_service import AuditService
from services.gateway_service import GatewayService
from services.service_service import ServiceService
from services.settings_service import SettingsService
from utils.base_utils.request_util import get_client_ip
from utils.base_utils.response_util import success

system_bp = Blueprint("system", __name__)


def read_json_body() -> dict:
    """Return a validated JSON object from the request body."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("请求体必须是 JSON 对象")
    return data


@system_bp.get("/info")
@jwt_required()
def system_info():
    """Return dashboard counters, gateway status and recent activity."""
    registry = ServiceService.list_services()
    return success(
        {
            "services": registry["services"],
            "stats": registry["stats"],
            "settings": SettingsService.get_settings(),
            "gateway": GatewayService.get_status(),
            "recent_logs": AuditService.list_recent(12),
        }
    )


@system_bp.get("/settings")
@jwt_required()
def get_settings():
    """Return the editable gateway settings."""
    return success(SettingsService.get_settings())


@system_bp.put("/settings")
@admin_required
def update_settings():
    """Update gateway settings and regenerate routing."""
    data = read_json_body()
    settings = SettingsService.update_settings(
        data,
        current_user,
        get_client_ip(request),
    )
    gateway = GatewayService.sync_safe()
    return success({"settings": settings, "gateway": gateway}, "设置已保存")


@system_bp.post("/gateway/sync")
@admin_required
def sync_gateway():
    """Force a routing-table regeneration."""
    result = GatewayService.sync_safe()
    if not result.get("synced"):
        raise GatewayError(result.get("message", "网关配置同步失败"))
    return success(result, "网关配置已同步")


@system_bp.get("/gateway/config")
@admin_required
def gateway_config():
    """Return the generated Nginx snippets for troubleshooting."""
    return success(GatewayService.get_generated_config())


@system_bp.get("/audit-logs")
@admin_required
def audit_logs():
    """Return recent audit entries."""
    try:
        limit = int(request.args.get("limit", "20"))
    except ValueError:
        limit = 20
    return success({"logs": AuditService.list_recent(limit)})
