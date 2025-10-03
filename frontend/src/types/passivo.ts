export interface Passivo {
  id: string;
  nome: string;
  categoria: string;
  saldo_atual: number;
  taxa_juros_aa?: number;
  vencimento?: string;
  observacoes?: string;
}

export type PassivoInput = Omit<Passivo, 'id'>;
