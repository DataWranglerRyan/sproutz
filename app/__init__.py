from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text

db = SQLAlchemy()
login_manager = LoginManager()


def ensure_runtime_schema(app):
    """Apply lightweight SQLite column migrations for additive schema changes."""
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not db_uri.startswith("sqlite:"):
        return

    def get_columns(table_name):
        rows = db.session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        return {row[1] for row in rows}

    watering_event_columns = get_columns("watering_event")
    if "previous_last_watered" not in watering_event_columns:
        db.session.execute(text("ALTER TABLE watering_event ADD COLUMN previous_last_watered DATETIME"))
    if "previous_snoozed_until" not in watering_event_columns:
        db.session.execute(text("ALTER TABLE watering_event ADD COLUMN previous_snoozed_until DATETIME"))
    if "is_reverted" not in watering_event_columns:
        db.session.execute(text("ALTER TABLE watering_event ADD COLUMN is_reverted BOOLEAN NOT NULL DEFAULT 0"))
    if "reverted_at" not in watering_event_columns:
        db.session.execute(text("ALTER TABLE watering_event ADD COLUMN reverted_at DATETIME"))

    plant_columns = get_columns("plant")
    if "snoozed_until" not in plant_columns:
        db.session.execute(text("ALTER TABLE plant ADD COLUMN snoozed_until DATETIME"))

    db.session.commit()


def ensure_postgres_schema(app):
    """Create Sproutz's isolated PostgreSQL schema before creating tables."""
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not db_uri.startswith("postgresql+psycopg://"):
        return

    db.session.execute(text("CREATE SCHEMA IF NOT EXISTS sproutz"))
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    required_auth_settings = ("SECRET_KEY", "AUTH_USERNAME", "AUTH_PASSWORD_HASH")
    missing_settings = [
        setting for setting in required_auth_settings if not app.config.get(setting)
    ]
    if missing_settings:
        raise RuntimeError(
            "Missing required authentication settings: "
            + ", ".join(missing_settings)
            + ". Copy .env.example to .env and configure the values."
        )

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.auth import auth
    from app.routes import main

    app.register_blueprint(auth)
    app.register_blueprint(main)

    with app.app_context():
        ensure_postgres_schema(app)
        db.create_all()
        ensure_runtime_schema(app)

    from app.scheduler import start_scheduler

    start_scheduler(app)

    return app
