"""Routes for renda fixa insights and CRUD operations."""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, Flask, current_app, jsonify, request
from pydantic import ValidationError

from ..models import RendaFixaPosition
from ..repositories import (
    DocumentNotFoundError,
    PersistenceLayerError,
    RendaFixaRepository,
)

blueprint = Blueprint("renda_fixa", __name__, url_prefix="/renda-fixa")


def _get_repository() -> RendaFixaRepository:
    factory = current_app.config.get("RENDA_FIXA_REPOSITORY_FACTORY")
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

    return RendaFixaRepository(gateway)


def _normalise_payload(payload: dict[str, object]) -> dict[str, object]:
    if "moeda" not in payload:
        payload["moeda"] = "brl"
    return payload


@blueprint.get("")
def list_renda_fixa() -> tuple[dict[str, object], int]:
    """Return renda fixa positions stored in the persistence layer."""

    repository = _get_repository()
    try:
        items = [item.model_dump(mode="json") for item in repository.list()]
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify({"items": items}), 200


@blueprint.post("")
def create_renda_fixa() -> tuple[dict[str, object], int]:
    """Persist a new renda fixa position document."""

    payload = _normalise_payload(request.get_json(silent=True) or {})

    try:
        position = RendaFixaPosition.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"errors": exc.errors()}), 400

    repository = _get_repository()
    serialised = position.model_dump(mode="json", exclude_none=True)

    try:
        created = repository.create(serialised)
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify({"item": created.model_dump(mode="json")}), 201


@blueprint.put("/<string:position_id>")
def update_renda_fixa(position_id: str) -> tuple[dict[str, object], int]:
    """Replace an existing renda fixa position document."""

    payload = _normalise_payload(request.get_json(silent=True) or {})

    try:
        position = RendaFixaPosition.model_validate({**payload, "id": position_id})
    except ValidationError as exc:
        return jsonify({"errors": exc.errors()}), 400

    repository = _get_repository()
    serialised = position.model_dump(mode="json", exclude_none=True, exclude={"id"})

    try:
        updated = repository.update(position_id, serialised)
    except DocumentNotFoundError:
        return jsonify({"error": "position nao encontrada"}), 404
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify({"item": updated.model_dump(mode="json")}), 200


@blueprint.delete("/<string:position_id>")
def delete_renda_fixa(position_id: str) -> tuple[str, int]:
    """Remove a renda fixa position document."""

    repository = _get_repository()

    try:
        repository.delete(position_id)
    except DocumentNotFoundError:
        return jsonify({"error": "position nao encontrada"}), 404
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    return "", 204


def register(app: Flask) -> None:
    """Register the blueprint on the Flask app."""
    app.register_blueprint(blueprint)
