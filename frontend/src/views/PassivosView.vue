<template>
  <section class="passivos-page">
    <header class="page-header">
      <div class="page-title">
        <p class="page-breadcrumb">Visao geral</p>
        <h1>Passivos</h1>
        <p class="page-description">
          Centralize dividas, cartoes e financiamentos para enxergar o impacto no fluxo de caixa.
        </p>
      </div>
      <button class="ghost-button" type="button" @click="carregar" :disabled="isCarregando">
        <ArrowPathIcon class="icon" aria-hidden="true" />
        <span>{{ isCarregando ? 'Atualizando...' : 'Atualizar lista' }}</span>
      </button>
    </header>

    <ul v-if="resumoCards.length" class="insights-grid">
      <li v-for="card in resumoCards" :key="card.label" class="insight-card">
        <component :is="card.icon" class="insight-card__icon" aria-hidden="true" />
        <div>
          <p class="insight-card__label">{{ card.label }}</p>
          <p class="insight-card__value">{{ card.value }}</p>
          <p class="insight-card__helper">{{ card.helper }}</p>
        </div>
      </li>
    </ul>

    <form class="passivo-form" @submit.prevent="salvar">
      <h2 class="section-title">Adicionar novo passivo</h2>
      <div class="form-grid">
        <label class="field">
          <span>Nome</span>
          <input v-model="novoNome" name="nome" placeholder="Cartao Platinum" />
        </label>
        <label class="field">
          <span>Categoria</span>
          <select v-model="novaCategoria" name="categoria">
            <option value="financiamento">Financiamento</option>
            <option value="emprestimo">Emprestimo</option>
            <option value="cartao">Cartao</option>
            <option value="outros">Outros</option>
          </select>
        </label>
        <label class="field">
          <span>Saldo atual (R$)</span>
          <input
            v-model.number="novoSaldo"
            min="0"
            name="saldo"
            step="0.01"
            type="number"
            placeholder="1200.50"
          />
        </label>
        <label class="field">
          <span>Taxa de juros (% a.a.)</span>
          <input
            v-model.number="novaTaxa"
            min="0"
            name="taxaJuros"
            step="0.1"
            type="number"
            placeholder="12.5"
          />
        </label>
        <label class="field">
          <span>Vencimento</span>
          <input v-model="novoVencimento" name="vencimento" type="date" />
        </label>
        <label class="field field--full">
          <span>Observacoes</span>
          <textarea v-model="novasObservacoes" name="observacoes" rows="3" placeholder="Anote detalhes importantes"></textarea>
        </label>
      </div>
      <div class="form-actions">
        <button class="primary-button" :disabled="isSalvando" type="submit">
          <span>{{ isSalvando ? 'Salvando...' : 'Adicionar passivo' }}</span>
        </button>
        <p v-if="erro" class="erro">{{ erro }}</p>
      </div>
    </form>

    <section class="lista-wrapper">
      <header class="lista-header">
        <h2 class="section-title">Passivos cadastrados</h2>
        <p class="lista-subtitle">Acompanhe os vencimentos e organize prioridades de pagamento.</p>
      </header>

      <ul v-if="passivos.length" class="passivos-lista">
        <li v-for="item in passivos" :key="item.id" class="passivo-card">
          <div class="passivo-card__icon" :class="getCategoriaAccent(item.categoria)">
            <component :is="getCategoriaIcon(item.categoria)" aria-hidden="true" />
          </div>
          <div class="passivo-card__body">
            <div class="passivo-card__header">
              <div class="passivo-card__heading">
                <h3>{{ item.nome }}</h3>
                <span class="passivo-card__saldo">{{ formatCurrency(item.saldo_atual) }}</span>
              </div>
              <button
                class="passivo-card__toggle"
                type="button"
                :aria-expanded="isExpanded(item.id)"
                @click="toggleExpand(item.id)"
              >
                {{ isExpanded(item.id) ? 'Recolher detalhes' : 'Ver detalhes' }}
              </button>
            </div>
            <p class="passivo-card__meta">
              <span>{{ getCategoriaLabel(item.categoria) }}</span>
              <span v-if="item.taxa_juros_aa" class="divider">{{ item.taxa_juros_aa }}% a.a.</span>
              <span v-if="item.vencimento" class="divider">Vence em {{ formatDate(item.vencimento) }}</span>
            </p>
            <transition name="passivo-details">
              <div v-if="isExpanded(item.id)" class="passivo-card__details">
                <div class="passivo-card__detail">
                  <span class="passivo-card__detail-label">Taxa de juros</span>
                  <span class="passivo-card__detail-value">
                    {{ item.taxa_juros_aa ? item.taxa_juros_aa + '% a.a.' : 'Sem taxa informada' }}
                  </span>
                </div>
                <div class="passivo-card__detail">
                  <span class="passivo-card__detail-label">Vencimento</span>
                  <span class="passivo-card__detail-value">
                    {{ item.vencimento ? formatDate(item.vencimento) : 'Sem vencimento' }}
                  </span>
                </div>
                <div v-if="item.observacoes" class="passivo-card__detail passivo-card__detail--stacked">
                  <span class="passivo-card__detail-label">Observacoes</span>
                  <p class="passivo-card__notes">{{ item.observacoes }}</p>
                </div>
              </div>
            </transition>
          </div>
        </li>
      </ul>

      <div v-else class="empty-state" role="status">
        <FaceFrownIcon class="empty-state__icon" aria-hidden="true" />
        <p>Nenhum passivo cadastrado ainda.</p>
        <p class="empty-state__helper">Use o formulario acima para comecar a acompanhar seus compromissos.</p>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import {
  ArrowPathIcon,
  BanknotesIcon,
  ChartPieIcon,
  CreditCardIcon,
  DocumentTextIcon,
  FaceFrownIcon,
  HomeModernIcon,
  ScaleIcon,
} from '@heroicons/vue/24/outline';
import type { Component } from 'vue';
import { usePortfolioStore } from '../store';
import type { PassivoInput } from '../types/passivo';

