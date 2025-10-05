"""Service layer for renda variavel domain operations."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from ..models import (
    RendaVariavelPosition,
    RendaVariavelTipo,
    RendaVariavelTrade,
)
from ..repositories import (
    RendaVariavelPositionsRepository,
    RendaVariavelTradesRepository,
)


class TradeNotAllowedError(Exception):
    """Raised when a trade cannot be executed with the provided payload."""


class RendaVariavelService:
    """Expose read helpers around renda variavel positions."""

    def __init__(
        self,
        repository: RendaVariavelPositionsRepository,
        trades_repository: RendaVariavelTradesRepository | None = None,
    ) -> None:
        self._repository = repository
        self._trades_repository = trades_repository

    def list_positions(self) -> list[RendaVariavelPosition]:
        """Return every stored renda variavel position, skipping corrupt docs."""

        try:
            return self._repository.list()
        except Exception:
            positions: list[RendaVariavelPosition] = []
            raw_documents: list[dict[str, object]] = []
            if hasattr(self._repository, "list_raw_documents"):
                raw_documents = self._repository.list_raw_documents()
            for raw in raw_documents:
                try:
                    positions.append(RendaVariavelPosition.model_validate(raw))
                except Exception:  # pragma: no cover - skip corrupt entries
                    continue
            return positions

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

    def list_trades(self, position_id: str) -> list[RendaVariavelTrade]:
        """Return trades recorded for a given position."""

        trades_repo = self._ensure_trades_repository()
        return trades_repo.list_by_position(position_id)

    def record_trade(
        self,
        position_id: str,
        *,
        tipo_operacao: str,
        quantidade: float,
        cotacao: float,
        data: datetime | None = None,
    ) -> tuple[RendaVariavelPosition, RendaVariavelTrade]:
        """Persist a trade and update the associated position totals."""

        trades_repo = self._ensure_trades_repository()
        position = self._repository.get(position_id)

        quantidade = float(quantidade)
        cotacao = float(cotacao)
        if quantidade <= 0 or cotacao <= 0:
            raise TradeNotAllowedError("quantidade e cotacao devem ser maiores que zero")

        previous_quantidade = float(position.quantidade)
        previous_preco_medio = float(position.preco_medio)
        previous_total_compra = float(position.total_compra)

        tipo_operacao = tipo_operacao.lower()
        if tipo_operacao not in {"compra", "venda"}:
            raise TradeNotAllowedError("tipo de transacao invalido")

        if tipo_operacao == "compra":
            nova_quantidade = previous_quantidade + quantidade
            novo_total_compra = previous_total_compra + quantidade * cotacao
        else:
            if quantidade > previous_quantidade:
                raise TradeNotAllowedError("quantidade vendida excede a quantidade em carteira")
            nova_quantidade = previous_quantidade - quantidade
            novo_total_compra = previous_preco_medio * nova_quantidade

        if nova_quantidade > 0:
            novo_preco_medio = novo_total_compra / nova_quantidade
        else:
            novo_preco_medio = 0.0

        novo_total_mercado = nova_quantidade * cotacao
        novo_resultado = novo_total_mercado - novo_total_compra
        if novo_preco_medio > 0:
            nova_performance = (cotacao / novo_preco_medio - 1) * 100
        else:
            nova_performance = 0.0

        agora = datetime.now(timezone.utc)

        update_payload = {
            "ticker": position.ticker,
            "tipo": position.tipo,
            "quantidade": nova_quantidade,
            "preco_medio": novo_preco_medio,
            "cotacao_atual": cotacao,
            "total_compra": novo_total_compra,
            "total_mercado": novo_total_mercado,
            "resultado_monetario": novo_resultado,
            "performance_percentual": nova_performance,
            "peso_desejado_percentual": position.peso_desejado_percentual,
            "peso_percentual": position.peso_percentual,
            "atualizado_em": agora,
        }

        updated_position = self._repository.update(position_id, update_payload)

        # Persist trade metadata
        trade_payload: dict[str, object] = {
            "position_id": position_id,
            "tipo_operacao": tipo_operacao,
            "data": data or agora,
            "quantidade": quantidade,
            "cotacao": cotacao,
            "total": quantidade * cotacao,
            "preco_medio_no_ato": (
                previous_preco_medio if tipo_operacao == "venda" else novo_preco_medio
            ),
        }

        if tipo_operacao == "venda":
            resultado = (cotacao - previous_preco_medio) * quantidade
            trade_payload["resultado_monetario"] = resultado
            if previous_preco_medio > 0:
                trade_payload["performance_percentual"] = (cotacao / previous_preco_medio - 1) * 100
        else:
            trade_payload["resultado_monetario"] = None
            trade_payload["performance_percentual"] = None

        recorded_trade = trades_repo.create(trade_payload)

        # Recalculate weights using the fresh repository state
        self.recalculate_pesos(updated_position.tipo)
        refreshed_position = self._repository.get(position_id)

        return refreshed_position, recorded_trade

    def _ensure_trades_repository(self) -> RendaVariavelTradesRepository:
        if self._trades_repository is None:
            raise RuntimeError("trades repository nao configurado")
        return self._trades_repository

    def recalculate_pesos(self, tipo: RendaVariavelTipo) -> list[RendaVariavelPosition]:
        """Recalculate peso_percentual for all positions of the given tipo."""

        try:
            positions = [item for item in self.list_positions() if item.tipo is tipo]
        except Exception:
            positions = []
            raw_documents = []
            if hasattr(self._repository, "list_raw_documents"):
                raw_documents = self._repository.list_raw_documents()
            for raw in raw_documents:
                try:
                    position = RendaVariavelPosition.model_validate(raw)
                except Exception:  # pragma: no cover - defensive for corrupt docs
                    continue
                if position.tipo is tipo:
                    positions.append(position)
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
