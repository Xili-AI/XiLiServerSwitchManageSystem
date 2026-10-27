"""Flask extension instances and shared initialization."""
import sqlite3

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


@event.listens_for(Engine, "connect")
def configure_sqlite_connection(dbapi_connection, connection_record):
    """Enable WAL and foreign keys for SQLite connections."""
    if not isinstance(dbapi_connection, sqlite3.Connection):
        return
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        # Some bind mounts (for example Windows drives) do not support WAL.
        # The default rollback journal is still safe for this single-instance app.
        pass
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_extensions(app) -> None:
    """Bind extensions to the Flask application."""
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", [])}},
        supports_credentials=False,
    )

    app.teardown_appcontext(remove_db_session)


def remove_db_session(exception=None):
    """Release the scoped session at the end of each request/app context."""
    db.session.remove()
