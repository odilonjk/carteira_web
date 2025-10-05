"""Tests for the renda variavel service helpers."""
from __future__ import annotations

from datetime import datetime

from app.models import RendaVariavelPosition, RendaVariavelTipo
from app.services import RendaVariavelService


class StubPositionsRepository:
    """In-memory repository double used to test the service."""

    def __init__(self, items: list[RendaVariavelPosition]) -> None:
        self._items = items

    def list(self) -> list[RendaVariavelPosition]:
        return list(self._items)


def _make_position(ticker: str, tipo: RendaVariavelTipo) -> RendaVariavelPosition:
    return RendaVariavelPosition(
        id=None,
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
