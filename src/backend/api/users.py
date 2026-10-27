"""User administration endpoints (administrators only)."""
from flask import Blueprint, request
from flask_jwt_extended import current_user

from app.errors import ValidationError
from app.security import admin_required
from services.user_service import UserService
from utils.base_utils.request_util import get_client_ip
from utils.base_utils.response_util import success

users_bp = Blueprint("users", __name__)


def read_json_body() -> dict:
    """Return a validated JSON object from the request body."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("请求体必须是 JSON 对象")
    return data


@users_bp.get("")
@admin_required
def list_users():
    """List every console account and its service grants."""
    return success(UserService.list_users())


@users_bp.post("")
@admin_required
def create_user():
    """Create a user account."""
    data = read_json_body()
    result = UserService.create_user(data, current_user, get_client_ip(request))
    return success({"user": result}, "用户已创建", 201)


@users_bp.put("/<int:user_id>")
@admin_required
def update_user(user_id: int):
    """Update profile, role, password or granted services."""
    data = read_json_body()
    result = UserService.update_user(
        user_id, data, current_user, get_client_ip(request)
    )
    return success({"user": result}, "用户已更新")


@users_bp.delete("/<int:user_id>")
@admin_required
def delete_user(user_id: int):
    """Delete a user account."""
    result = UserService.delete_user(user_id, current_user, get_client_ip(request))
    return success(result, "用户已删除")
