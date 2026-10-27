"""Key/value application settings model."""
from datetime import datetime

from app.extensions import db
from models.base import to_local_iso


class AppSetting(db.Model):
    """A single runtime setting persisted in the database."""

    __tablename__ = "app_settings"

    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        """Serialize the setting row."""
        return {
            "key": self.key,
            "value": self.value,
            "updated_at": to_local_iso(self.updated_at),
        }
