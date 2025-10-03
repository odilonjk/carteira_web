"""Application factory for the Flask backend."""
from __future__ import annotations

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from .config import load_config
from .repositories import FirestoreGateway, TinyDbGateway


def create_app(env: str | None = None) -> Flask:
    """Create and configure a Flask application instance."""
    load_dotenv()

    app = Flask(__name__)
    app.config.from_mapping(load_config(env))

    _configure_data_gateway(app)

    cors_origins = app.config.get("CORS_ORIGINS")
    cors_resources = {r"/*": {"origins": cors_origins}} if cors_origins else None
    cors_kwargs = {"resources": cors_resources} if cors_resources else {}
    CORS(app, **cors_kwargs)

    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints grouped by domain."""
    from .routes import home, passivos, renda_fixa, renda_variavel

    home.register(app)
    passivos.register(app)
    renda_variavel.register(app)
    renda_fixa.register(app)


def _configure_data_gateway(app: Flask) -> None:
    """Attach a data gateway factory based on configuration."""

    backend = (app.config.get("DATA_BACKEND") or "firestore").lower()

    if backend == "tinydb":
        tinydb_path = app.config.get("TINYDB_FILE") or "var/tinydb.json"
        gateway = TinyDbGateway.from_file(tinydb_path)
    else:
        gateway = FirestoreGateway.from_settings(
            project_id=app.config.get("FIRESTORE_PROJECT_ID")
        )

    app.extensions["data_gateway"] = gateway
    app.config["DATA_GATEWAY_FACTORY"] = lambda gateway=gateway: gateway
