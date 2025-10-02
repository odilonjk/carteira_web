"""Routes for renda variavel insights and listings."""
from __future__ import annotations

from flask import Blueprint, Flask, jsonify

blueprint = Blueprint("renda_variavel", __name__, url_prefix="/renda-variavel")


@blueprint.get("")
def list_renda_variavel() -> tuple[dict[str, object], int]:
    """Return placeholder data split by asset types."""
    payload = {"items": {"fiis": [], "acoes": [], "stocks": [], "etfs": [], "reits": []}}
    return jsonify(payload), 200


def register(app: Flask) -> None:
    """Register the blueprint on the Flask app."""
    app.register_blueprint(blueprint)