type CategoriaChave = 'financiamento' | 'emprestimo' | 'cartao' | 'outros';

const categoriaConfig: Record<CategoriaChave, { icon: Component; label: string; accent: string }> = {
  financiamento: { icon: HomeModernIcon, label: 'Financiamento', accent: 'accent-financiamento' },
  emprestimo: { icon: ScaleIcon, label: 'Emprestimo', accent: 'accent-emprestimo' },
  cartao: { icon: CreditCardIcon, label: 'Cartao de credito', accent: 'accent-cartao' },
  outros: { icon: DocumentTextIcon, label: 'Outros', accent: 'accent-outros' },
};

const portfolioStore = usePortfolioStore();
const { passivos } = storeToRefs(portfolioStore);

const novoNome = ref('');
const novaCategoria = ref<CategoriaChave>('outros');
const novoSaldo = ref(0);
const novaTaxa = ref<number | null>(null);
const novoVencimento = ref('');
const novasObservacoes = ref('');
const erro = ref('');
const isSalvando = ref(false);
const isCarregando = ref(false);

const formatCurrency = (valor: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor ?? 0);

const formatDate = (valor: string) => {
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) {
    return valor;
  }
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' }).format(data);
};

const carregar = async () => {
  isCarregando.value = true;
  try {
    await portfolioStore.fetchPassivos();
    erro.value = '';
  } catch (err) {
    erro.value = 'Nao foi possivel carregar os passivos.';
  } finally {
    isCarregando.value = false;
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
    const payload: PassivoInput = {
      nome: novoNome.value.trim(),
      categoria: novaCategoria.value,
      saldo_atual: Number(novoSaldo.value),
      taxa_juros_aa: novaTaxa.value ?? undefined,
      vencimento: novoVencimento.value || undefined,
      observacoes: novasObservacoes.value || undefined,
    };

    await portfolioStore.createPassivo(payload);
    erro.value = '';
    novoNome.value = '';
    novaCategoria.value = 'outros';
    novoSaldo.value = 0;
    novaTaxa.value = null;
    novoVencimento.value = '';
    novasObservacoes.value = '';
  } catch (err) {
    erro.value = 'Nao foi possivel salvar o passivo.';
  } finally {
    isSalvando.value = false;
  }
};

const totalSaldo = computed(() => passivos.value.reduce((acc, item) => acc + (item.saldo_atual ?? 0), 0));

const categoriaComMaiorSaldo = computed(() => {
  const agregado = passivos.value.reduce<Record<string, number>>((acc, item) => {
    acc[item.categoria] = (acc[item.categoria] ?? 0) + (item.saldo_atual ?? 0);
    return acc;
  }, {});

  const [categoria] = Object.entries(agregado).sort((a, b) => b[1] - a[1])[0] ?? [];
  return categoria as CategoriaChave | undefined;
});

const saldoMedio = computed(() => {
  if (!passivos.value.length) {
    return 0;
  }
  return totalSaldo.value / passivos.value.length;
});

const resumoCards = computed(() => {
  if (!passivos.value.length) {
    return [] as Array<{ label: string; value: string; helper: string; icon: Component }>;
  }

  const categoriaChave = categoriaComMaiorSaldo.value;
  const categoriaResumo = categoriaChave ? categoriaConfig[categoriaChave] : null;

  return [
    {
      label: 'Saldo total devido',
      value: formatCurrency(totalSaldo.value),
      helper: `${passivos.value.length} passivo(s) registrado(s)`,
      icon: BanknotesIcon,
    },
    {
      label: 'Categoria com maior peso',
      value: categoriaResumo ? categoriaResumo.label : '--',
      helper: categoriaResumo ? 'Priorize amortizacoes nesta categoria' : 'Cadastre ao menos um passivo',
      icon: ChartPieIcon,
    },
    {
      label: 'Saldo medio por passivo',
      value: formatCurrency(saldoMedio.value),
      helper: 'Use como referencia para definir metas mensais',
      icon: ScaleIcon,
    },
  ];
});

