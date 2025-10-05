"""Service layer for renda variavel domain operations."""
from __future__ import annotations

from typing import Iterable

from ..models import RendaVariavelPosition, RendaVariavelTipo
from ..repositories import RendaVariavelPositionsRepository


class RendaVariavelService:
    """Expose read helpers around renda variavel positions."""

    def __init__(self, repository: RendaVariavelPositionsRepository) -> None:
        self._repository = repository

    def list_positions(self) -> list[RendaVariavelPosition]:
        """Return every stored renda variavel position."""
        return self._repository.list()

    def list_positions_by_tipo(self, tipo: RendaVariavelTipo) -> list[RendaVariavelPosition]:
        """Return only positions belonging to the provided tipo."""
        return [item for item in self.list_positions() if item.tipo is tipo]

    def list_positions_grouped(
        self, tipos: Iterable[RendaVariavelTipo]
    ) -> dict[RendaVariavelTipo, list[RendaVariavelPosition]]:
        """Group positions by the provided tipos preserving the iteration order."""
        tipos_tuple = tuple(tipos)
        filtered: dict[RendaVariavelTipo, list[RendaVariavelPosition]] = {
            tipo: [] for tipo in tipos_tuple
        }

        all_positions = self.list_positions()
        for position in all_positions:
            if position.tipo in filtered:
                filtered[position.tipo].append(position)

        return filtered

    def recalculate_pesos(self, tipo: RendaVariavelTipo) -> list[RendaVariavelPosition]:
        """Recalculate peso_percentual for all positions of the given tipo."""

        positions = [item for item in self.list_positions() if item.tipo is tipo]
        if not positions:
            return []

        total_mercado = sum(max(item.total_mercado or 0.0, 0.0) for item in positions)
        recalculated: list[RendaVariavelPosition] = []

        for position in positions:
            if position.id is None:
                continue

            novo_peso = 0.0
            if total_mercado > 0:
                novo_peso = (position.total_mercado or 0.0) / total_mercado * 100

            payload = position.model_dump(mode="json", exclude_none=True, exclude={"id"})
            payload["peso_percentual"] = novo_peso
            updated = self._repository.update(position.id, payload)
            recalculated.append(updated)

        return recalculated
