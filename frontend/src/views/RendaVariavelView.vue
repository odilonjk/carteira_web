<template>
  <section>
    <h2>Renda Variável</h2>
    <button type="button" @click="carregar">Atualizar lista</button>
    <pre>{{ rendaVariavel }}</pre>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { usePortfolioStore } from '../store';

const portfolioStore = usePortfolioStore();
const { rendaVariavel } = storeToRefs(portfolioStore);

const carregar = async () => {
  await portfolioStore.fetchRendaVariavel();
};

onMounted(carregar);
</script>
