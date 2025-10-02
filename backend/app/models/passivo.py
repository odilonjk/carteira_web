"""Domain models for passivos."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PassivoCategoria(str, Enum):
    """Identifica o tipo do passivo."""

    FINANCIAMENTO = "financiamento"
    EMPRESTIMO = "emprestimo"
    CARTAO = "cartao"
    OUTROS = "outros"


class Passivo(BaseModel):
    """Modelo principal para documentos da coleção passivos."""

    id: Optional[str] = Field(default=None)
    nome: str = Field(min_length=1)
    categoria: PassivoCategoria
    saldo_atual: float = Field(ge=0)
    taxa_juros_aa: Optional[float] = Field(default=None, ge=0)
    vencimento: Optional[datetime] = None
    observacoes: Optional[str] = Field(default=None, max_length=1024)

    @field_validator("nome")
    def _strip_nome(cls, value: str) -> str:  # noqa: D401
        return value.strip()
