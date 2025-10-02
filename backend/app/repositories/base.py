"""Shared repository utilities."""
from __future__ import annotations

from typing import Generic, Mapping, TypeVar

from pydantic import BaseModel

from .errors import DocumentNotFoundError
from .interfaces import FirestoreGatewayProtocol

TModel = TypeVar("TModel", bound=BaseModel)


class FirestoreRepository(Generic[TModel]):
    """Generic repository with basic CRUD semantics."""

    def __init__(
        self,
        collection: str,
        gateway: FirestoreGatewayProtocol,
        model_type: type[TModel],
    ) -> None:
        self._collection = collection
        self._gateway = gateway
        self._model_type = model_type

    def create(self, payload: Mapping[str, object]) -> TModel:
        """Persist a new document and return the hydrated model."""

        data = dict(payload)
        document_id = data.pop("id", None)
        created_id = self._gateway.add_document(self._collection, data, document_id)
        return self._hydrate(created_id)

    def update(self, document_id: str, payload: Mapping[str, object]) -> TModel:
        """Replace an existing document."""

        if not self._gateway.get_document(self._collection, document_id):
            raise DocumentNotFoundError(f"documento {document_id} nao encontrado")

        data = dict(payload)
        data.pop("id", None)
        self._gateway.add_document(self._collection, data, document_id, merge=False)
        return self._hydrate(document_id)

    def get(self, document_id: str) -> TModel:
        """Return a single document or raise when missing."""

        data = self._gateway.get_document(self._collection, document_id)
        if data is None:
            raise DocumentNotFoundError(f"documento {document_id} nao encontrado")
        return self._model_type.model_validate(data)

    def list(self) -> list[TModel]:
        """Return all documents stored in the collection."""

        items = self._gateway.list_documents(self._collection)
        return [self._model_type.model_validate(item) for item in items]

    def delete(self, document_id: str) -> None:
        """Remove a document. Successful when document exists."""

        if not self._gateway.get_document(self._collection, document_id):
            raise DocumentNotFoundError(f"documento {document_id} nao encontrado")
        self._gateway.delete_document(self._collection, document_id)

    def _hydrate(self, document_id: str) -> TModel:
        data = self._gateway.get_document(self._collection, document_id)
        if data is None:  # pragma: no cover - defensive
            raise DocumentNotFoundError(f"documento {document_id} nao encontrado")
        return self._model_type.model_validate(data)

