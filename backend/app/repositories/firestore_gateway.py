"""Firestore gateway implementation."""
from __future__ import annotations

from typing import Any, Mapping

from google.api_core import exceptions as google_exceptions
from google.cloud import firestore

from .errors import PersistenceLayerError
from .interfaces import FirestoreGatewayProtocol


class FirestoreGateway(FirestoreGatewayProtocol):
    """Concrete gateway that wraps a google-cloud-firestore client."""

    def __init__(self, client: firestore.Client):
        self._client = client

    @classmethod
    def from_settings(
        cls,
        project_id: str | None = None,
        namespace: str | None = None,
    ) -> "FirestoreGateway":
        """Factory that respects emulator configuration automatically."""

        client = firestore.Client(project=project_id, namespace=namespace)
        return cls(client)

    def add_document(
        self,
        collection: str,
        payload: Mapping[str, Any],
        document_id: str | None = None,
        merge: bool = False,
    ) -> str:
        try:
            collection_ref = self._client.collection(collection)
            doc_ref = collection_ref.document(document_id) if document_id else collection_ref.document()
            doc_ref.set(dict(payload), merge=merge)
            return doc_ref.id
        except google_exceptions.GoogleAPICallError as exc:  # pragma: no cover - defensive
            raise PersistenceLayerError("erro ao salvar documento no firestore") from exc

    def get_document(self, collection: str, document_id: str) -> Mapping[str, Any] | None:
        try:
            snapshot = self._client.collection(collection).document(document_id).get()
        except google_exceptions.GoogleAPICallError as exc:  # pragma: no cover - defensive
            raise PersistenceLayerError("erro ao buscar documento no firestore") from exc

        if not snapshot.exists:
            return None

        data = snapshot.to_dict() or {}
        data.setdefault("id", snapshot.id)
        return data

    def list_documents(self, collection: str) -> list[Mapping[str, Any]]:
        try:
            snapshots = self._client.collection(collection).stream()
        except google_exceptions.GoogleAPICallError as exc:  # pragma: no cover - defensive
            raise PersistenceLayerError("erro ao listar documentos no firestore") from exc

        items: list[Mapping[str, Any]] = []
        for snapshot in snapshots:
            data = snapshot.to_dict() or {}
            data.setdefault("id", snapshot.id)
            items.append(data)
        return items

    def delete_document(self, collection: str, document_id: str) -> None:
        try:
            self._client.collection(collection).document(document_id).delete()
        except google_exceptions.GoogleAPICallError as exc:  # pragma: no cover - defensive
            raise PersistenceLayerError("erro ao excluir documento no firestore") from exc

