import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';

import { usePortfolioStore } from '../../src/store';
import { apiClient } from '../../src/services/apiClient';
import type { RendaVariavelCategory } from '../../src/types/rendaVariavel';

vi.mock('../../src/services/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('usePortfolioStore - renda variavel', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.mocked(apiClient.get).mockReset();
    vi.mocked(apiClient.post).mockReset();
    vi.mocked(apiClient.put).mockReset();
    vi.mocked(apiClient.delete).mockReset();
  });

  it('fetches grouped renda variavel data', async () => {
    const store = usePortfolioStore();
    vi.mocked(apiClient.get).mockResolvedValue({
      data: {
        items: {
          acoes: [
            {
              id: 'acao-1',
              ticker: 'PETR4',
              tipo: 'acao_br',
              quantidade: 100,
              preco_medio: 28.5,
              cotacao_atual: 30.1,
              total_compra: 2850,
              total_mercado: 3010,
              resultado_monetario: 160,
              performance_percentual: 5.6,
              peso_percentual: 15,
              peso_desejado_percentual: 18,
              atualizado_em: '2024-02-01T12:00:00Z',
            },
          ],
          fiis: [
            {
              id: 'fii-1',
              ticker: 'VISC11',
              tipo: 'fii',
              quantidade: 50,
              preco_medio: 110,
              cotacao_atual: 115,
              total_compra: 5500,
              total_mercado: 5750,
              resultado_monetario: 250,
              performance_percentual: 4.5,
              peso_percentual: 10,
              peso_desejado_percentual: 12,
              atualizado_em: '2024-02-05T10:00:00Z',
            },
          ],
        },
      },
    });

    const result = await store.fetchRendaVariavel();

    expect(apiClient.get).toHaveBeenCalledWith('/renda-variavel');
    expect(result.acoes[0]?.ticker).toBe('PETR4');
    expect(result.fiis[0]?.ticker).toBe('VISC11');
    expect(store.rendaVariavel.acoes.length).toBe(1);
    expect(store.rendaVariavel.reits.length).toBe(0);
  });

  it('fetches renda variavel positions by category', async () => {
    const store = usePortfolioStore();
    const categoria: RendaVariavelCategory = 'reits';

    vi.mocked(apiClient.get).mockResolvedValue({
      data: {
        items: [
          {
            id: 'reit-1',
            ticker: 'O',
            tipo: 'reit',
            quantidade: 10,
            preco_medio: 55,
            cotacao_atual: 60,
            total_compra: 550,
            total_mercado: 600,
            resultado_monetario: 50,
            performance_percentual: 9.09,
            peso_percentual: 5,
            peso_desejado_percentual: 8,
            atualizado_em: '2024-02-01T12:00:00Z',
          },
        ],
      },
    });

    const items = await store.fetchRendaVariavelByCategory(categoria);

    expect(apiClient.get).toHaveBeenCalledWith('/renda-variavel/reits');
    expect(items).toHaveLength(1);
    expect(store.rendaVariavel[categoria][0]?.ticker).toBe('O');
  });

  it('creates a renda variavel position and updates the store', async () => {
    const store = usePortfolioStore();
    store.$patch({ rendaVariavel: { acoes: [], fiis: [], stocks: [], reits: [], etf: [] } });

    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        item: {
          id: 'acao-1',
          ticker: 'BBAS3',
          tipo: 'acao_br',
          quantidade: 50,
          preco_medio: 30,
          cotacao_atual: 32,
          total_compra: 1500,
          total_mercado: 1600,
          resultado_monetario: 100,
          performance_percentual: 6.66,
          peso_percentual: 60,
          peso_desejado_percentual: 12,
          atualizado_em: '2024-02-01T12:00:00Z',
        },
      },
    });

    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        items: [
          {
            id: 'acao-1',
            ticker: 'BBAS3',
            tipo: 'acao_br',
            quantidade: 50,
            preco_medio: 30,
            cotacao_atual: 32,
            total_compra: 1500,
            total_mercado: 1600,
            resultado_monetario: 100,
            performance_percentual: 6.66,
            peso_percentual: 60,
            peso_desejado_percentual: 12,
            atualizado_em: '2024-02-01T12:00:00Z',
          },
        ],
      },
    });

    const created = await store.createRendaVariavelPosition('acoes', {
      ticker: 'BBAS3',
      quantidade: 50,
      preco_medio: 30,
      cotacao_atual: 32,
      total_compra: 1500,
      total_mercado: 1600,
      resultado_monetario: 100,
      performance_percentual: 6.66,
      peso_desejado_percentual: 12,
      atualizado_em: '2024-02-01T12:00:00Z',
    });

    expect(apiClient.post).toHaveBeenCalledWith('/renda-variavel/acoes', expect.any(Object));
    expect(apiClient.get).toHaveBeenCalledWith('/renda-variavel/acoes');
    expect(store.rendaVariavel.acoes).toHaveLength(1);
    expect(store.rendaVariavel.acoes[0]?.peso_percentual).toBe(60);
    expect(created.peso_percentual).toBe(60);
  });

  it('updates a renda variavel position inside the store', async () => {
    const store = usePortfolioStore();
    store.$patch({
      rendaVariavel: {
        acoes: [
          {
            id: 'acao-1',
            ticker: 'PETR4',
            tipo: 'acao_br',
            quantidade: 100,
            preco_medio: 28,
            cotacao_atual: 30,
            total_compra: 2800,
            total_mercado: 3000,
            resultado_monetario: 200,
            performance_percentual: 7.14,
            peso_percentual: 15,
            peso_desejado_percentual: 18,
            atualizado_em: '2024-02-01T12:00:00Z',
          },
        ],
        fiis: [],
        stocks: [],
        reits: [],
        etf: [],
      },
    });

    vi.mocked(apiClient.put).mockResolvedValue({
      data: {
        item: {
          id: 'acao-1',
          ticker: 'PETR4',
          tipo: 'acao_br',
          quantidade: 120,
          preco_medio: 28,
          cotacao_atual: 32,
          total_compra: 3360,
          total_mercado: 3840,
          resultado_monetario: 480,
          performance_percentual: 12.12,
          peso_percentual: 55,
          peso_desejado_percentual: 20,
          atualizado_em: '2024-03-01T10:00:00Z',
        },
      },
    });

    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        items: [
          {
            id: 'acao-1',
            ticker: 'PETR4',
            tipo: 'acao_br',
            quantidade: 120,
            preco_medio: 28,
            cotacao_atual: 32,
            total_compra: 3360,
            total_mercado: 3840,
            resultado_monetario: 480,
            performance_percentual: 12.12,
            peso_percentual: 55,
            peso_desejado_percentual: 20,
            atualizado_em: '2024-03-01T10:00:00Z',
          },
        ],
      },
    });

    const updated = await store.updateRendaVariavelPosition('acoes', 'acao-1', {
      ticker: 'PETR4',
      quantidade: 120,
      preco_medio: 28,
      cotacao_atual: 32,
      total_compra: 3360,
      total_mercado: 3840,
      resultado_monetario: 480,
      performance_percentual: 12.12,
      peso_desejado_percentual: 20,
      atualizado_em: '2024-03-01T10:00:00Z',
    });

    expect(apiClient.put).toHaveBeenCalledWith('/renda-variavel/acoes/acao-1', expect.any(Object));
    expect(apiClient.get).toHaveBeenCalledWith('/renda-variavel/acoes');
    expect(store.rendaVariavel.acoes[0]?.quantidade).toBe(120);
    expect(store.rendaVariavel.acoes[0]?.peso_percentual).toBe(55);
    expect(updated.peso_percentual).toBe(55);
  });

  it('removes a renda variavel position from the store', async () => {
    const store = usePortfolioStore();
    store.$patch({
      rendaVariavel: {
        acoes: [
          {
            id: 'acao-1',
            ticker: 'PETR4',
            tipo: 'acao_br',
            quantidade: 100,
            preco_medio: 28,
            cotacao_atual: 30,
            total_compra: 2800,
            total_mercado: 3000,
            resultado_monetario: 200,
            performance_percentual: 7.14,
            peso_percentual: 15,
            peso_desejado_percentual: 18,
            atualizado_em: '2024-02-01T12:00:00Z',
          },
        ],
        fiis: [],
        stocks: [],
        reits: [],
        etf: [],
      },
    });

    vi.mocked(apiClient.delete).mockResolvedValue({ data: {} });

    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        items: [],
      },
    });

    await store.deleteRendaVariavelPosition('acoes', 'acao-1');

    expect(apiClient.delete).toHaveBeenCalledWith('/renda-variavel/acoes/acao-1');
    expect(apiClient.get).toHaveBeenCalledWith('/renda-variavel/acoes');
    expect(store.rendaVariavel.acoes).toHaveLength(0);
  });

  it('fetches renda variavel trades for a position', async () => {
    const store = usePortfolioStore();

    vi.mocked(apiClient.get).mockResolvedValue({
      data: {
        items: [
          {
            id: 'trade-1',
            position_id: 'pos-1',
            tipo_operacao: 'compra',
            data: '2024-03-01T10:00:00Z',
            quantidade: 5,
            cotacao: 20,
            total: 100,
            preco_medio_no_ato: 16.5,
            resultado_monetario: null,
            performance_percentual: null,
          },
        ],
      },
    });

    const trades = await store.fetchRendaVariavelTrades('fiis', 'pos-1');

    expect(apiClient.get).toHaveBeenCalledWith('/renda-variavel/fiis/pos-1/transacoes');
    expect(trades).toHaveLength(1);
    expect(store.rendaVariavelTrades['pos-1'][0]?.tipo_operacao).toBe('compra');
  });

  it('creates a renda variavel trade and refreshes data', async () => {
    const store = usePortfolioStore();
    store.$patch({
      rendaVariavel: {
        acoes: [],
        fiis: [
          {
            id: 'pos-1',
            ticker: 'HSML11',
            tipo: 'fii',
            quantidade: 10,
            preco_medio: 100,
            cotacao_atual: 110,
            total_compra: 1000,
            total_mercado: 1100,
            resultado_monetario: 100,
            performance_percentual: 10,
            peso_percentual: 100,
            peso_desejado_percentual: 50,
            atualizado_em: '2024-02-01T12:00:00Z',
          },
        ],
        stocks: [],
        reits: [],
        etf: [],
      },
    });

    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        item: {
          id: 'trade-1',
          position_id: 'pos-1',
          tipo_operacao: 'compra',
          data: '2024-03-01T10:00:00Z',
          quantidade: 5,
          cotacao: 120,
          total: 600,
          preco_medio_no_ato: 105,
          resultado_monetario: null,
          performance_percentual: null,
        },
        position: {
          id: 'pos-1',
          ticker: 'HSML11',
          tipo: 'fii',
          quantidade: 15,
          preco_medio: 105,
          cotacao_atual: 120,
          total_compra: 1575,
          total_mercado: 1800,
          resultado_monetario: 225,
          performance_percentual: 14.2857,
          peso_percentual: 100,
          peso_desejado_percentual: 50,
          atualizado_em: '2024-03-01T10:00:00Z',
        },
      },
    });

    vi.mocked(apiClient.get)
      .mockResolvedValueOnce({
        data: {
          items: [
            {
              id: 'pos-1',
              ticker: 'HSML11',
              tipo: 'fii',
              quantidade: 15,
              preco_medio: 105,
              cotacao_atual: 120,
              total_compra: 1575,
              total_mercado: 1800,
              resultado_monetario: 225,
              performance_percentual: 14.2857,
              peso_percentual: 100,
              peso_desejado_percentual: 50,
              atualizado_em: '2024-03-01T10:00:00Z',
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          items: [
            {
              id: 'trade-1',
              position_id: 'pos-1',
              tipo_operacao: 'compra',
              data: '2024-03-01T10:00:00Z',
              quantidade: 5,
              cotacao: 120,
              total: 600,
              preco_medio_no_ato: 105,
              resultado_monetario: null,
              performance_percentual: null,
            },
          ],
        },
      });

    const result = await store.createRendaVariavelTrade('fiis', 'pos-1', {
      tipo_operacao: 'compra',
      quantidade: 5,
      cotacao: 120,
      data: '2024-03-01T10:00:00Z',
    });

    expect(apiClient.post).toHaveBeenCalledWith('/renda-variavel/fiis/pos-1/transacoes', expect.any(Object));
    expect(apiClient.get).toHaveBeenNthCalledWith(1, '/renda-variavel/fiis');
    expect(apiClient.get).toHaveBeenNthCalledWith(2, '/renda-variavel/fiis/pos-1/transacoes');
    expect(store.rendaVariavelTrades['pos-1']).toHaveLength(1);
    expect(result.trade.id).toBe('trade-1');
    expect(result.position.quantidade).toBe(15);
  });
});
