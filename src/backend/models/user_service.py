"""Per-user service access grants."""
from app.extensions import db


class UserService(db.Model):
    """Join table: which services a non-admin user may open."""

    __tablename__ = "user_services"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    service_id = db.Column(db.String(36), primary_key=True)
