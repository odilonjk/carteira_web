"""Route-level tests for renda variavel endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from app.models import RendaVariavelPosition, RendaVariavelTipo, RendaVariavelTrade
from app.repositories import DocumentNotFoundError


class StubPositionsRepository:
    """Very small repository double used to stub renda variavel data."""

    def __init__(self) -> None:
        self._items: dict[str, RendaVariavelPosition] = {}

    def list(self) -> list[RendaVariavelPosition]:
        return list(self._items.values())

    def create(self, payload: dict[str, Any]) -> RendaVariavelPosition:
        next_id = f"position-{len(self._items) + 1}"
        data = dict(payload, id=next_id)
        position = RendaVariavelPosition.model_validate(data)
        self._items[next_id] = position
        return position

    def update(self, position_id: str, payload: dict[str, Any]) -> RendaVariavelPosition:
        if position_id not in self._items:
            raise DocumentNotFoundError("position not found")

        base = self._items[position_id].model_dump(mode="json")
        base.update(payload)
        base["id"] = position_id
        data = base
        position = RendaVariavelPosition.model_validate(data)
        self._items[position_id] = position
        return position

    def get(self, position_id: str) -> RendaVariavelPosition:
        try:
            return self._items[position_id]
        except KeyError as exc:  # pragma: no cover - defensive
            raise DocumentNotFoundError("position not found") from exc

    def delete(self, position_id: str) -> None:
        if position_id not in self._items:
            raise DocumentNotFoundError("position not found")
        self._items.pop(position_id, None)

    def seed(self, payloads: list[dict[str, Any]]) -> None:
        self._items = {}
        for payload in payloads:
            position = RendaVariavelPosition.model_validate(payload)
            identifier = position.id or f"position-{len(self._items) + 1}"
            self._items[identifier] = position.model_copy(update={"id": identifier})


class StubTradesRepository:
    """Simple in-memory store for renda variavel trades."""

    def __init__(self) -> None:
        self._items: list[RendaVariavelTrade] = []

    def list(self) -> list[RendaVariavelTrade]:
        return list(self._items)

    def list_by_position(self, position_id: str) -> list[RendaVariavelTrade]:
        return [item for item in self._items if item.position_id == position_id]

    def create(self, payload: dict[str, Any]) -> RendaVariavelTrade:
        data = dict(payload, id=f"trade-{len(self._items) + 1}")
        trade = RendaVariavelTrade.model_validate(data)
        self._items.append(trade)
        return trade


@pytest.fixture()
def stub_positions_repository(app) -> StubPositionsRepository:
    repository = StubPositionsRepository()

    def factory() -> StubPositionsRepository:
        return repository

    app.config["RENDA_VARIAVEL_POSITIONS_REPOSITORY_FACTORY"] = factory  # type: ignore[assignment]
    yield repository
    app.config.pop("RENDA_VARIAVEL_POSITIONS_REPOSITORY_FACTORY", None)


@pytest.fixture()
def stub_trades_repository(app) -> StubTradesRepository:
    repository = StubTradesRepository()

    def factory() -> StubTradesRepository:
        return repository

    app.config["RENDA_VARIAVEL_TRADES_REPOSITORY_FACTORY"] = factory  # type: ignore[assignment]
    yield repository
    app.config.pop("RENDA_VARIAVEL_TRADES_REPOSITORY_FACTORY", None)


def _position_payload(ticker: str, tipo: RendaVariavelTipo) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "tipo": tipo.value,
        "quantidade": 10,
        "preco_medio": 15.0,
        "cotacao_atual": 18.0,
        "total_compra": 150.0,
        "total_mercado": 180.0,
        "resultado_monetario": 30.0,
        "performance_percentual": 20.0,
        "peso_percentual": 25.0,
        "peso_desejado_percentual": 30.0,
        "atualizado_em": datetime(2024, 1, 1, 12, 0, 0),
    }


def test_list_renda_variavel_returns_grouped_payload(client, stub_positions_repository: StubPositionsRepository) -> None:
    stub_positions_repository.seed(
        [
            _position_payload("ITUB4", RendaVariavelTipo.ACAO_BR),
            _position_payload("HGLG11", RendaVariavelTipo.FII),
            _position_payload("IVVB11", RendaVariavelTipo.ETF),
        ]
    )

    response = client.get("/renda-variavel")

    assert response.status_code == 200
    body = response.get_json()
    assert set(body["items"].keys()) == {"acoes", "fiis", "stocks", "reits", "etf"}
    assert [item["ticker"] for item in body["items"]["acoes"]] == ["ITUB4"]
    assert [item["ticker"] for item in body["items"]["fiis"]] == ["HGLG11"]
    assert [item["ticker"] for item in body["items"]["etf"]] == ["IVVB11"]


def test_list_renda_variavel_por_categoria_filters_by_slug(client, stub_positions_repository: StubPositionsRepository) -> None:
    stub_positions_repository.seed(
        [
            _position_payload("PETR4", RendaVariavelTipo.ACAO_BR),
            _position_payload("BBDC4", RendaVariavelTipo.ACAO_BR),
            _position_payload("VISC11", RendaVariavelTipo.FII),
        ]
    )

    response = client.get("/renda-variavel/acoes")

    assert response.status_code == 200
    body = response.get_json()
    assert body["categoria"] == "acoes"
    assert [item["ticker"] for item in body["items"]] == ["PETR4", "BBDC4"]


def test_list_renda_variavel_por_categoria_returns_404_for_unknown_slug(client) -> None:
    response = client.get("/renda-variavel/cripto")

    assert response.status_code == 404
    assert response.get_json()["error"] == "categoria nao encontrada"

def test_create_renda_variavel_position_assigns_tipo(
    client, stub_positions_repository: StubPositionsRepository
) -> None:
    response = client.post(
        "/renda-variavel/acoes",
        json={
            "ticker": "PETR4",
            "quantidade": 100,
            "preco_medio": 28.5,
            "cotacao_atual": 30.1,
            "peso_desejado_percentual": 18,
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["item"]["tipo"] == "acao_br"
    assert body["item"]["peso_percentual"] == pytest.approx(100.0)

    stored = stub_positions_repository.list()
    assert stored
    assert stored[0].peso_percentual == pytest.approx(100.0)


def test_update_renda_variavel_position_edits_document(
    client, stub_positions_repository: StubPositionsRepository
) -> None:
    created = stub_positions_repository.create(
        _position_payload("BBAS3", RendaVariavelTipo.ACAO_BR)
    )

    response = client.put(
        f"/renda-variavel/acoes/{created.id}",
        json={
            "ticker": "BBAS3",
            "quantidade": 150,
            "preco_medio": 30.0,
            "cotacao_atual": 32.0,
            "peso_desejado_percentual": 22.0,
        },
    )

    assert response.status_code == 200
    updated_item = response.get_json()["item"]
    assert updated_item["quantidade"] == 150
    assert updated_item["peso_percentual"] == pytest.approx(100.0)


def test_delete_renda_variavel_position_removes_document(
    client, stub_positions_repository: StubPositionsRepository
) -> None:
    created = stub_positions_repository.create(
        _position_payload("SMAL11", RendaVariavelTipo.ETF)
    )

    response = client.delete(f"/renda-variavel/etf/{created.id}")

    assert response.status_code == 204
    assert not stub_positions_repository.list()

def test_recalculate_pesos_after_new_position(
    client, stub_positions_repository: StubPositionsRepository
) -> None:
    stub_positions_repository.seed(
        [
            {
                **_position_payload("ITUB4", RendaVariavelTipo.ACAO_BR),
                "id": "acao-1",
                "total_compra": 2800.0,
                "total_mercado": 3000.0,
                "resultado_monetario": 200.0,
                "performance_percentual": 7.14,
                "peso_percentual": 100.0,
                "peso_desejado_percentual": 20.0,
            }
        ]
    )

    response = client.post(
        "/renda-variavel/acoes",
        json={
            "ticker": "BBDC4",
            "quantidade": 100,
            "preco_medio": 20.0,
            "cotacao_atual": 25.0,
            "peso_desejado_percentual": 30.0,
        },
    )

    assert response.status_code == 201

    items = {item.ticker: item for item in stub_positions_repository.list()}
    total = sum(item.total_mercado for item in items.values())
    assert total == pytest.approx(5500.0)
    assert items["ITUB4"].peso_percentual == pytest.approx(3000.0 / total * 100)
    assert items["BBDC4"].peso_percentual == pytest.approx(2500.0 / total * 100)

def test_delete_renda_variavel_recalculates_weights(
    client, stub_positions_repository: StubPositionsRepository
) -> None:
    stub_positions_repository.seed(
        [
            {
                **_position_payload("ITSA4", RendaVariavelTipo.ACAO_BR),
                "id": "acao-1",
                "total_compra": 1000.0,
                "total_mercado": 1000.0,
                "resultado_monetario": 0.0,
                "performance_percentual": 0.0,
                "peso_percentual": 60.0,
                "peso_desejado_percentual": 30.0,
            },
            {
                **_position_payload("BBDC4", RendaVariavelTipo.ACAO_BR),
                "id": "acao-2",
                "total_compra": 1500.0,
                "total_mercado": 1500.0,
                "resultado_monetario": 0.0,
                "performance_percentual": 0.0,
                "peso_percentual": 40.0,
                "peso_desejado_percentual": 30.0,
            },
        ]
    )

    response = client.delete("/renda-variavel/acoes/acao-2")

    assert response.status_code == 204

    remaining = stub_positions_repository.list()
    assert len(remaining) == 1
    assert remaining[0].ticker == "ITSA4"
    assert remaining[0].peso_percentual == pytest.approx(100.0)


def test_create_trade_compra_updates_position(
    client,
    stub_positions_repository: StubPositionsRepository,
    stub_trades_repository: StubTradesRepository,
) -> None:
    position = stub_positions_repository.create(_position_payload("HGLG11", RendaVariavelTipo.FII))

    response = client.post(
        f"/renda-variavel/fiis/{position.id}/transacoes",
        json={
            "tipo_operacao": "compra",
            "quantidade": 5,
            "cotacao": 20.0,
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    updated = body["position"]

    assert updated["quantidade"] == pytest.approx(15.0)
    assert updated["preco_medio"] == pytest.approx((150.0 + 5 * 20.0) / 15.0)
    assert updated["total_compra"] == pytest.approx(250.0)
    assert updated["total_mercado"] == pytest.approx(15 * 20.0)
    trades = stub_trades_repository.list_by_position(position.id)
    assert len(trades) == 1
    assert trades[0].tipo_operacao == "compra"


def test_create_trade_venda_updates_position(
    client,
    stub_positions_repository: StubPositionsRepository,
    stub_trades_repository: StubTradesRepository,
) -> None:
    position = stub_positions_repository.create(_position_payload("HGLG11", RendaVariavelTipo.FII))

    response = client.post(
        f"/renda-variavel/fiis/{position.id}/transacoes",
        json={
            "tipo_operacao": "venda",
            "quantidade": 4,
            "cotacao": 18.0,
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    updated = body["position"]

    assert updated["quantidade"] == pytest.approx(6.0)
    assert updated["total_compra"] == pytest.approx(6 * 15.0)
    assert updated["total_mercado"] == pytest.approx(6 * 18.0)

    trade = stub_trades_repository.list_by_position(position.id)[0]
    assert trade.tipo_operacao == "venda"
    assert trade.resultado_monetario == pytest.approx((18.0 - 15.0) * 4)


def test_create_trade_venda_rejects_excess_quantity(
    client,
    stub_positions_repository: StubPositionsRepository,
    stub_trades_repository: StubTradesRepository,
) -> None:
    position = stub_positions_repository.create(_position_payload("HGLG11", RendaVariavelTipo.FII))

    response = client.post(
        f"/renda-variavel/fiis/{position.id}/transacoes",
        json={
            "tipo_operacao": "venda",
            "quantidade": 50,
            "cotacao": 18.0,
        },
    )

    assert response.status_code == 400
    assert "quantidade" in response.get_json()["error"]
    assert not stub_trades_repository.list_by_position(position.id)


def test_list_trades_returns_sorted_items(
    client,
    stub_positions_repository: StubPositionsRepository,
    stub_trades_repository: StubTradesRepository,
) -> None:
    position = stub_positions_repository.create(_position_payload("HGLG11", RendaVariavelTipo.FII))

    # Seed trades manually in repository
    stub_trades_repository.create(
        {
            "position_id": position.id,
            "tipo_operacao": "compra",
            "data": datetime(2024, 5, 5, 12, 0, 0),
            "quantidade": 5,
            "cotacao": 20.0,
            "total": 100.0,
        }
    )
    stub_trades_repository.create(
        {
            "position_id": position.id,
            "tipo_operacao": "venda",
            "data": datetime(2024, 6, 1, 12, 0, 0),
            "quantidade": 2,
            "cotacao": 22.0,
            "total": 44.0,
        }
    )

    response = client.get(f"/renda-variavel/fiis/{position.id}/transacoes")

    assert response.status_code == 200
    items = response.get_json()["items"]
    assert len(items) == 2
    assert items[0]["tipo_operacao"] == "venda"  # latest first
