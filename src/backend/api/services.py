"""Service registry endpoints."""
from flask import Blueprint, request
from flask_jwt_extended import current_user, jwt_required

from app.errors import ValidationError
from app.security import admin_required
from services.service_service import ServiceService, build_service_payload
from services.settings_service import SettingsService
from utils.base_utils.request_util import get_client_ip
from utils.base_utils.response_util import success

services_bp = Blueprint("services", __name__)


def read_json_body() -> dict:
    """Return a validated JSON object from the request body."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("请求体必须是 JSON 对象")
    return data


@services_bp.get("")
@jwt_required()
def list_services():
    """List all registered services and aggregate status."""
    return success(ServiceService.list_services(current_user))


@services_bp.put("/reorder")
@admin_required
def reorder_services():
    """Persist a new display order."""
    data = read_json_body()
    result = ServiceService.reorder_services(
        data.get("ordered_ids", []),
        current_user,
        get_client_ip(request),
    )
    return success(result, "排序已保存")


@services_bp.post("")
@admin_required
def create_service():
    """Register a new service."""
    data = read_json_body()
    result = ServiceService.create_service(data, current_user, get_client_ip(request))
    return success(result, "服务已创建", 201)


@services_bp.get("/<service_id>")
@jwt_required()
def get_service(service_id: str):
    """Return one service."""
    service = ServiceService.get_service(service_id, current_user)
    return success(build_service_payload(service, SettingsService.get_settings()))


@services_bp.put("/<service_id>")
@admin_required
def update_service(service_id: str):
    """Update a service."""
    data = read_json_body()
    result = ServiceService.update_service(
        service_id,
        data,
        current_user,
        get_client_ip(request),
    )
    return success(result, "服务已更新")


@services_bp.delete("/<service_id>")
@admin_required
def delete_service(service_id: str):
    """Delete a service."""
    result = ServiceService.delete_service(
        service_id,
        current_user,
        get_client_ip(request),
    )
    return success(result, "服务已删除")


@services_bp.post("/<service_id>/check")
@admin_required
def check_service(service_id: str):
    """Run an immediate health check."""
    result = ServiceService.check_service(
        service_id,
        current_user,
        get_client_ip(request),
    )
    return success(result, "检测完成")
