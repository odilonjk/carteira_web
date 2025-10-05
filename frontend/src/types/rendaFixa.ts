export type RendaFixaTipoValue =
  | 'cdb'
  | 'lci'
  | 'lca'
  | 'tesouro_prefixado'
  | 'tesouro_ipca'
  | 'tesouro_selic'
  | 'debenture'
  | 'outros';

export type RendaFixaIndexadorValue = 'pre' | 'pos_cdi' | 'pos_ipca' | 'pos_selic' | 'outros';

export interface RendaFixaPosition {
  id: string | null;
  ativo: string;
  tipo: RendaFixaTipoValue;
  indexador: RendaFixaIndexadorValue;
  rentabilidade_aa: number;
  distribuidor?: string | null;
  valor: number;
  data_inicio: string;
  vencimento: string;
  moeda: string;
}

export interface RendaFixaPositionInput {
  ativo: string;
  tipo: RendaFixaTipoValue;
  indexador: RendaFixaIndexadorValue;
  rentabilidade_aa: number;
  distribuidor?: string | null;
  valor: number;
  data_inicio: string;
  vencimento: string;
  moeda: string;
}
