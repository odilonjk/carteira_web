"""Homepage and health-check endpoints."""
from __future__ import annotations

from flask import Blueprint, Flask, jsonify

blueprint = Blueprint("home", __name__)


@blueprint.get("/")
def index() -> tuple[dict[str, str], int]:
    """Return a simple heartbeat payload."""
    return jsonify({"status": "ok"}), 200


def register(app: Flask) -> None:
    """Register the blueprint on the Flask app."""
    app.register_blueprint(blueprint)
