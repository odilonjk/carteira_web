"""Interfaces and protocols used by repository implementations."""
from __future__ import annotations

from typing import Any, Iterable, Mapping, MutableMapping, Protocol


class SupportsDocument(Protocol):
    """Minimum shape for Firestore-like documents."""

    id: str
    exists: bool

    def to_dict(self) -> Mapping[str, Any]:
        """Return the document payload as a dict."""


class SupportsCollection(Protocol):
    """Minimal operations required from a Firestore collection reference."""

    def document(self, document_id: str | None = None) -> SupportsDocumentReference:
        """Return a document reference."""

    def stream(self) -> Iterable[SupportsDocument]:
        """Return an iterable with all documents in the collection."""


class SupportsDocumentReference(Protocol):
    """Minimal operations required from a Firestore document reference."""

    @property
    def id(self) -> str:
        """Return the document identifier."""

    def get(self) -> SupportsDocument:
        """Fetch the document snapshot."""

    def set(self, payload: MutableMapping[str, Any], merge: bool = False) -> None:
        """Persist the payload on Firestore."""

    def delete(self) -> None:
        """Delete the document."""


class FirestoreGatewayProtocol(Protocol):
    """Operations exposed by the Firestore gateway abstraction."""

    def add_document(
        self,
        collection: str,
        payload: Mapping[str, Any],
        document_id: str | None = None,
        merge: bool = False,
    ) -> str:
        """Create or update a document and return its id."""

    def get_document(self, collection: str, document_id: str) -> Mapping[str, Any] | None:
        """Return the data for a document or None if missing."""

    def list_documents(self, collection: str) -> list[Mapping[str, Any]]:
        """Return all documents in the collection."""

    def delete_document(self, collection: str, document_id: str) -> None:
        """Remove a document from the collection."""
