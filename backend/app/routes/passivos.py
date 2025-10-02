"""Routes for managing passivos."""
from __future__ import annotations

from flask import Blueprint, Flask, jsonify

blueprint = Blueprint("passivos", __name__, url_prefix="/passivos")


@blueprint.get("")
def list_passivos() -> tuple[dict[str, object], int]:
    """Return placeholder data for passivos."""
    return jsonify({"items": [], "insights": {}}), 200


def register(app: Flask) -> None:
    """Register the blueprint on the Flask app."""
    app.register_blueprint(blueprint)
