"""Audit trail service."""
from typing import Optional

from app.extensions import db
from models.audit_log import AuditLog
from models.user import User


class AuditService:
    """Write and read security-relevant operation logs."""

    @classmethod
    def record(
        cls,
        action: str,
        resource_type: str = "",
        resource_id: str = "",
        detail: str = "",
        user: Optional[User] = None,
        ip_address: str = "",
    ) -> None:
        """Add an audit entry to the current session without committing."""
        entry = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else None,
            action=action,
            resource_type=resource_type or None,
            resource_id=resource_id or None,
            detail=detail or None,
            ip_address=ip_address or None,
        )
        db.session.add(entry)

    @classmethod
    def list_recent(cls, limit: int = 20) -> list:
        """Return the most recent audit entries."""
        safe_limit = max(1, min(int(limit or 20), 100))
        entries = (
            AuditLog.query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
            .limit(safe_limit)
            .all()
        )
        return [entry.to_dict() for entry in entries]
