"""Data access layer interacting with Firestore collections."""

from .base import FirestoreRepository
from .errors import DocumentConflictError, DocumentNotFoundError, PersistenceLayerError, RepositoryError
from .firestore_gateway import FirestoreGateway
from .tinydb_gateway import TinyDbGateway
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
    "TinyDbGateway",
    "FirestoreRepository",
    "PassivosRepository",
    "RendaFixaRepository",
    "RendaVariavelPositionsRepository",
    "RendaVariavelProventosRepository",
    "RendaVariavelTradesRepository",
]
