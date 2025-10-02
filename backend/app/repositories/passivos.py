"""Repository implementation for passivos."""
from __future__ import annotations

from .base import FirestoreRepository
from .interfaces import FirestoreGatewayProtocol
from ..models import Passivo


class PassivosRepository(FirestoreRepository[Passivo]):
    """Concrete repository bound to the `passivos` collection."""

    COLLECTION = "passivos"

    def __init__(self, gateway: FirestoreGatewayProtocol) -> None:
        super().__init__(self.COLLECTION, gateway, Passivo)

