"""Route-level tests for renda fixa endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from app.models import RendaFixaIndexador, RendaFixaPosition, RendaFixaTipo
from app.repositories import DocumentNotFoundError


class StubRendaFixaRepository:
    """In-memory double mimicking the renda fixa repository."""

    def __init__(self) -> None:
        self._items: dict[str, RendaFixaPosition] = {}

    def list(self) -> list[RendaFixaPosition]:
        return list(self._items.values())

    def create(self, payload: dict[str, Any]) -> RendaFixaPosition:
        next_id = f"renda-fixa-{len(self._items) + 1}"
        data = dict(payload, id=next_id)
        position = RendaFixaPosition.model_validate(data)
        self._items[next_id] = position
        return position

    def update(self, position_id: str, payload: dict[str, Any]) -> RendaFixaPosition:
        if position_id not in self._items:
            raise DocumentNotFoundError("position not found")
        data = dict(payload, id=position_id)
        position = RendaFixaPosition.model_validate(data)
        self._items[position_id] = position
        return position

    def delete(self, position_id: str) -> None:
        if position_id not in self._items:
            raise DocumentNotFoundError("position not found")
        self._items.pop(position_id, None)


@pytest.fixture()
def stub_renda_fixa_repository(app) -> StubRendaFixaRepository:
    repository = StubRendaFixaRepository()

    def factory() -> StubRendaFixaRepository:
        return repository

    app.config["RENDA_FIXA_REPOSITORY_FACTORY"] = factory  # type: ignore[assignment]
    yield repository
    app.config.pop("RENDA_FIXA_REPOSITORY_FACTORY", None)


def _payload() -> dict[str, Any]:
    return {
        "ativo": "Tesouro IPCA+ 2029",
        "tipo": RendaFixaTipo.TESOURO_IPCA.value,
        "indexador": RendaFixaIndexador.POS_IPCA.value,
        "rentabilidade_aa": 5.5,
        "distribuidor": "Tesouro Direto",
        "valor": 2500.0,
        "data_inicio": datetime(2024, 1, 1, 12, 0, 0).isoformat(),
        "vencimento": datetime(2029, 1, 1, 12, 0, 0).isoformat(),
        "moeda": "brl",
    }


def test_list_renda_fixa_returns_items(client, stub_renda_fixa_repository: StubRendaFixaRepository) -> None:
    stub_renda_fixa_repository.create(_payload())

    response = client.get("/renda-fixa")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["items"]) == 1
    assert body["items"][0]["ativo"] == "Tesouro IPCA+ 2029"


def test_create_renda_fixa_persists_document(client, stub_renda_fixa_repository: StubRendaFixaRepository) -> None:
    response = client.post("/renda-fixa", json=_payload())

    assert response.status_code == 201
    assert len(stub_renda_fixa_repository.list()) == 1


def test_create_renda_fixa_validates_payload(client) -> None:
    response = client.post("/renda-fixa", json={"ativo": "", "valor": -1})

    assert response.status_code == 400
    body = response.get_json()
    assert isinstance(body.get("errors"), list)


def test_update_renda_fixa_handles_unknown_document(
    client, stub_renda_fixa_repository: StubRendaFixaRepository
) -> None:
    response = client.put("/renda-fixa/renda-fixa-999", json=_payload())

    assert response.status_code == 404


def test_delete_renda_fixa_removes_document(
    client, stub_renda_fixa_repository: StubRendaFixaRepository
) -> None:
    created = stub_renda_fixa_repository.create(_payload())

    response = client.delete(f"/renda-fixa/{created.id}")

    assert response.status_code == 204
    assert not stub_renda_fixa_repository.list()
