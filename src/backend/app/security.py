"""JWT wiring and authorization decorators."""
from functools import wraps

from flask import jsonify
from flask_jwt_extended import current_user, jwt_required

from app.errors import ForbiddenError
from app.extensions import db
from models.user import User


def load_user(jwt_header, jwt_payload):
    """Load the active user referenced by a JWT subject."""
    user_id = jwt_payload.get("sub")
    if not user_id:
        return None
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def is_token_revoked(jwt_header, jwt_payload) -> bool:
    """Revoke tokens after account changes or an explicit logout."""
    user = load_user(jwt_header, jwt_payload)
    if user is None or not user.is_active:
        return True
    return int(jwt_payload.get("ver", -1)) != int(user.token_version)


def unauthorized_response(reason):
    """Return the unified envelope for missing credentials."""
    return jsonify({"code": 401, "message": "请先登录后再操作"}), 401


def invalid_token_response(reason):
    """Return the unified envelope for malformed tokens."""
    return jsonify({"code": 401, "message": "登录凭证无效，请重新登录"}), 401


def expired_token_response(jwt_header, jwt_payload):
    """Return the unified envelope for expired tokens."""
    return jsonify({"code": 401, "message": "登录已过期，请重新登录"}), 401


def revoked_token_response(jwt_header, jwt_payload):
    """Return the unified envelope for revoked tokens."""
    return jsonify({"code": 401, "message": "登录状态已失效，请重新登录"}), 401


def user_lookup_error_response(jwt_header, jwt_payload):
    """Return the unified envelope when the JWT subject no longer exists."""
    return jsonify({"code": 401, "message": "账号不存在或已被禁用"}), 401


def register_jwt_callbacks(jwt) -> None:
    """Attach identity and error callbacks to the JWT manager."""
    jwt.user_lookup_loader(load_user)
    jwt.token_in_blocklist_loader(is_token_revoked)
    jwt.unauthorized_loader(unauthorized_response)
    jwt.invalid_token_loader(invalid_token_response)
    jwt.expired_token_loader(expired_token_response)
    jwt.revoked_token_loader(revoked_token_response)
    jwt.user_lookup_error_loader(user_lookup_error_response)


def admin_required(func):
    """Require a valid JWT belonging to an administrator."""

    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if current_user is None or not current_user.is_admin:
            raise ForbiddenError("需要管理员权限")
        return func(*args, **kwargs)

    return wrapper
