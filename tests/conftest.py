"""Shared pytest fixtures for the backend."""
import pytest

from app.extensions import db
from app.factory import create_app

ADMIN_PASSWORD = "TestPass123"


@pytest.fixture()
def app(tmp_path):
    """Create an isolated application with a temporary SQLite database."""
    database_path = tmp_path / "test.db"
    dynamic_dir = tmp_path / "nginx"
    application = create_app(
        {
            "TESTING": True,
            "START_HEALTH_WORKER": False,
            "SEED_DEMO_SERVICES": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": ADMIN_PASSWORD,
            "GATEWAY_DYNAMIC_DIR": str(dynamic_dir),
            "GATEWAY_HOSTS_FILE": str(dynamic_dir / "hosts.conf"),
            "GATEWAY_PATHS_FILE": str(dynamic_dir / "paths.conf"),
        }
    )
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Return the Flask test client."""
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    """Log in as the seeded administrator and return bearer headers."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200, response.get_json()
    token = response.get_json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def service_payload():
    """Return a valid create-service payload."""
    return {
        "name": "Demo Service",
        "slug": "demo-service",
        "target_url": "http://127.0.0.1:1",
        "description": "pytest service",
        "color": "#5fd3f3",
        "icon": "server",
        "mode": "auto",
        "is_enabled": True,
    }
