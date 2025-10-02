"""Custom exceptions for repository interactions."""
from __future__ import annotations


class RepositoryError(RuntimeError):
    """Base error for persistence operations."""


class DocumentNotFoundError(RepositoryError):
    """Raised when a requested document does not exist."""


class DocumentConflictError(RepositoryError):
    """Raised when a document already exists and cannot be overwritten."""


class PersistenceLayerError(RepositoryError):
    """Raised when the datastore interaction fails irrecoverably."""

