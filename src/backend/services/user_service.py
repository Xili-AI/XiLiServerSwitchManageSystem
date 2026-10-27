"""User administration and per-user service grants."""
import re

from app.errors import ConflictError, NotFoundError, ValidationError
from app.extensions import db
from models.service import Service
from models.user import User
from services.audit_service import AuditService
from utils.base_utils.validation_util import validate_password_strength

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,64}$")


class UserService:
    """Manage console accounts. Administrators may edit everything."""

    @staticmethod
    def list_users() -> dict:
        """Return every account with its granted service IDs."""
        users = User.query.order_by(User.id.asc()).all()
        return {"users": [user.to_dict() for user in users]}

    @staticmethod
    def _validate_username(value) -> str:
        username = str(value or "").strip()
        if not USERNAME_PATTERN.match(username):
            raise ValidationError("用户名 3-64 位，只能包含字母、数字、下划线、点和中划线")
        return username

    @staticmethod
    def _normalize_service_ids(raw):
        if raw is None:
            return None
        if not isinstance(raw, list):
            raise ValidationError("service_ids 必须是数组")
        ids = []
        for item in raw:
            value = str(item or "").strip()
            if value and value not in ids:
                ids.append(value)
        if ids:
            existing = {
                service.id
                for service in Service.query.filter(Service.id.in_(ids)).all()
            }
            missing = [value for value in ids if value not in existing]
            if missing:
                raise ValidationError("包含不存在的服务: " + ", ".join(missing[:3]))
        return ids

    @staticmethod
    def _active_admin_count() -> int:
        return User.query.filter_by(is_admin=True, is_active=True).count()

    @classmethod
    def _ensure_admin_remains(cls, user: User) -> None:
        if user.is_admin and user.is_active and cls._active_admin_count() <= 1:
            raise ValidationError("至少要保留一个启用的管理员")

    @classmethod
    def create_user(cls, payload: dict, operator: User, ip_address: str = "") -> dict:
        """Create a user; non-admins only see the services granted here."""
        username = cls._validate_username(payload.get("username"))
        if User.query.filter_by(username=username).first():
            raise ConflictError(f"用户名 {username} 已存在")

        password = validate_password_strength(payload.get("password"))
        is_admin = bool(payload.get("is_admin", False))
        user = User(
            username=username,
            display_name=str(payload.get("display_name") or username).strip()[:100],
            email=str(payload.get("email") or "").strip() or None,
            is_admin=is_admin,
            is_active=bool(payload.get("is_active", True)),
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if not is_admin:
            user.set_service_ids(cls._normalize_service_ids(payload.get("service_ids")) or [])

        AuditService.record(
            action="user.create",
            resource_type="user",
            resource_id=str(user.id),
            detail=f"username={user.username}, admin={is_admin}",
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        return user.to_dict()

    @classmethod
    def update_user(
        cls,
        user_id: int,
        payload: dict,
        operator: User,
        ip_address: str = "",
    ) -> dict:
        """Update profile, role, state, password or service grants."""
        user = db.session.get(User, user_id)
        if user is None:
            raise NotFoundError("用户不存在")

        if "username" in payload:
            username = cls._validate_username(payload.get("username"))
            duplicate = User.query.filter(
                User.username == username, User.id != user.id
            ).first()
            if duplicate:
                raise ConflictError(f"用户名 {username} 已存在")
            user.username = username
        if "display_name" in payload:
            user.display_name = str(payload.get("display_name") or user.username).strip()[:100]
        if "email" in payload:
            user.email = str(payload.get("email") or "").strip() or None

        if "is_admin" in payload:
            next_admin = bool(payload.get("is_admin"))
            if user.is_admin and not next_admin:
                cls._ensure_admin_remains(user)
            user.is_admin = next_admin
        if "is_active" in payload:
            next_active = bool(payload.get("is_active"))
            if user.is_active and not next_active:
                cls._ensure_admin_remains(user)
            user.is_active = next_active

        if payload.get("password"):
            user.set_password(validate_password_strength(payload.get("password")))
            user.token_version += 1

        if user.is_admin:
            user.set_service_ids([])
        elif "service_ids" in payload:
            user.set_service_ids(cls._normalize_service_ids(payload.get("service_ids")) or [])

        AuditService.record(
            action="user.update",
            resource_type="user",
            resource_id=str(user.id),
            detail=f"username={user.username}",
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        return user.to_dict()

    @classmethod
    def delete_user(cls, user_id: int, operator: User, ip_address: str = "") -> dict:
        """Delete an account, but never the current or last enabled admin."""
        user = db.session.get(User, user_id)
        if user is None:
            raise NotFoundError("用户不存在")
        if operator is not None and user.id == operator.id:
            raise ValidationError("不能删除当前登录用户")
        cls._ensure_admin_remains(user)

        username = user.username
        db.session.delete(user)
        AuditService.record(
            action="user.delete",
            resource_type="user",
            resource_id=str(user_id),
            detail=f"username={username}",
            user=operator,
            ip_address=ip_address,
        )
        db.session.commit()
        return {"deleted_id": user_id, "username": username}
