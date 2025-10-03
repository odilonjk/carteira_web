<template>
  <main class="layout">
    <header class="topbar">
      <div class="topbar__frame">
        <nav class="topbar__nav" aria-label="Navegacao principal">
          <RouterLink class="topbar__link" to="/">Início</RouterLink>
          <span aria-hidden="true" class="topbar__separator">|</span>
          <RouterLink class="topbar__link" to="/passivos">Passivos</RouterLink>
          <span aria-hidden="true" class="topbar__separator">|</span>
          <RouterLink class="topbar__link" to="/renda-variavel">Renda Variável</RouterLink>
          <span aria-hidden="true" class="topbar__separator">|</span>
          <RouterLink class="topbar__link" to="/renda-fixa">Renda Fixa</RouterLink>
        </nav>
      </div>
    </header>
    <section class="layout__content">
      <RouterView />
    </section>
  </main>
</template>

<script setup lang="ts">
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 20%);
}

.topbar {
  padding: 1.75rem 1.5rem 1.25rem;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(12px);
}

.topbar::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.7);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
  z-index: -1;
}

.topbar__frame {
  max-width: 72rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.topbar__nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.35rem;
}

.topbar__link {
  position: relative;
  padding: 0.35rem 1.25rem;
  color: #475569;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 0.75rem;
  transition: color 0.2s ease;
  text-decoration: none;
}

.topbar__separator {
  color: rgba(148, 163, 184, 0.7);
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  padding-top: 0.1rem;
}

.topbar__link:hover {
  color: #1d4ed8;
}

.topbar__link.router-link-active {
  color: #111827;
}

.layout__content {
  max-width: 72rem;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

@media (max-width: 640px) {
  .topbar {
    padding: 1.25rem 1rem 1rem;
  }

  .topbar__link {
    padding: 0.35rem 0.9rem;
    font-size: 0.7rem;
  }

  .topbar__separator {
    padding: 0;
  }

  .layout__content {
    padding: 1.5rem 1rem 2.5rem;
  }
}
</style>
