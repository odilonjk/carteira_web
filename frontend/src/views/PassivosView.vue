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

    <section class="lista-wrapper">
      <header class="lista-header">
        <div class="lista-header__info">
          <h2 class="section-title">Passivos cadastrados</h2>
          <p class="lista-subtitle">Acompanhe os vencimentos e organize prioridades de pagamento.</p>
          <p v-if="listaErro" class="erro erro--inline">{{ listaErro }}</p>
        </div>
        <button
          class="add-passivo-button"
          type="button"
          @click="criarNovoPassivo"
          :disabled="newCardId !== null || isCarregando"
        >
          {{ newCardId ? 'Passivo em criacao' : 'Novo passivo' }}
        </button>
      </header>

      <ul v-if="cards.length" class="passivos-lista">
        <li
          v-for="item in cards"
          :key="item.id"
          :class="['passivo-card', { 'passivo-card--editing': isEditing(item.id) }]"
        >
          <div class="passivo-card__icon" :class="getCategoriaAccent(displayCategoriaKey(item))">
            <component :is="getCategoriaIcon(displayCategoriaKey(item))" aria-hidden="true" />
          </div>
          <div class="passivo-card__body">
            <div class="passivo-card__header">
              <div class="passivo-card__heading">
                <h3>{{ displayNome(item) }}</h3>
                <span class="passivo-card__saldo">{{ displaySaldo(item) }}</span>
              </div>
              <div class="passivo-card__actions">
                <button
                  class="passivo-card__toggle"
                  type="button"
                  :aria-expanded="isExpanded(item.id)"
                  @click="toggleExpand(item.id)"
                >
                  {{ isExpanded(item.id) ? 'Recolher detalhes' : 'Ver detalhes' }}
                </button>
                <template v-if="isEditing(item.id)">
                  <button
                    class="passivo-card__save"
                    type="button"
                    @click="salvarEdicao(item.id)"
                    :disabled="isSaving(item.id)"
                  >
                    {{ isSaving(item.id) ? 'Salvando...' : 'Salvar' }}
                  </button>
                  <button
                    class="passivo-card__cancel"
                    type="button"
                    @click="cancelar(item.id)"
                    :disabled="isSaving(item.id)"
                  >
                    Cancelar
                  </button>
                </template>
                <template v-else>
                  <button class="passivo-card__edit" type="button" @click="iniciarEdicao(item)">
                    Editar
                  </button>
                  <button
                    class="passivo-card__delete"
                    type="button"
                    @click="remover(item.id)"
                    :disabled="isRemovendo(item.id)"
                  >
                    {{ isRemovendo(item.id) ? 'Removendo...' : 'Remover' }}
                  </button>
                </template>
              </div>
            </div>
            <p class="passivo-card__meta">
              <span>{{ displayCategoriaLabel(item) }}</span>
              <span v-if="displayTaxa(item)" class="divider">{{ displayTaxa(item) }}</span>
              <span v-if="displayVencimento(item)" class="divider">Vence em {{ displayVencimento(item) }}</span>
            </p>
            <transition name="passivo-details">
              <div v-if="isExpanded(item.id)" class="passivo-card__details">
                <template v-if="isEditing(item.id)">
                  <div class="passivo-card__edit-grid">
                    <label class="field">
                      <span>Nome</span>
                      <input v-model="drafts[item.id].nome" placeholder="Cartao Platinum" />
                    </label>
                    <label class="field">
                      <span>Categoria</span>
                      <select v-model="drafts[item.id].categoria">
                        <option value="financiamento">Financiamento</option>
                        <option value="emprestimo">Emprestimo</option>
                        <option value="cartao">Cartao</option>
                        <option value="outros">Outros</option>
                      </select>
                    </label>
                    <label class="field">
                      <span>Saldo atual (R$)</span>
                      <input
                        v-model.number="drafts[item.id].saldo_atual"
                        min="0"
                        step="0.01"
                        type="number"
                        placeholder="1200.50"
                      />
                    </label>
                    <label class="field">
                      <span>Taxa de juros (% a.a.)</span>
                      <input
                        v-model.number="drafts[item.id].taxa_juros_aa"
                        min="0"
                        step="0.1"
                        type="number"
                        placeholder="12.5"
                      />
                    </label>
                    <label class="field">
                      <span>Vencimento</span>
                      <input v-model="drafts[item.id].vencimento" type="date" />
                    </label>
                    <label class="field field--span-full">
                      <span>Observacoes</span>
                      <textarea
                        v-model="drafts[item.id].observacoes"
                        rows="3"
                        placeholder="Anote detalhes importantes"
                      ></textarea>
                    </label>
                  </div>
                  <p v-if="erros[item.id]" class="erro passivo-card__erro">{{ erros[item.id] }}</p>
                </template>
                <template v-else>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Taxa de juros</span>
                    <span class="passivo-card__detail-value">
                      {{ displayTaxa(item) ?? 'Sem taxa informada' }}
                    </span>
                  </div>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Vencimento</span>
                    <span class="passivo-card__detail-value">
                      {{ displayVencimento(item) ?? 'Sem vencimento' }}
                    </span>
                  </div>
                  <div v-if="displayObservacoes(item)" class="passivo-card__detail passivo-card__detail--stacked">
                    <span class="passivo-card__detail-label">Observacoes</span>
                    <p class="passivo-card__notes">{{ displayObservacoes(item) }}</p>
                  </div>
                </template>
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
import { computed, onMounted, reactive, ref } from 'vue';
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
import type { Passivo, PassivoInput } from '../types/passivo';

