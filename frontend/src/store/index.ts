import { defineStore } from 'pinia';
import { apiClient } from '../services/apiClient';
import type { Passivo, PassivoInput } from '../types/passivo';
import type {
  RendaVariavelCategory,
  RendaVariavelPosition,
  RendaVariavelPositionInput,
} from '../types/rendaVariavel';
import type { RendaFixaPosition, RendaFixaPositionInput } from '../types/rendaFixa';

const createEmptyRendaVariavelState = (): Record<RendaVariavelCategory, RendaVariavelPosition[]> => ({
  acoes: [],
  fiis: [],
  stocks: [],
  reits: [],
  etf: [],
});

export const usePortfolioStore = defineStore('portfolio', {
  state: () => ({
    passivos: [] as Passivo[],
    rendaVariavel: createEmptyRendaVariavelState(),
    rendaFixa: [] as RendaFixaPosition[],
  }),
  actions: {
    async fetchPassivos() {
      const response = await apiClient.get('/passivos');
      this.passivos = response.data.items as Passivo[];
    },
    async createPassivo(payload: PassivoInput) {
      const response = await apiClient.post('/passivos', payload);
      const created = response.data.item as Passivo;
      this.passivos = [...this.passivos, created];
      return created;
    },
    async updatePassivo(id: string, payload: PassivoInput) {
      const response = await apiClient.put(`/passivos/${id}`, payload);
      const updated = response.data.item as Passivo;
      this.passivos = this.passivos.map((item) => (item.id === id ? updated : item));
      return updated;
    },
    async deletePassivo(id: string) {
      await apiClient.delete(`/passivos/${id}`);
      this.passivos = this.passivos.filter((item) => item.id !== id);
    },
    async fetchRendaVariavel() {
      const response = await apiClient.get('/renda-variavel');
      const grouped = response.data.items as Partial<Record<RendaVariavelCategory, RendaVariavelPosition[]>>;
      const nextState = createEmptyRendaVariavelState();
      (Object.keys(nextState) as RendaVariavelCategory[]).forEach((categoria) => {
        nextState[categoria] = (grouped[categoria] ?? []) as RendaVariavelPosition[];
      });
      this.rendaVariavel = nextState;
      return nextState;
    },
    async fetchRendaVariavelByCategory(categoria: RendaVariavelCategory) {
      const response = await apiClient.get(`/renda-variavel/${categoria}`);
      const items = response.data.items as RendaVariavelPosition[];
      this.rendaVariavel = {
        ...this.rendaVariavel,
        [categoria]: items,
      };
      return items;
    },
    async fetchRendaFixa() {
      const response = await apiClient.get('/renda-fixa');
      this.rendaFixa = response.data.items as RendaFixaPosition[];
      return this.rendaFixa;
    },
    async createRendaFixaPosition(payload: RendaFixaPositionInput) {
      const response = await apiClient.post('/renda-fixa', payload);
      const created = response.data.item as RendaFixaPosition;
      await this.fetchRendaFixa();
      return created;
    },
    async updateRendaFixaPosition(id: string, payload: RendaFixaPositionInput) {
      const response = await apiClient.put(`/renda-fixa/${id}`, payload);
      const updated = response.data.item as RendaFixaPosition;
      await this.fetchRendaFixa();
      return updated;
    },
    async deleteRendaFixaPosition(id: string) {
      await apiClient.delete(`/renda-fixa/${id}`);
      await this.fetchRendaFixa();
    },
    async createRendaVariavelPosition(
      categoria: RendaVariavelCategory,
      payload: RendaVariavelPositionInput,
    ) {
      const response = await apiClient.post(`/renda-variavel/${categoria}`, payload);
      const created = response.data.item as RendaVariavelPosition;
      await this.fetchRendaVariavelByCategory(categoria);
      return created;
    },
    async updateRendaVariavelPosition(
      categoria: RendaVariavelCategory,
      id: string,
      payload: RendaVariavelPositionInput,
    ) {
      const response = await apiClient.put(`/renda-variavel/${categoria}/${id}`, payload);
      const updated = response.data.item as RendaVariavelPosition;
      await this.fetchRendaVariavelByCategory(categoria);
      return updated;
    },
    async deleteRendaVariavelPosition(categoria: RendaVariavelCategory, id: string) {
      await apiClient.delete(`/renda-variavel/${categoria}/${id}`);
      await this.fetchRendaVariavelByCategory(categoria);
    },
  },
});
