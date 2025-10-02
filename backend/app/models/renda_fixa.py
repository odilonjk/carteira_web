"""Domain models for renda fixa positions."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RendaFixaTipo(str, Enum):
    """Tipos de ativos de renda fixa suportados."""

    CDB = "cdb"
    LCI = "lci"
    LCA = "lca"
    TESOURO_PREFIXADO = "tesouro_prefixado"
    TESOURO_IPCA = "tesouro_ipca"
    TESOURO_SELIC = "tesouro_selic"
    DEBENTURE = "debenture"
    OUTROS = "outros"


class RendaFixaIndexador(str, Enum):
    """Indexadores aceitos para renda fixa."""

    PRE = "pre"
    POS_CDI = "pos_cdi"
    POS_IPCA = "pos_ipca"
    POS_SELIC = "pos_selic"
    OUTROS = "outros"


class RendaFixaPosition(BaseModel):
    """Documento principal para a coleção renda_fixa_positions."""

    id: Optional[str] = Field(default=None)
    ativo: str = Field(min_length=1)
    tipo: RendaFixaTipo
    indexador: RendaFixaIndexador
    rentabilidade_aa: float = Field(ge=0)
    distribuidor: Optional[str] = Field(default=None, max_length=128)
    valor: float = Field(gt=0)
    data_inicio: datetime
    vencimento: datetime
    moeda: str = Field(default="brl", min_length=3, max_length=3)

