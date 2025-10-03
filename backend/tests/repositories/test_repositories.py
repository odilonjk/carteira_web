"""Tests for Firestore repositories and gateway abstractions."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping
from uuid import uuid4
from unittest import mock

import pytest
from google.api_core import exceptions as google_exceptions

from app.models import (
    Passivo,
    PassivoCategoria,
    RendaVariavelPosition,
    RendaVariavelTipo,
)
from app.repositories import (
    DocumentNotFoundError,
    PassivosRepository,
    PersistenceLayerError,
    RendaVariavelPositionsRepository,
)
from app.repositories.firestore_gateway import FirestoreGateway
from app.repositories.tinydb_gateway import TinyDbGateway
from app.repositories.interfaces import FirestoreGatewayProtocol


class InMemoryGateway(FirestoreGatewayProtocol):
    """Simple in-memory double used to mimic Firestore behavior."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, dict[str, Any]]] = {}

    def add_document(
        self,
        collection: str,
        payload: Mapping[str, Any],
        document_id: str | None = None,
        merge: bool = False,
    ) -> str:
        coll = self._store.setdefault(collection, {})
        doc_id = document_id or uuid4().hex
        if merge and doc_id in coll:
            coll[doc_id].update(dict(payload))
        else:
            coll[doc_id] = dict(payload)
        return doc_id

    def get_document(self, collection: str, document_id: str) -> Mapping[str, Any] | None:
        data = self._store.get(collection, {}).get(document_id)
        if data is None:
            return None
        result = dict(data)
        result.setdefault("id", document_id)
        return result

    def list_documents(self, collection: str) -> list[Mapping[str, Any]]:
        coll = self._store.get(collection, {})
        return [dict(value, id=doc_id) for doc_id, value in coll.items()]

    def delete_document(self, collection: str, document_id: str) -> None:
        coll = self._store.get(collection, {})
        coll.pop(document_id, None)


def _sample_passivo_payload() -> Mapping[str, Any]:
    return Passivo(
        nome="Financiamento Casa",
        categoria=PassivoCategoria.FINANCIAMENTO,
        saldo_atual=250000.0,
        taxa_juros_aa=10.5,
    ).model_dump(exclude_none=True)


def _sample_position_payload() -> Mapping[str, Any]:
    return RendaVariavelPosition(
        ticker="HSML11",
        tipo=RendaVariavelTipo.FII,
        quantidade=80,
        preco_medio=10.0,
        cotacao_atual=20.0,
        total_compra=800.0,
        total_mercado=1600.0,
        resultado_monetario=800.0,
        performance_percentual=100.0,
        peso_percentual=100.0,
        peso_desejado_percentual=25.0,
        atualizado_em=datetime(2024, 1, 5, 12, 0, 0),
    ).model_dump(exclude_none=True)


def test_passivos_repository_create_and_get_roundtrip() -> None:
    gateway = InMemoryGateway()
    repo = PassivosRepository(gateway)

    created = repo.create(_sample_passivo_payload())

    assert created.id is not None
    fetched = repo.get(created.id)
    assert fetched == created


def test_passivos_repository_update_replaces_document() -> None:
    gateway = InMemoryGateway()
    repo = PassivosRepository(gateway)
    created = repo.create(_sample_passivo_payload())

    repo.update(created.id, {"nome": "Atualizado", "categoria": "outros", "saldo_atual": 100.0})
    updated = repo.get(created.id)

    assert updated.nome == "Atualizado"
    assert updated.categoria.value == "outros"
    assert updated.saldo_atual == 100.0


def test_passivos_repository_delete_missing_raises() -> None:
    repo = PassivosRepository(InMemoryGateway())

    with pytest.raises(DocumentNotFoundError):
        repo.delete("missing")


def test_renda_variavel_repository_list() -> None:
    gateway = InMemoryGateway()
    repo = RendaVariavelPositionsRepository(gateway)
    repo.create(_sample_position_payload())
    repo.create(_sample_position_payload())

    items = repo.list()
    assert len(items) == 2
    assert all(item.ticker == "HSML11" for item in items)


def test_firestore_gateway_propagates_google_errors_on_add() -> None:
    client = mock.Mock()
    client.collection.side_effect = google_exceptions.GoogleAPICallError("boom")
    gateway = FirestoreGateway(client)

    with pytest.raises(PersistenceLayerError):
        gateway.add_document("passivos", {"nome": "Erro"})


def test_firestore_gateway_add_and_get_successful() -> None:
    mock_collection = mock.Mock()
    mock_document = mock.Mock()
    mock_document.id = "generated-id"
    mock_snapshot = mock.Mock()
    mock_snapshot.exists = True
    mock_snapshot.id = "generated-id"
    mock_snapshot.to_dict.return_value = {"nome": "Financiamento"}

    client = mock.Mock()
    client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    mock_document.get.return_value = mock_snapshot

    gateway = FirestoreGateway(client)

    doc_id = gateway.add_document("passivos", {"nome": "Financiamento"})
    fetched = gateway.get_document("passivos", doc_id)

    mock_document.set.assert_called_once_with({"nome": "Financiamento"}, merge=False)
    assert fetched == {"nome": "Financiamento", "id": "generated-id"}


def test_tinydb_gateway_roundtrip(tmp_path) -> None:
    gateway = TinyDbGateway.from_file(str(tmp_path / "tiny.json"))

    doc_id = gateway.add_document("passivos", {"nome": "Cartao"})
    assert doc_id

    fetched = gateway.get_document("passivos", doc_id)
    assert fetched == {"nome": "Cartao", "id": doc_id}


def test_tinydb_gateway_merge_updates_fields(tmp_path) -> None:
    gateway = TinyDbGateway.from_file(str(tmp_path / "tiny.json"))
    doc_id = gateway.add_document("passivos", {"nome": "Cartao", "saldo": 100.0})

    gateway.add_document("passivos", {"saldo": 50.0}, document_id=doc_id, merge=True)

    fetched = gateway.get_document("passivos", doc_id)
    assert fetched == {"nome": "Cartao", "saldo": 50.0, "id": doc_id}


def test_tinydb_gateway_delete_removes_document(tmp_path) -> None:
    gateway = TinyDbGateway.from_file(str(tmp_path / "tiny.json"))
    doc_id = gateway.add_document("passivos", {"nome": "Cartao"})

    gateway.delete_document("passivos", doc_id)

    assert gateway.get_document("passivos", doc_id) is None


def test_tinydb_gateway_replace_overwrites_missing_fields(tmp_path) -> None:
    gateway = TinyDbGateway.from_file(str(tmp_path / "tiny.json"))
    doc_id = gateway.add_document("passivos", {"nome": "Cartao", "saldo": 100.0})

    gateway.add_document("passivos", {"nome": "Atualizado"}, document_id=doc_id)

    fetched = gateway.get_document("passivos", doc_id)
    assert fetched == {"nome": "Atualizado", "id": doc_id}
