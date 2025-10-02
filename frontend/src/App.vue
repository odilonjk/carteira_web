<template>
  <main class="layout">
    <header class="layout__header">
      <h1>Carteira Web</h1>
    </header>
    <nav class="layout__nav">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/passivos">Passivos</RouterLink>
      <RouterLink to="/renda-variavel">Renda Variável</RouterLink>
      <RouterLink to="/renda-fixa">Renda Fixa</RouterLink>
    </nav>
    <section class="layout__content">
      <RouterView />
    </section>
  </main>
</template>

<script setup lang="ts">
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-areas:
    "header"
    "nav"
    "content";
  gap: 1rem;
  padding: 1.5rem;
}

.layout__header {
  grid-area: header;
}

.layout__nav {
  grid-area: nav;
  display: flex;
  gap: 1rem;
}

.layout__content {
  grid-area: content;
}
</style>
