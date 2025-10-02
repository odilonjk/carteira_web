import { defineStore } from 'pinia';
import { apiClient } from '../services/apiClient';

export const usePortfolioStore = defineStore('portfolio', {
  state: () => ({
    passivos: [] as unknown[],
    rendaVariavel: {} as Record<string, unknown[]>,
    rendaFixa: {} as Record<string, unknown[]>,
  }),
  actions: {
    async fetchPassivos() {
      const response = await apiClient.get('/passivos');
      this.passivos = response.data.items;
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
