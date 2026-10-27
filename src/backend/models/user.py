"""User model."""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from models.base import to_local_iso
from models.user_service import UserService


class User(db.Model):
    """Administrator account used by the console."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    token_version = db.Column(db.Integer, default=0, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    service_links = db.relationship(
        "UserService",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def service_ids(self) -> list:
        """Return the granted service IDs (ignored for administrators)."""
        return [link.service_id for link in self.service_links]

    def set_service_ids(self, service_ids) -> None:
        """Replace the granted service list."""
        self.service_links.clear()
        seen = set()
        for service_id in service_ids or []:
            value = str(service_id)
            if value and value not in seen:
                seen.add(value)
                self.service_links.append(UserService(user_id=self.id, service_id=value))

    def can_access(self, service_id: str) -> bool:
        """Administrators see everything; other users need an explicit grant."""
        if self.is_admin:
            return True
        return str(service_id) in self.service_ids

    def set_password(self, password: str) -> None:
        """Hash and store a password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_locked(self) -> bool:
        """Return whether the account is currently locked."""
        return bool(self.locked_until and self.locked_until > datetime.utcnow())

    def to_dict(self) -> dict:
        """Serialize the public user fields."""
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "service_ids": [] if self.is_admin else self.service_ids,
            "last_login_at": to_local_iso(self.last_login_at),
            "created_at": to_local_iso(self.created_at),
            "updated_at": to_local_iso(self.updated_at),
        }