type CategoriaChave = 'financiamento' | 'emprestimo' | 'cartao' | 'outros';
type PassivoDraft = {
  nome: string;
  categoria: CategoriaChave;
  saldo_atual: number;
  taxa_juros_aa: number | null;
  vencimento: string;
  observacoes: string;
};

const categoriaConfig: Record<CategoriaChave, { icon: Component; label: string; accent: string }> = {
  financiamento: { icon: HomeModernIcon, label: 'Financiamento', accent: 'accent-financiamento' },
  emprestimo: { icon: ScaleIcon, label: 'Emprestimo', accent: 'accent-emprestimo' },
  cartao: { icon: CreditCardIcon, label: 'Cartao de credito', accent: 'accent-cartao' },
  outros: { icon: DocumentTextIcon, label: 'Outros', accent: 'accent-outros' },
};

const portfolioStore = usePortfolioStore();
const { passivos } = storeToRefs(portfolioStore);

const drafts = reactive<Record<string, PassivoDraft>>({});
const erros = reactive<Record<string, string>>({});
const expandedPassivos = ref<Set<string>>(new Set());
const editingId = ref<string | null>(null);
const savingId = ref<string | null>(null);
const isCarregando = ref(false);
const isRemovendoId = ref<string | null>(null);
const newCardId = ref<string | null>(null);
const listaErro = ref('');

const cards = computed<Passivo[]>(() => {
  if (!newCardId.value) {
    return passivos.value;
  }

  const draft = drafts[newCardId.value];
  if (!draft) {
    return passivos.value;
  }

  const placeholder: Passivo = {
    id: newCardId.value,
    nome: draft.nome,
    categoria: draft.categoria,
    saldo_atual: draft.saldo_atual,
    taxa_juros_aa: draft.taxa_juros_aa ?? undefined,
    vencimento: draft.vencimento || undefined,
    observacoes: draft.observacoes || undefined,
  };

  return [placeholder, ...passivos.value];
});

const getDraftCategoria = (id: string, fallback: string): CategoriaChave => {
  if (drafts[id]) {
    return drafts[id].categoria;
  }
  return (fallback in categoriaConfig ? (fallback as CategoriaChave) : 'outros');
};

const isNew = (id: string) => newCardId.value === id;
const isEditing = (id?: string | null) => !!id && editingId.value === id;
const isSaving = (id: string) => savingId.value === id;
const isRemovendo = (id: string) => isRemovendoId.value === id;

const ensureExpanded = (id: string) => {
  if (!id) {
    return;
  }
  const next = new Set(expandedPassivos.value);
  next.add(id);
  expandedPassivos.value = next;
};

