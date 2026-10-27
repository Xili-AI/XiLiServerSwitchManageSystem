"""Reset the administrator password.

Usage:
    python scripts/reset_admin_password.py <new-password>
"""
import sys

from server import app
from app.extensions import db
from models.user import User
from utils.base_utils.validation_util import validate_password_strength


def main() -> int:
    """Reset the configured administrator password."""
    if len(sys.argv) != 2:
        print("用法: python scripts/reset_admin_password.py <new-password>")
        return 1

    password = validate_password_strength(sys.argv[1])
    with app.app_context():
        username = app.config["ADMIN_USERNAME"]
        user = User.query.filter_by(username=username).first()
        if user is None:
            print(f"管理员 {username} 不存在")
            return 1
        user.set_password(password)
        user.token_version += 1
        db.session.commit()
        print(f"已重置 {username} 的密码，旧登录状态已失效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
