"""Service registry model."""
import uuid
from datetime import datetime

from app.extensions import db
from models.base import to_local_iso


class Service(db.Model):
    """An internal HTTP service exposed through the single gateway."""

    __tablename__ = "services"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(32), unique=True, nullable=False, index=True)
    target_url = db.Column(db.String(500), nullable=False)
    entry_path = db.Column(db.String(200), default="", nullable=False)
    strip_prefix = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.String(200), default="", nullable=False)
    color = db.Column(db.String(16), default="#5fd3f3", nullable=False)
    icon = db.Column(db.String(40), default="server", nullable=False)
    mode = db.Column(db.String(16), default="auto", nullable=False)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    is_online = db.Column(db.Boolean, nullable=True)
    last_checked_at = db.Column(db.DateTime, nullable=True)
    latency_ms = db.Column(db.Integer, nullable=True)
    last_error = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        """Serialize persisted service fields."""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "target_url": self.target_url,
            "entry_path": self.entry_path,
            "strip_prefix": self.strip_prefix,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "mode": self.mode,
            "is_enabled": self.is_enabled,
            "sort_order": self.sort_order,
            "is_online": self.is_online,
            "last_checked_at": to_local_iso(self.last_checked_at),
            "latency_ms": self.latency_ms,
            "last_error": self.last_error,
            "created_at": to_local_iso(self.created_at),
            "updated_at": to_local_iso(self.updated_at),
        }
