"""Repository for renda fixa positions."""
from __future__ import annotations

from .base import FirestoreRepository
from .interfaces import FirestoreGatewayProtocol
from ..models import RendaFixaPosition


class RendaFixaRepository(FirestoreRepository[RendaFixaPosition]):
    """Concrete repository bound to renda_fixa_positions."""

    COLLECTION = "renda_fixa_positions"

    def __init__(self, gateway: FirestoreGatewayProtocol) -> None:
        super().__init__(self.COLLECTION, gateway, RendaFixaPosition)

