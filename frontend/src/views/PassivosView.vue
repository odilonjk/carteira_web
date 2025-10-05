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
import { formatCurrency, formatDate } from '../utils/format';

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

onMounted(carregar);
</script>

<style src="../assets/portfolio.css"></style>

