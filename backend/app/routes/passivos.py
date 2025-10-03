"""Routes for managing passivos backed by Firestore."""
from __future__ import annotations

from flask import Blueprint, Flask, current_app, jsonify, request
from pydantic import ValidationError

from ..models import Passivo
from ..repositories import PassivosRepository, PersistenceLayerError

blueprint = Blueprint("passivos", __name__, url_prefix="/passivos")


def _get_repository() -> PassivosRepository:
    factory = current_app.config.get("PASSIVOS_REPOSITORY_FACTORY")
    if callable(factory):
        return factory()  # type: ignore[return-value]

    gateway_factory = current_app.config.get("DATA_GATEWAY_FACTORY")
    if callable(gateway_factory):
        gateway = gateway_factory()
    else:  # pragma: no cover - defensive fallback for misconfiguration
        from ..repositories import FirestoreGateway

        gateway = FirestoreGateway.from_settings(
            project_id=current_app.config.get("FIRESTORE_PROJECT_ID"),
        )
    return PassivosRepository(gateway)


@blueprint.get("")
def list_passivos() -> tuple[dict[str, object], int]:
    """Return passivos stored in Firestore."""

    try:
        repository = _get_repository()
        items = [item.model_dump(mode="json") for item in repository.list()]
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify({"items": items}), 200


@blueprint.post("")
def create_passivo() -> tuple[dict[str, object], int]:
    """Persist a new passivo document based on the payload provided."""

    payload = request.get_json(silent=True) or {}

    try:
        passivo = Passivo.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"errors": exc.errors()}), 400

    repository = _get_repository()
    serialised_payload = passivo.model_dump(mode="json", exclude_none=True)

    try:
        created = repository.create(serialised_payload)
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify({"item": created.model_dump(mode="json")}), 201


def register(app: Flask) -> None:
    """Register the blueprint on the Flask app."""
    app.register_blueprint(blueprint)
