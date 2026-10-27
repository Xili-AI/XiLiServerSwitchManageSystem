"""Application exceptions and JSON error handlers."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for expected business errors."""

    status_code = 500
    default_message = "服务器内部错误"

    def __init__(self, message: str = "", status_code: int = 0, data=None):
        super().__init__(message or self.default_message)
        if status_code:
            self.status_code = status_code
        self.data = data


class ValidationError(AppError):
    """Invalid user input."""

    status_code = 400
    default_message = "请求参数错误"


class AuthenticationError(AppError):
    """Missing or invalid credentials."""

    status_code = 401
    default_message = "身份验证失败"


class ForbiddenError(AppError):
    """Authenticated user lacks permission."""

    status_code = 403
    default_message = "没有操作权限"


class NotFoundError(AppError):
    """Requested resource does not exist."""

    status_code = 404
    default_message = "资源不存在"


class ConflictError(AppError):
    """Request conflicts with current state."""

    status_code = 409
    default_message = "资源冲突"


class RateLimitError(AppError):
    """Too many requests."""

    status_code = 429
    default_message = "请求过于频繁，请稍后再试"


class GatewayError(AppError):
    """Gateway configuration could not be generated."""

    status_code = 500
    default_message = "网关配置同步失败"


def error_response(message: str, status_code: int, data=None):
    """Build the unified JSON error envelope."""
    payload = {"code": status_code, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def handle_app_error(error: AppError):
    """Handle expected business errors."""
    logger.warning("业务错误 %s: %s", error.status_code, error)
    return error_response(str(error), error.status_code, error.data)


def handle_http_error(error: HTTPException):
    """Handle framework HTTP errors with the same envelope."""
    message = error.description or "请求失败"
    if error.code == 404:
        message = "接口不存在"
    return error_response(message, error.code or 500)


def handle_unexpected_error(error: Exception):
    """Log and mask unexpected exceptions."""
    logger.exception("未处理异常: %s", error)
    return error_response("服务器内部错误", 500)


def register_error_handlers(app) -> None:
    """Attach global error handlers."""
    app.register_error_handler(AppError, handle_app_error)
    app.register_error_handler(HTTPException, handle_http_error)
    app.register_error_handler(Exception, handle_unexpected_error)
