<template>
  <section>
    <h2>Renda Fixa</h2>
    <button type="button" @click="carregar">Atualizar lista</button>
    <pre>{{ rendaFixa }}</pre>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { usePortfolioStore } from '../store';

const portfolioStore = usePortfolioStore();
const { rendaFixa } = storeToRefs(portfolioStore);

const carregar = async () => {
  await portfolioStore.fetchRendaFixa();
};

onMounted(carregar);
</script>
