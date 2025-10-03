import { defineStore } from 'pinia';
import { apiClient } from '../services/apiClient';
import type { Passivo, PassivoInput } from '../types/passivo';

export const usePortfolioStore = defineStore('portfolio', {
  state: () => ({
    passivos: [] as Passivo[],
    rendaVariavel: {} as Record<string, unknown[]>,
    rendaFixa: {} as Record<string, unknown[]>,
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
      this.rendaVariavel = response.data.items;
    },
    async fetchRendaFixa() {
      const response = await apiClient.get('/renda-fixa');
      this.rendaFixa = response.data.items;
    },
  },
});
