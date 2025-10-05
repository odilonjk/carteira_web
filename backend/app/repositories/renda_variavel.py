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

    def list_raw_documents(self) -> list[dict[str, object]]:
        """Return raw documents as stored in the gateway."""

        return [dict(item) for item in self._gateway.list_documents(self._collection)]


class RendaVariavelTradesRepository(FirestoreRepository[RendaVariavelTrade]):
    """Repository bound to renda_variavel_trades."""

    COLLECTION = "renda_variavel_trades"

    def __init__(self, gateway: FirestoreGatewayProtocol) -> None:
        super().__init__(self.COLLECTION, gateway, RendaVariavelTrade)

    def list_by_position(self, position_id: str) -> list[RendaVariavelTrade]:
        """Return trades associated with a single position id."""

        return [
            trade
            for trade in self.list()
            if trade.position_id == position_id
        ]


class RendaVariavelProventosRepository(FirestoreRepository[RendaVariavelProvento]):
    """Repository bound to renda_variavel_proventos."""

    COLLECTION = "renda_variavel_proventos"

    def __init__(self, gateway: FirestoreGatewayProtocol) -> None:
        super().__init__(self.COLLECTION, gateway, RendaVariavelProvento)
