"""Authentication endpoints."""
from flask import Blueprint, request
from flask_jwt_extended import current_user, jwt_required

from app.errors import ValidationError
from services.auth_service import AuthService
from utils.base_utils.request_util import get_client_ip
from utils.base_utils.response_util import success

auth_bp = Blueprint("auth", __name__)


def read_json_body() -> dict:
    """Return a validated JSON object from the request body."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("请求体必须是 JSON 对象")
    return data


@auth_bp.post("/login")
def login():
    """Authenticate and return a JWT."""
    data = read_json_body()
    result = AuthService.login(
        data.get("username", ""),
        data.get("password", ""),
        get_client_ip(request),
    )
    return success(result, "登录成功")


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """Invalidate all tokens issued to the current user."""
    AuthService.logout(current_user, get_client_ip(request))
    return success(message="已退出登录")


@auth_bp.get("/profile")
@jwt_required()
def profile():
    """Return the current user's profile."""
    return success(AuthService.get_profile(current_user))


@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    """Change the current user's password."""
    data = read_json_body()
    AuthService.change_password(
        current_user,
        data.get("old_password", ""),
        data.get("new_password", ""),
        get_client_ip(request),
    )
    return success(message="密码已修改，请重新登录")
