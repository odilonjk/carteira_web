"""Data access layer interacting with Firestore collections."""

from .base import FirestoreRepository
from .errors import DocumentConflictError, DocumentNotFoundError, PersistenceLayerError, RepositoryError
from .firestore_gateway import FirestoreGateway
from .passivos import PassivosRepository
from .renda_fixa import RendaFixaRepository
from .renda_variavel import (
    RendaVariavelPositionsRepository,
    RendaVariavelProventosRepository,
    RendaVariavelTradesRepository,
)

__all__ = [
    "DocumentConflictError",
    "DocumentNotFoundError",
    "PersistenceLayerError",
    "RepositoryError",
    "FirestoreGateway",
    "FirestoreRepository",
    "PassivosRepository",
    "RendaFixaRepository",
    "RendaVariavelPositionsRepository",
    "RendaVariavelProventosRepository",
    "RendaVariavelTradesRepository",
]
