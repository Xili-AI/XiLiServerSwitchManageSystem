"""Unified JSON response helpers."""
from flask import jsonify


def success(data=None, message: str = "操作成功", status_code: int = 200):
    """Return a successful response envelope."""
    payload = {"code": status_code, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error(message: str, status_code: int = 400, data=None):
    """Return an error response envelope."""
    payload = {"code": status_code, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code
