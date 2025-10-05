"""Tests for the renda variavel service helpers."""
from __future__ import annotations

from datetime import datetime

import pytest

from app.models import RendaVariavelPosition, RendaVariavelTipo, RendaVariavelTrade
from app.services import RendaVariavelService, TradeNotAllowedError


class StubPositionsRepository:
    """In-memory repository double used to test the service."""

    def __init__(self, items: list[RendaVariavelPosition]) -> None:
        self._items: dict[str, RendaVariavelPosition] = {}
        for index, item in enumerate(items, start=1):
            identifier = item.id or f"position-{index}"
            self._items[identifier] = item.model_copy(update={"id": identifier})

    def list(self) -> list[RendaVariavelPosition]:
        return list(self._items.values())

    def get(self, position_id: str) -> RendaVariavelPosition:
        return self._items[position_id]

    def update(self, position_id: str, payload: dict[str, object]) -> RendaVariavelPosition:
        current = self._items[position_id]
        updated = current.model_copy(update=payload)
        self._items[position_id] = updated
        return updated


class StubTradesRepository:
    """In-memory repository double for renda variavel trades."""

    def __init__(self) -> None:
        self._items: list[RendaVariavelTrade] = []

    def list(self) -> list[RendaVariavelTrade]:
        return list(self._items)

    def list_by_position(self, position_id: str) -> list[RendaVariavelTrade]:
        return [item for item in self._items if item.position_id == position_id]

    def create(self, payload: dict[str, object]) -> RendaVariavelTrade:
        data = dict(payload, id=f"trade-{len(self._items) + 1}")
        trade = RendaVariavelTrade.model_validate(data)
        self._items.append(trade)
        return trade


def _make_position(ticker: str, tipo: RendaVariavelTipo, *, identifier: str | None = None) -> RendaVariavelPosition:
    return RendaVariavelPosition(
        id=identifier,
        ticker=ticker,
        tipo=tipo,
        quantidade=10,
        preco_medio=15.5,
        cotacao_atual=17.8,
        total_compra=155.0,
        total_mercado=178.0,
        resultado_monetario=23.0,
        performance_percentual=14.8,
        peso_percentual=20.0,
        peso_desejado_percentual=25.0,
        atualizado_em=datetime(2024, 1, 1, 12, 0, 0),
    )


def test_list_positions_by_tipo_filters_correctly() -> None:
    repository = StubPositionsRepository(
        [
            _make_position("BBAS3", RendaVariavelTipo.ACAO_BR),
            _make_position("HGLG11", RendaVariavelTipo.FII),
        ]
    )
    service = RendaVariavelService(repository)

    only_acoes = service.list_positions_by_tipo(RendaVariavelTipo.ACAO_BR)

    tickers = {item.ticker for item in only_acoes}
    assert tickers == {"BBAS3"}


def test_list_positions_grouped_respects_requested_tipos() -> None:
    repository = StubPositionsRepository(
        [
            _make_position("IVVB11", RendaVariavelTipo.ETF),
            _make_position("VIG", RendaVariavelTipo.ETF),
            _make_position("VISC11", RendaVariavelTipo.FII),
        ]
    )
    service = RendaVariavelService(repository)

    grouped = service.list_positions_grouped((RendaVariavelTipo.ETF, RendaVariavelTipo.FII))

    assert set(grouped.keys()) == {RendaVariavelTipo.ETF, RendaVariavelTipo.FII}
    assert [item.ticker for item in grouped[RendaVariavelTipo.ETF]] == ["IVVB11", "VIG"]
    assert [item.ticker for item in grouped[RendaVariavelTipo.FII]] == ["VISC11"]


def test_record_trade_compra_updates_position_totals() -> None:
    positions = StubPositionsRepository(
        [_make_position("HGLG11", RendaVariavelTipo.FII, identifier="position-1")]
    )
    trades = StubTradesRepository()
    service = RendaVariavelService(positions, trades)

    updated, trade = service.record_trade(
        "position-1",
        tipo_operacao="compra",
        quantidade=5,
        cotacao=20.0,
    )

    assert updated.quantidade == pytest.approx(15.0)
    assert updated.preco_medio == pytest.approx((155.0 + 5 * 20.0) / 15.0)
    assert updated.total_compra == pytest.approx(155.0 + 100.0)
    assert trade.tipo_operacao == "compra"
    assert len(trades.list_by_position("position-1")) == 1
    # peso recalculado com apenas um ativo deve ser 100%
    assert updated.peso_percentual == pytest.approx(100.0)


def test_record_trade_venda_reduces_quantity_and_tracks_resultado() -> None:
    positions = StubPositionsRepository(
        [_make_position("HGLG11", RendaVariavelTipo.FII, identifier="position-1")]
    )
    trades = StubTradesRepository()
    service = RendaVariavelService(positions, trades)

    updated, trade = service.record_trade(
        "position-1",
        tipo_operacao="venda",
        quantidade=4,
        cotacao=18.0,
    )

    assert updated.quantidade == pytest.approx(6.0)
    assert updated.total_compra == pytest.approx(6 * 15.5)  # previous preco_medio 15.5
    assert trade.resultado_monetario == pytest.approx((18.0 - 15.5) * 4)


def test_record_trade_venda_rejects_excess_quantity() -> None:
    positions = StubPositionsRepository(
        [_make_position("HGLG11", RendaVariavelTipo.FII, identifier="position-1")]
    )
    trades = StubTradesRepository()
    service = RendaVariavelService(positions, trades)

    with pytest.raises(TradeNotAllowedError):
        service.record_trade(
            "position-1",
            tipo_operacao="venda",
            quantidade=50,
            cotacao=18.0,
        )