const expandedPassivos = ref<Set<string>>(new Set());

const toggleExpand = (id: string) => {
  const next = new Set(expandedPassivos.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  expandedPassivos.value = next;
};

const isExpanded = (id: string) => expandedPassivos.value.has(id);

const getCategoriaIcon = (categoria: string) => {
  const chave = (categoria in categoriaConfig ? categoria : 'outros') as CategoriaChave;
  return categoriaConfig[chave].icon;
};

const getCategoriaLabel = (categoria: string) => {
  const chave = (categoria in categoriaConfig ? categoria : 'outros') as CategoriaChave;
  return categoriaConfig[chave].label;
};

const getCategoriaAccent = (categoria: string) => {
  const chave = (categoria in categoriaConfig ? categoria : 'outros') as CategoriaChave;
  return categoriaConfig[chave].accent;
};

onMounted(carregar);
</script>

<style scoped>
.passivos-page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-bottom: 4rem;
}

.page-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
}

.page-title {
  max-width: 40rem;
}

.page-breadcrumb {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

.page-title h1 {
  margin: 0.25rem 0;
  font-size: 2.25rem;
  color: #0f172a;
  font-weight: 700;
}

.page-description {
  margin: 0;
  color: #475569;
  font-size: 1rem;
}

.ghost-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.15rem;
  border-radius: 0.75rem;
  border: 1px solid #cbd5f5;
  background: #f8fafc;
  color: #1d4ed8;
  font-weight: 600;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.ghost-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.ghost-button:not(:disabled):hover {
  background: #eff6ff;
  border-color: #93c5fd;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
}

.insights-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  list-style: none;
  padding: 0;
  margin: 0;
}

.insight-card {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 1rem;
  border: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}

.insight-card__icon {
  width: 2.25rem;
  height: 2.25rem;
  color: #2563eb;
}

.insight-card__label {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.insight-card__value {
  margin: 0.25rem 0 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

.insight-card__helper {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: #94a3b8;
}

.passivo-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  border-radius: 1rem;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  box-shadow: 0 15px 35px rgba(15, 23, 42, 0.05);
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.form-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field span {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}

.field input,
.field select,
.field textarea {
  border-radius: 0.75rem;
  border: 1px solid #cbd5f5;
  padding: 0.65rem 0.85rem;
  font-size: 0.95rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background: #f8fafc;
  color: #0f172a;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

.field--full {
  grid-column: 1 / -1;
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border-radius: 0.85rem;
  border: none;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: #ffffff;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.primary-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.primary-button:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 15px 25px rgba(79, 70, 229, 0.25);
}

.erro {
  margin: 0;
  color: #dc2626;
  font-weight: 600;
}

.lista-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.lista-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.lista-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
}

.passivos-lista {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.passivo-card {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 1rem;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}

.passivo-card__icon {
  width: 3rem;
  height: 3rem;
  border-radius: 1rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  font-size: 1.5rem;
}

.passivo-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.passivo-card__header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
}

.passivo-card__heading {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.passivo-card__toggle {
  border: 1px solid #dbeafe;
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 0.75rem;
  padding: 0.35rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.passivo-card__toggle:hover {
  background: #dbeafe;
  border-color: #bfdbfe;
}

.passivo-card__toggle:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.passivo-card__header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
}

.passivo-card__saldo {
  font-size: 1.05rem;
  font-weight: 700;
  color: #2563eb;
}

.passivo-card__meta {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #64748b;
}

.passivo-card__details {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.passivo-card__detail {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #475569;
}

.passivo-card__detail--stacked {
  align-items: flex-start;
  flex-direction: column;
}

.passivo-card__detail-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  font-weight: 700;
}

.passivo-card__detail-value {
  font-weight: 600;
  color: #1e293b;
}

.divider::before {
  content: '- ';
}

.passivo-card__notes {
  margin: 0;
  font-size: 0.85rem;
  color: #475569;
  background: #f8fafc;
  border-radius: 0.75rem;
  padding: 0.75rem;
}

.passivo-details-enter-active,
.passivo-details-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.passivo-details-enter-from,
.passivo-details-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.empty-state {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  border-radius: 1rem;
  background: #f8fafc;
  border: 1px dashed #cbd5f5;
  color: #475569;
}

.empty-state__icon {
  width: 2.5rem;
  height: 2.5rem;
  color: #94a3b8;
}

.empty-state__helper {
  margin: 0;
  font-size: 0.9rem;
  color: #94a3b8;
}

.accent-financiamento {
  background: #e0f2fe;
  color: #0369a1;
}

.accent-emprestimo {
  background: #fef3c7;
  color: #b45309;
}

.accent-cartao {
  background: #ede9fe;
  color: #5b21b6;
}

.accent-outros {
  background: #f1f5f9;
  color: #334155;
}

@media (max-width: 640px) {
  .page-title h1 {
    font-size: 1.75rem;
  }

  .passivo-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .passivo-card__icon {
    width: 2.5rem;
    height: 2.5rem;
  }
}
</style>
