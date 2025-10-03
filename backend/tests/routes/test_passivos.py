"""Integration-lite tests for passivos routes using stub repositories."""
from __future__ import annotations

from typing import Any

import pytest

from app.models import Passivo, PassivoCategoria


class StubPassivosRepository:
    """Minimal repository double storing passivos in memory."""

    def __init__(self) -> None:
        self._items: list[Passivo] = []

    def list(self) -> list[Passivo]:
        return list(self._items)

    def create(self, payload: dict[str, Any]) -> Passivo:
        next_id = f"passivo-{len(self._items) + 1}"
        data = dict(payload, id=next_id)
        passivo = Passivo.model_validate(data)
        self._items.append(passivo)
        return passivo


@pytest.fixture()
def stub_repository(app) -> StubPassivosRepository:
    stub = StubPassivosRepository()

    def factory() -> StubPassivosRepository:
        return stub

    app.config["PASSIVOS_REPOSITORY_FACTORY"] = factory  # type: ignore[assignment]
    yield stub
    app.config.pop("PASSIVOS_REPOSITORY_FACTORY", None)


def test_list_passivos_returns_data(client, stub_repository: StubPassivosRepository) -> None:
    stub_repository.create(
        {
            "nome": "Financiamento Casa",
            "categoria": PassivoCategoria.FINANCIAMENTO.value,
            "saldo_atual": 250000.0,
        }
    )

    response = client.get("/passivos")

    assert response.status_code == 200
    body = response.get_json()
    assert body == {
        "items": [
            {
                "categoria": "financiamento",
                "id": "passivo-1",
                "nome": "Financiamento Casa",
                "observacoes": None,
                "saldo_atual": 250000.0,
                "taxa_juros_aa": None,
                "vencimento": None,
            }
        ]
    }


def test_create_passivo_persists_and_returns_document(client, stub_repository: StubPassivosRepository) -> None:
    response = client.post(
        "/passivos",
        json={
            "nome": "Cartao",
            "categoria": "cartao",
            "saldo_atual": 1500.0,
            "taxa_juros_aa": 12.5,
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["item"]["nome"] == "Cartao"
    assert len(stub_repository.list()) == 1


def test_create_passivo_returns_validation_errors(client, stub_repository: StubPassivosRepository) -> None:
    response = client.post(
        "/passivos",
        json={"nome": "", "categoria": "cartao", "saldo_atual": -1},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert isinstance(body.get("errors"), list)


def test_passivos_endpoints_use_tinydb_gateway_when_not_stubbed(client) -> None:
    create_response = client.post(
        "/passivos",
        json={
            "nome": "Consorcio",
            "categoria": "outros",
            "saldo_atual": 1000.0,
        },
    )

    assert create_response.status_code == 201

    list_response = client.get("/passivos")
    assert list_response.status_code == 200
    items = list_response.get_json()["items"]
    assert len(items) == 1
    assert items[0]["nome"] == "Consorcio"
