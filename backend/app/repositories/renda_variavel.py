"""Repositories for renda variavel domain."""
from __future__ import annotations

from .base import FirestoreRepository
from .interfaces import FirestoreGatewayProtocol
from ..models import RendaVariavelPosition, RendaVariavelProvento, RendaVariavelTrade


class RendaVariavelPositionsRepository(FirestoreRepository[RendaVariavelPosition]):
    """Repository bound to renda_variavel_positions."""

    COLLECTION = "renda_variavel_positions"

    def __init__(self, gateway: FirestoreGatewayProtocol) -> None:
        super().__init__(self.COLLECTION, gateway, RendaVariavelPosition)


class RendaVariavelTradesRepository(FirestoreRepository[RendaVariavelTrade]):
    """Repository bound to renda_variavel_trades."""

    COLLECTION = "renda_variavel_trades"

    def __init__(self, gateway: FirestoreGatewayProtocol) -> None:
        super().__init__(self.COLLECTION, gateway, RendaVariavelTrade)


class RendaVariavelProventosRepository(FirestoreRepository[RendaVariavelProvento]):
    """Repository bound to renda_variavel_proventos."""

    COLLECTION = "renda_variavel_proventos"

    def __init__(self, gateway: FirestoreGatewayProtocol) -> None:
        super().__init__(self.COLLECTION, gateway, RendaVariavelProvento)

