<template>
  <section>
    <h2>Passivos</h2>

    <form class="passivo-form" @submit.prevent="salvar">
      <label>
        Nome
        <input v-model="novoNome" name="nome" placeholder="Cartão" />
      </label>
      <label>
        Categoria
        <select v-model="novaCategoria" name="categoria">
          <option value="financiamento">Financiamento</option>
          <option value="emprestimo">Emprestimo</option>
          <option value="cartao">Cartão</option>
          <option value="outros">Outros</option>
        </select>
      </label>
      <label>
        Saldo atual (R$)
        <input v-model.number="novoSaldo" min="0" name="saldo" step="0.01" type="number" />
      </label>
      <button :disabled="isSalvando" type="submit">Adicionar</button>
      <button type="button" @click="carregar">Atualizar lista</button>
    </form>

    <p v-if="erro" class="erro">{{ erro }}</p>

    <ul class="passivos-lista">
      <li v-for="item in passivos" :key="item.id">
        <strong>{{ item.nome }}</strong>
        <span> • {{ item.categoria }} • Saldo: R$ {{ item.saldo_atual.toFixed(2) }}</span>
      </li>
    </ul>

    <p v-if="!passivos.length">Nenhum passivo cadastrado ainda.</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { usePortfolioStore } from '../store';

const portfolioStore = usePortfolioStore();
const { passivos } = storeToRefs(portfolioStore);

const novoNome = ref('');
const novaCategoria = ref('outros');
const novoSaldo = ref(0);
const erro = ref('');
const isSalvando = ref(false);

const carregar = async () => {
  try {
    await portfolioStore.fetchPassivos();
  } catch (err) {
    erro.value = 'Nao foi possivel carregar os passivos.';
  }
};

const salvar = async () => {
  if (!novoNome.value.trim()) {
    erro.value = 'Informe o nome do passivo.';
    return;
  }

  erro.value = '';
  isSalvando.value = true;
  try {
    await portfolioStore.createPassivo({
      nome: novoNome.value.trim(),
      categoria: novaCategoria.value,
      saldo_atual: Number(novoSaldo.value),
    });
    novoNome.value = '';
    novaCategoria.value = 'outros';
    novoSaldo.value = 0;
  } catch (err) {
    erro.value = 'Nao foi possivel salvar o passivo.';
  } finally {
    isSalvando.value = false;
  }
};

onMounted(carregar);
</script>

<style scoped>
.passivo-form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.passivo-form label {
  display: flex;
  flex-direction: column;
}

.passivos-lista {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.erro {
  color: #c0392b;
}
</style>
