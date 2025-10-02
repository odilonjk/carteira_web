<template>
  <section>
    <h2>Passivos</h2>
    <button type="button" @click="carregar">Atualizar lista</button>
    <pre>{{ passivos }}</pre>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { usePortfolioStore } from '../store';

const portfolioStore = usePortfolioStore();
const { passivos } = storeToRefs(portfolioStore);

const carregar = async () => {
  await portfolioStore.fetchPassivos();
};

onMounted(carregar);
</script>
