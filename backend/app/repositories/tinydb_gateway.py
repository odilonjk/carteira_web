"""TinyDB-backed gateway implementing Firestore-like semantics."""
from __future__ import annotations

import os
from typing import Any, Mapping, MutableMapping
from uuid import uuid4

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

from .interfaces import FirestoreGatewayProtocol


class TinyDbGateway(FirestoreGatewayProtocol):
    """Gateway storing documents inside a TinyDB database."""

    def __init__(self, database: TinyDB):
        self._database = database

    @classmethod
    def from_file(cls, path: str) -> "TinyDbGateway":
        """Build a gateway backed by a JSON file or in-memory storage."""
        if path == ":memory:":
            db = TinyDB(storage=MemoryStorage)
            return cls(db)

        normalized = os.path.abspath(path)
        os.makedirs(os.path.dirname(normalized), exist_ok=True)
        db = TinyDB(normalized, indent=2)
        return cls(db)

    def close(self) -> None:
        """Close the underlying database handle."""
        self._database.close()

    def add_document(
        self,
        collection: str,
        payload: Mapping[str, Any],
        document_id: str | None = None,
        merge: bool = False,
    ) -> str:
        table = self._database.table(collection)
        doc_id = document_id or uuid4().hex
        record = dict(payload)

        condition = Query().id == doc_id
        existing = table.get(condition)
        if existing:
            if merge:
                updated: MutableMapping[str, Any] = dict(existing)
                updated.update(record)
                updated["id"] = doc_id
                table.update(updated, condition)
            else:
                table.remove(condition)
                record["id"] = doc_id
                table.insert(record)
        else:
            record["id"] = doc_id
            table.insert(record)

        return doc_id

    def get_document(self, collection: str, document_id: str) -> Mapping[str, Any] | None:
        table = self._database.table(collection)
        document = table.get(Query().id == document_id)
        if document is None:
            return None
        return dict(document)

    def list_documents(self, collection: str) -> list[Mapping[str, Any]]:
        table = self._database.table(collection)
        return [dict(item) for item in table.all()]

    def delete_document(self, collection: str, document_id: str) -> None:
        table = self._database.table(collection)
        table.remove(Query().id == document_id)