const toInputDate = (valor?: string | null) => {
  if (!valor) {
    return '';
  }
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) {
    return valor.slice(0, 10);
  }
  return data.toISOString().slice(0, 10);
};

const createDraftFromPassivo = (item: Passivo): PassivoDraft => ({
  nome: item.nome ?? '',
  categoria: getDraftCategoria(item.id ?? '', item.categoria ?? 'outros'),
  saldo_atual: Number(item.saldo_atual ?? 0),
  taxa_juros_aa: item.taxa_juros_aa ?? null,
  vencimento: toInputDate(item.vencimento ?? null),
  observacoes: item.observacoes ?? '',
});

const displayNome = (item: Passivo) => {
  const id = item.id ?? '';
  if (isEditing(id) && drafts[id]) {
    return drafts[id].nome.trim() || 'Novo passivo';
  }
  return item.nome;
};

const displaySaldo = (item: Passivo) => {
  const id = item.id ?? '';
  const valor = isEditing(id) && drafts[id] ? drafts[id].saldo_atual : item.saldo_atual ?? 0;
  return formatCurrency(Number(valor ?? 0));
};

const displayCategoriaKey = (item: Passivo): CategoriaChave => {
  const id = item.id ?? '';
  if (isEditing(id) && drafts[id]) {
    return drafts[id].categoria;
  }
  const categoria = item.categoria ?? 'outros';
  return (categoria in categoriaConfig ? (categoria as CategoriaChave) : 'outros');
};

const displayCategoriaLabel = (item: Passivo) => categoriaConfig[displayCategoriaKey(item)].label;

const displayTaxa = (item: Passivo) => {
  const id = item.id ?? '';
  const valor = isEditing(id) && drafts[id] ? drafts[id].taxa_juros_aa : item.taxa_juros_aa;
  if (valor === null || valor === undefined || Number.isNaN(valor)) {
    return null;
  }
  return `${valor}% a.a.`;
};

const displayVencimento = (item: Passivo) => {
  const id = item.id ?? '';
  const valor = isEditing(id) && drafts[id] ? drafts[id].vencimento : item.vencimento;
  if (!valor) {
    return null;
  }
  return formatDate(valor);
};

const displayObservacoes = (item: Passivo) => {
  const id = item.id ?? '';
  const valor = isEditing(id) && drafts[id] ? drafts[id].observacoes : item.observacoes;
  return valor?.trim() ? valor.trim() : null;
};

const carregar = async () => {
  isCarregando.value = true;
  try {
    await portfolioStore.fetchPassivos();
    listaErro.value = '';
  } catch (err) {
    listaErro.value = 'Nao foi possivel carregar os passivos.';
  } finally {
    isCarregando.value = false;
  }
};

const criarNovoPassivo = () => {
  if (newCardId.value) {
    editingId.value = newCardId.value;
    ensureExpanded(newCardId.value);
    return;
  }

  if (editingId.value && !isNew(editingId.value)) {
    cancelar(editingId.value);
  }

  const id = `novo-${Date.now()}`;
  newCardId.value = id;
  drafts[id] = {
    nome: '',
    categoria: 'outros',
    saldo_atual: 0,
    taxa_juros_aa: null,
    vencimento: '',
    observacoes: '',
  };
  erros[id] = '';
  editingId.value = id;
  ensureExpanded(id);
};

const iniciarEdicao = (item: Passivo) => {
  if (!item.id) {
    return;
  }

  if (editingId.value && editingId.value !== item.id) {
    cancelar(editingId.value);
  }

  drafts[item.id] = createDraftFromPassivo(item);
  erros[item.id] = '';
  editingId.value = item.id;
  ensureExpanded(item.id);
};

const cancelar = (id: string) => {
  delete drafts[id];
  delete erros[id];

  if (isNew(id)) {
    newCardId.value = null;
    const next = new Set(expandedPassivos.value);
    next.delete(id);
    expandedPassivos.value = next;
  }

  if (editingId.value === id) {
    editingId.value = null;
  }
};

