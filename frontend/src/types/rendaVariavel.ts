export type RendaVariavelCategory = 'acoes' | 'fiis' | 'stocks' | 'reits' | 'etf';

export type RendaVariavelTipoValue =
  | 'fii'
  | 'acao_br'
  | 'stock_us'
  | 'etf'
  | 'reit'
  | 'fundo_investimento'
  | 'outros';

export interface RendaVariavelPosition {
  id: string | null;
  ticker: string;
  tipo: RendaVariavelTipoValue;
  quantidade: number;
  preco_medio: number;
  cotacao_atual: number;
  total_compra: number;
  total_mercado: number;
  resultado_monetario: number;
  performance_percentual: number;
  peso_percentual: number;
  peso_desejado_percentual: number;
  atualizado_em: string;
}

export interface RendaVariavelPositionInput {
  ticker: string;
  quantidade: number;
  preco_medio: number;
  cotacao_atual: number;
  total_compra: number;
  total_mercado: number;
  resultado_monetario: number;
  performance_percentual: number;
  peso_desejado_percentual: number;
  atualizado_em: string;
}

export interface RendaVariavelTrade {
  id: string | null;
  position_id: string;
  tipo_operacao: 'compra' | 'venda';
  data: string;
  quantidade: number;
  cotacao: number;
  total: number;
  preco_medio_no_ato: number | null;
  resultado_monetario: number | null;
  performance_percentual: number | null;
}

export interface RendaVariavelTradeInput {
  tipo_operacao: 'compra' | 'venda';
  quantidade: number;
  cotacao: number;
  data?: string;
}
