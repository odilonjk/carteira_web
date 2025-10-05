import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';

import { usePortfolioStore } from '../../src/store';
import { apiClient } from '../../src/services/apiClient';

vi.mock('../../src/services/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('usePortfolioStore - renda fixa', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.mocked(apiClient.get).mockReset();
    vi.mocked(apiClient.post).mockReset();
    vi.mocked(apiClient.put).mockReset();
    vi.mocked(apiClient.delete).mockReset();
  });

  const samplePayload = {
    id: 'rf-1',
    ativo: 'Tesouro IPCA 2029',
    tipo: 'tesouro_ipca',
    indexador: 'pos_ipca',
    rentabilidade_aa: 5.5,
    distribuidor: 'Tesouro Direto',
    valor: 2500,
    data_inicio: '2024-01-01T12:00:00Z',
    vencimento: '2029-01-01T12:00:00Z',
    moeda: 'brl',
  } as const;

  it('fetches renda fixa positions', async () => {
    const store = usePortfolioStore();
    vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [samplePayload] } });

    await store.fetchRendaFixa();

    expect(apiClient.get).toHaveBeenCalledWith('/renda-fixa');
    expect(store.rendaFixa).toHaveLength(1);
    expect(store.rendaFixa[0]?.ativo).toBe('Tesouro IPCA 2029');
  });

  it('creates a renda fixa position', async () => {
    const store = usePortfolioStore();
    vi.mocked(apiClient.post).mockResolvedValue({ data: { item: samplePayload } });
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: { items: [samplePayload] } });

    const created = await store.createRendaFixaPosition({
      ativo: 'Tesouro IPCA 2029',
      tipo: 'tesouro_ipca',
      indexador: 'pos_ipca',
      rentabilidade_aa: 5.5,
      distribuidor: 'Tesouro Direto',
      valor: 2500,
      data_inicio: '2024-01-01T12:00:00Z',
      vencimento: '2029-01-01T12:00:00Z',
      moeda: 'brl',
    });

    expect(apiClient.post).toHaveBeenCalledWith('/renda-fixa', expect.any(Object));
    expect(apiClient.get).toHaveBeenCalledWith('/renda-fixa');
    expect(store.rendaFixa).toHaveLength(1);
    expect(created.id).toBe('rf-1');
  });

  it('updates a renda fixa position', async () => {
    const store = usePortfolioStore();
    store.$patch({ rendaFixa: [JSON.parse(JSON.stringify(samplePayload))] });

    vi.mocked(apiClient.put).mockResolvedValue({
      data: {
        item: {
          ...samplePayload,
          rentabilidade_aa: 6,
        },
      },
    });

    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        items: [
          {
            ...samplePayload,
            rentabilidade_aa: 6,
          },
        ],
      },
    });

    const updated = await store.updateRendaFixaPosition('rf-1', {
      ativo: 'Tesouro IPCA 2029',
      tipo: 'tesouro_ipca',
      indexador: 'pos_ipca',
      rentabilidade_aa: 6,
      distribuidor: 'Tesouro Direto',
      valor: 2500,
      data_inicio: '2024-01-01T12:00:00Z',
      vencimento: '2029-01-01T12:00:00Z',
      moeda: 'brl',
    });

    expect(apiClient.put).toHaveBeenCalledWith('/renda-fixa/rf-1', expect.any(Object));
    expect(apiClient.get).toHaveBeenCalledWith('/renda-fixa');
    expect(store.rendaFixa[0]?.rentabilidade_aa).toBe(6);
    expect(updated.rentabilidade_aa).toBe(6);
  });

  it('deletes a renda fixa position', async () => {
    const store = usePortfolioStore();
    store.$patch({ rendaFixa: [JSON.parse(JSON.stringify(samplePayload))] });

    vi.mocked(apiClient.delete).mockResolvedValue({ data: {} });
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: { items: [] } });

    await store.deleteRendaFixaPosition('rf-1');

    expect(apiClient.delete).toHaveBeenCalledWith('/renda-fixa/rf-1');
    expect(apiClient.get).toHaveBeenCalledWith('/renda-fixa');
    expect(store.rendaFixa).toHaveLength(0);
  });
});
