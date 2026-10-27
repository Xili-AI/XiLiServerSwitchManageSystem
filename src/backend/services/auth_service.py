"""Authentication and account services."""
import logging
from datetime import datetime, timedelta

from flask import current_app
from flask_jwt_extended import create_access_token

from app.errors import AuthenticationError, ValidationError
from app.extensions import db
from models.user import User
from services.audit_service import AuditService
from utils.base_utils.rate_limit_util import LoginRateLimiter
from utils.base_utils.validation_util import validate_password_strength

logger = logging.getLogger(__name__)


class AuthService:
    """Login, logout and password management."""

    @classmethod
    def build_rate_limit_key(cls, username: str, ip_address: str) -> str:
        """Build a process-local rate-limit key."""
        return f"{ip_address or 'unknown'}:{str(username or '').strip().lower()}"

    @classmethod
    def login(cls, username: str, password: str, ip_address: str = "") -> dict:
        """Authenticate a user and return a JWT plus the public profile."""
        value = str(username or "").strip()
        secret = str(password or "")
        if not value or not secret:
            raise ValidationError("用户名和密码不能为空")

        key = cls.build_rate_limit_key(value, ip_address)
        LoginRateLimiter.check(
            key,
            current_app.config["LOGIN_RATE_MAX_ATTEMPTS"],
            current_app.config["LOGIN_RATE_WINDOW_SECONDS"],
        )

        user = User.query.filter_by(username=value).first()
        if user is None or not user.is_active:
            LoginRateLimiter.record_failure(key, current_app.config["LOGIN_RATE_WINDOW_SECONDS"])
            AuditService.record(
                action="auth.login_failed",
                resource_type="user",
                detail=f"username={value}",
                ip_address=ip_address,
            )
            db.session.commit()
            raise AuthenticationError("用户名或密码错误")

        if user.is_locked():
            remaining = 1
            if user.locked_until:
                remaining = max(
                    1,
                    int((user.locked_until - datetime.utcnow()).total_seconds() // 60) + 1,
                )
            raise AuthenticationError(f"账号已锁定，请约 {remaining} 分钟后再试")

        if not user.check_password(secret):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= current_app.config["LOGIN_MAX_ATTEMPTS"]:
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=current_app.config["LOGIN_LOCK_MINUTES"]
                )
            LoginRateLimiter.record_failure(
                key, current_app.config["LOGIN_RATE_WINDOW_SECONDS"]
            )
            AuditService.record(
                action="auth.login_failed",
                resource_type="user",
                resource_id=str(user.id),
                detail=f"username={user.username}",
                ip_address=ip_address,
            )
            db.session.commit()
            raise AuthenticationError("用户名或密码错误")

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        token = create_access_token(
            identity=str(user.id),
            additional_claims={"ver": user.token_version, "username": user.username},
        )
        AuditService.record(
            action="auth.login",
            resource_type="user",
            resource_id=str(user.id),
            detail=f"username={user.username}",
            user=user,
            ip_address=ip_address,
        )
        db.session.commit()
        LoginRateLimiter.reset(key)
        logger.info("用户登录成功: %s (%s)", user.username, ip_address)
        return {"token": token, "user": user.to_dict()}

    @classmethod
    def logout(cls, user: User, ip_address: str = "") -> None:
        """Invalidate all currently issued tokens for the user."""
        user.token_version += 1
        AuditService.record(
            action="auth.logout",
            resource_type="user",
            resource_id=str(user.id),
            detail=f"username={user.username}",
            user=user,
            ip_address=ip_address,
        )
        db.session.commit()

    @classmethod
    def change_password(
        cls,
        user: User,
        old_password: str,
        new_password: str,
        ip_address: str = "",
    ) -> None:
        """Change the password and invalidate existing tokens."""
        if not user.check_password(str(old_password or "")):
            raise AuthenticationError("原密码不正确")
        validated = validate_password_strength(new_password)
        user.set_password(validated)
        user.token_version += 1
        AuditService.record(
            action="auth.change_password",
            resource_type="user",
            resource_id=str(user.id),
            detail=f"username={user.username}",
            user=user,
            ip_address=ip_address,
        )
        db.session.commit()
        logger.info("用户修改密码: %s", user.username)

    @classmethod
    def get_profile(cls, user: User) -> dict:
        """Return the public profile."""
        return user.to_dict()
