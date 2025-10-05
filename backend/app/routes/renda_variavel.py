"""Routes for renda variavel insights and listings."""
from __future__ import annotations

from datetime import datetime, timezone
from collections.abc import Iterable

from flask import Blueprint, Flask, current_app, jsonify, request
from pydantic import ValidationError

from ..models import (
    RendaVariavelPosition,
    RendaVariavelTipo,
    RendaVariavelTradeInput,
)
from ..repositories import (
    DocumentNotFoundError,
    PersistenceLayerError,
    RendaVariavelPositionsRepository,
    RendaVariavelTradesRepository,
)
from ..services import RendaVariavelService, TradeNotAllowedError

blueprint = Blueprint("renda_variavel", __name__, url_prefix="/renda-variavel")


_CATEGORY_ALIASES: dict[str, RendaVariavelTipo] = {
    "acoes": RendaVariavelTipo.ACAO_BR,
    "fiis": RendaVariavelTipo.FII,
    "stocks": RendaVariavelTipo.STOCK_US,
    "reits": RendaVariavelTipo.REIT,
    "etf": RendaVariavelTipo.ETF,
}


def _ordered_tipos() -> Iterable[RendaVariavelTipo]:
    return _CATEGORY_ALIASES.values()


def _get_repository() -> RendaVariavelPositionsRepository:
    factory = current_app.config.get("RENDA_VARIAVEL_POSITIONS_REPOSITORY_FACTORY")
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

    return RendaVariavelPositionsRepository(gateway)


def _get_trades_repository() -> RendaVariavelTradesRepository:
    factory = current_app.config.get("RENDA_VARIAVEL_TRADES_REPOSITORY_FACTORY")
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

    return RendaVariavelTradesRepository(gateway)


def _build_service() -> RendaVariavelService:
    return RendaVariavelService(_get_repository())


def _resolve_tipo(categoria: str) -> RendaVariavelTipo | None:
    return _CATEGORY_ALIASES.get(categoria.lower())


def _ensure_timestamp(payload: dict[str, object]) -> dict[str, object]:
    payload.setdefault("atualizado_em", datetime.now(timezone.utc))
    return payload


def _ensure_defaults(payload: dict[str, object]) -> dict[str, object]:
    payload.setdefault("peso_percentual", 0.0)
    payload.setdefault("peso_desejado_percentual", 0.0)
    return payload


def _compute_totals(payload: dict[str, object]) -> dict[str, object]:
    quantidade = float(payload.get("quantidade", 0) or 0)
    preco_medio = float(payload.get("preco_medio", 0) or 0)
    cotacao_atual = float(payload.get("cotacao_atual", 0) or 0)

    total_compra = quantidade * preco_medio
    total_mercado = quantidade * cotacao_atual
    resultado_monetario = total_mercado - total_compra
    performance_percentual = 0.0
    if preco_medio:
        performance_percentual = (cotacao_atual / preco_medio - 1) * 100

    payload.update(
        {
            "total_compra": total_compra,
            "total_mercado": total_mercado,
            "resultado_monetario": resultado_monetario,
            "performance_percentual": performance_percentual,
        }
    )

    return payload


def _inject_tipo(payload: dict[str, object], tipo: RendaVariavelTipo) -> dict[str, object]:
    payload["tipo"] = tipo.value
    return payload


@blueprint.get("")
def list_renda_variavel() -> tuple[dict[str, object], int]:
    """Return renda variavel positions grouped by curated categories."""

    service = _build_service()
    try:
        grouped = service.list_positions_grouped(_ordered_tipos())
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    payload = {
        "items": {
            alias: [item.model_dump(mode="json") for item in grouped.get(tipo, [])]
            for alias, tipo in _CATEGORY_ALIASES.items()
        }
    }
    return jsonify(payload), 200


@blueprint.get("/<string:categoria>")
def list_renda_variavel_por_categoria(categoria: str) -> tuple[dict[str, object], int]:
    """Return renda variavel positions for a specific categoria slug."""

    tipo = _resolve_tipo(categoria)
    if tipo is None:
        return jsonify({"error": "categoria nao encontrada"}), 404

    service = _build_service()
    try:
        items = [item.model_dump(mode="json") for item in service.list_positions_by_tipo(tipo)]
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    payload = {"items": items, "categoria": categoria.lower(), "tipo": tipo.value}
    return jsonify(payload), 200