const buildPayload = (draft: PassivoDraft): PassivoInput => ({
  nome: draft.nome.trim(),
  categoria: draft.categoria,
  saldo_atual: Number(draft.saldo_atual ?? 0),
  taxa_juros_aa: typeof draft.taxa_juros_aa === 'number' ? draft.taxa_juros_aa : undefined,
  vencimento: draft.vencimento || undefined,
  observacoes: draft.observacoes?.trim() ? draft.observacoes.trim() : undefined,
});

const salvarEdicao = async (id: string) => {
  const draft = drafts[id];
  if (!draft) {
    return;
  }

  if (!draft.nome.trim()) {
    erros[id] = 'Informe o nome do passivo.';
    return;
  }

  erros[id] = '';
  savingId.value = id;

  try {
    const payload = buildPayload(draft);

    if (isNew(id)) {
      const created = await portfolioStore.createPassivo(payload);
      const novoId = created?.id;
      cancelar(id);
      newCardId.value = null;
      if (novoId) {
        ensureExpanded(novoId);
      }
    } else {
      await portfolioStore.updatePassivo(id, payload);
      cancelar(id);
      ensureExpanded(id);
    }
  } catch (err) {
    erros[id] = isNew(id) ? 'Nao foi possivel salvar o passivo.' : 'Nao foi possivel atualizar o passivo.';
  } finally {
    savingId.value = null;
  }
};

const remover = async (id: string) => {
  if (isNew(id)) {
    cancelar(id);
    return;
  }

  if (typeof window !== 'undefined') {
    const confirmado = window.confirm('Tem certeza que deseja remover este passivo?');
    if (!confirmado) {
      return;
    }
  }

  isRemovendoId.value = id;
  try {
    await portfolioStore.deletePassivo(id);
    const next = new Set(expandedPassivos.value);
    next.delete(id);
    expandedPassivos.value = next;
    if (editingId.value === id) {
      editingId.value = null;
    }
  } catch (err) {
    erros[id] = 'Nao foi possivel remover o passivo.';
  } finally {
    isRemovendoId.value = null;
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

const toggleExpand = (id: string) => {
  if (!id) {
    return;
  }
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

const getCategoriaAccent = (categoria: string) => {
  const chave = (categoria in categoriaConfig ? categoria : 'outros') as CategoriaChave;
  return categoriaConfig[chave].accent;
};

const formatCurrency = (valor: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor ?? 0);

const formatDate = (valor: string) => {
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) {
    return valor;
  }
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' }).format(data);
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

.lista-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.lista-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.lista-header__info {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.lista-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
}

.add-passivo-button {
  border-radius: 0.85rem;
  border: 1px solid #dbeafe;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: #ffffff;
  font-weight: 600;
  padding: 0.65rem 1.5rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.add-passivo-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.add-passivo-button:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.2);
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

.passivo-card--editing {
  border-color: #bfdbfe;
  box-shadow: 0 12px 32px rgba(37, 99, 235, 0.18);
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

.passivo-card__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
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

.passivo-card__toggle:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.passivo-card__edit,
.passivo-card__save,
.passivo-card__cancel,
.passivo-card__delete {
  border-radius: 0.75rem;
  padding: 0.35rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.passivo-card__edit {
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #1e293b;
}

.passivo-card__edit:hover {
  background: #e2e8f0;
}

.passivo-card__save {
  border: 1px solid #2563eb;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: #ffffff;
}

.passivo-card__save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.passivo-card__cancel {
  border: 1px solid #cbd5f5;
  background: #ffffff;
  color: #1d4ed8;
}

.passivo-card__cancel:hover {
  background: #eff6ff;
  border-color: #93c5fd;
}

.passivo-card__cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.passivo-card__delete {
  border: 1px solid #fee2e2;
  background: #fee2e2;
  color: #b91c1c;
}

.passivo-card__delete:hover {
  background: #fecaca;
  border-color: #fca5a5;
}

.passivo-card__delete:disabled {
  opacity: 0.55;
  cursor: not-allowed;
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

.passivo-card__edit-grid {
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

.field--span-full {
  grid-column: 1 / -1;
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

.passivo-card__erro {
  margin: 0;
  color: #dc2626;
  font-weight: 600;
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

.erro--inline {
  margin: 0;
  font-size: 0.85rem;
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

  .add-passivo-button {
    width: 100%;
  }
}
</style>
