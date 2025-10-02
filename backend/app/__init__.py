"""Application factory for the Flask backend."""
from __future__ import annotations

from flask import Flask
from dotenv import load_dotenv

from .config import load_config


def create_app(env: str | None = None) -> Flask:
    """Create and configure a Flask application instance."""
    load_dotenv()

    app = Flask(__name__)
    app.config.from_mapping(load_config(env))

    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints grouped by domain."""
    from .routes import home, passivos, renda_fixa, renda_variavel

    home.register(app)
    passivos.register(app)
    renda_variavel.register(app)
    renda_fixa.register(app)
