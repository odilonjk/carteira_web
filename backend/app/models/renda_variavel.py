"""Domain models for renda variavel assets."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RendaVariavelTipo(str, Enum):
    """Tipos de ativos de renda variavel suportados."""

    FII = "fii"
    ACAO_BR = "acao_br"
    STOCK_US = "stock_us"
    ETF = "etf"
    REIT = "reit"
    FUNDO_INVESTIMENTO = "fundo_investimento"
    OUTROS = "outros"


class Moeda(str, Enum):
    """Moedas permitidas para ativos e proventos."""

    BRL = "brl"
    USD = "usd"


class RendaVariavelPosition(BaseModel):
    """Documento principal a ser armazenado em renda_variavel_positions."""

    id: Optional[str] = Field(default=None)
    ticker: str = Field(min_length=1)
    tipo: RendaVariavelTipo
    quantidade: float = Field(ge=0)
    preco_medio: float = Field(ge=0)
    cotacao_atual: float = Field(ge=0)
    total_compra: float = Field(ge=0)
    total_mercado: float = Field(ge=0)
    resultado_monetario: float
    performance_percentual: float
    peso_percentual: float = Field(ge=0)
    peso_desejado_percentual: float = Field(ge=0)
    atualizado_em: datetime


class RendaVariavelTrade(BaseModel):
    """Movimentações de compra e venda de ativos de renda variável."""

    id: Optional[str] = Field(default=None)
    position_id: str = Field(min_length=1)
    tipo_operacao: str = Field(pattern="^(compra|venda)$")
    data: datetime
    quantidade: float = Field(gt=0)
    cotacao: float = Field(gt=0)
    total: float = Field(gt=0)
    preco_medio_no_ato: Optional[float] = Field(default=None, ge=0)
    resultado_monetario: Optional[float] = None
    performance_percentual: Optional[float] = None


class RendaVariavelProvento(BaseModel):
    """Proventos associados a ativos de renda variavel."""

    id: Optional[str] = Field(default=None)
    position_id: str = Field(min_length=1)
    tipo_provento: str = Field(min_length=1)
    data: datetime
    valor_monetario: float = Field(gt=0)
    moeda: Moeda = Moeda.BRL

