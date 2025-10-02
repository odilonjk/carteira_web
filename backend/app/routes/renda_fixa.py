"""Routes for renda fixa insights and listings."""
from __future__ import annotations

from flask import Blueprint, Flask, jsonify

blueprint = Blueprint("renda_fixa", __name__, url_prefix="/renda-fixa")


@blueprint.get("")
def list_renda_fixa() -> tuple[dict[str, object], int]:
    """Return placeholder data split by fixed-income types."""
    payload = {"items": {"cdb": [], "debentures": [], "tesouro_direto": [], "lci": [], "lca": []}}
    return jsonify(payload), 200


def register(app: Flask) -> None:
    """Register the blueprint on the Flask app."""
    app.register_blueprint(blueprint)