@blueprint.post("/<string:categoria>")
def create_renda_variavel_position(categoria: str) -> tuple[dict[str, object], int]:
    """Create a renda variavel position bound to the provided categoria."""

    tipo = _resolve_tipo(categoria)
    if tipo is None:
        return jsonify({"error": "categoria nao encontrada"}), 404

    payload = request.get_json(silent=True) or {}
    payload = _inject_tipo(payload, tipo)
    payload = _ensure_defaults(payload)
    payload = _ensure_timestamp(payload)
    payload = _compute_totals(payload)

    try:
        position = RendaVariavelPosition.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"errors": exc.errors()}), 400

    repository = _get_repository()
    serialised = position.model_dump(mode="json", exclude_none=True)

    try:
        created = repository.create(serialised)
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    service = RendaVariavelService(repository)
    service.recalculate_pesos(tipo)

    refreshed = created
    if created.id is not None:
        refreshed = repository.get(created.id)

    return jsonify({"item": refreshed.model_dump(mode="json")}), 201


@blueprint.put("/<string:categoria>/<string:position_id>")
def update_renda_variavel_position(
    categoria: str, position_id: str
) -> tuple[dict[str, object], int]:
    """Update a renda variavel position enforcing the categoria slug."""

    tipo = _resolve_tipo(categoria)
    if tipo is None:
        return jsonify({"error": "categoria nao encontrada"}), 404

    payload = request.get_json(silent=True) or {}
    payload = _inject_tipo(payload, tipo)
    payload = _ensure_defaults(payload)
    payload = _ensure_timestamp(payload)
    payload = _compute_totals(payload)

    try:
        position = RendaVariavelPosition.model_validate({**payload, "id": position_id})
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

    service = RendaVariavelService(repository)
    service.recalculate_pesos(tipo)

    refreshed = repository.get(position_id)

    return jsonify({"item": refreshed.model_dump(mode="json")}), 200


@blueprint.delete("/<string:categoria>/<string:position_id>")
def delete_renda_variavel_position(categoria: str, position_id: str) -> tuple[str, int]:
    """Remove a renda variavel position bound to the categoria."""

    tipo = _resolve_tipo(categoria)
    if tipo is None:
        return jsonify({"error": "categoria nao encontrada"}), 404

    repository = _get_repository()
    service = RendaVariavelService(repository)

    try:
        repository.delete(position_id)
    except DocumentNotFoundError:
        return jsonify({"error": "position nao encontrada"}), 404
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    service.recalculate_pesos(tipo)

    return "", 204


@blueprint.get("/<string:categoria>/<string:position_id>/transacoes")
def list_renda_variavel_trades(
    categoria: str, position_id: str
) -> tuple[dict[str, object], int]:
    """Return trades recorded for a specific position."""

    tipo = _resolve_tipo(categoria)
    if tipo is None:
        return jsonify({"error": "categoria nao encontrada"}), 404

    repository = _get_repository()

    try:
        position = repository.get(position_id)
    except DocumentNotFoundError:
        return jsonify({"error": "position nao encontrada"}), 404

    if position.tipo is not tipo:
        return jsonify({"error": "categoria nao corresponde ao ativo"}), 400

    service = RendaVariavelService(repository, _get_trades_repository())
    trades = sorted(
        service.list_trades(position_id),
        key=lambda trade: trade.data,
        reverse=True,
    )

    payload = {
        "items": [trade.model_dump(mode="json") for trade in trades],
        "position_id": position_id,
    }
    return jsonify(payload), 200


@blueprint.post("/<string:categoria>/<string:position_id>/transacoes")
def create_renda_variavel_trade(
    categoria: str, position_id: str
) -> tuple[dict[str, object], int]:
    """Create a trade tied to a given renda variavel position."""

    tipo = _resolve_tipo(categoria)
    if tipo is None:
        return jsonify({"error": "categoria nao encontrada"}), 404

    repository = _get_repository()
    try:
        position = repository.get(position_id)
    except DocumentNotFoundError:
        return jsonify({"error": "position nao encontrada"}), 404

    if position.tipo is not tipo:
        return jsonify({"error": "categoria nao corresponde ao ativo"}), 400

    payload = request.get_json(silent=True) or {}

    try:
        trade_input = RendaVariavelTradeInput.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"errors": exc.errors()}), 400

    service = RendaVariavelService(repository, _get_trades_repository())

    try:
        updated_position, recorded_trade = service.record_trade(
            position_id,
            tipo_operacao=trade_input.tipo_operacao,
            quantidade=trade_input.quantidade,
            cotacao=trade_input.cotacao,
            data=trade_input.data,
        )
    except TradeNotAllowedError as exc:
        return jsonify({"error": str(exc)}), 400
    except DocumentNotFoundError:
        return jsonify({"error": "position nao encontrada"}), 404
    except PersistenceLayerError as exc:
        return jsonify({"error": str(exc)}), 503

    payload = {
        "item": recorded_trade.model_dump(mode="json"),
        "position": updated_position.model_dump(mode="json"),
    }

    return jsonify(payload), 201


def register(app: Flask) -> None:
    """Register the blueprint on the Flask app."""
    app.register_blueprint(blueprint)
