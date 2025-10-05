<template>
  <section class="passivos-page renda-fixa-page">
    <header class="page-header">
      <div class="page-title">
        <p class="page-breadcrumb">Renda fixa</p>
        <h1>Renda Fixa</h1>
        <p class="page-description">
          Administre CDBs, titulos publicos e debentures com a mesma experiencia das demais secoes.
        </p>
      </div>
      <button class="ghost-button" type="button" @click="carregar" :disabled="isCarregando">
        <ArrowPathIcon class="icon" aria-hidden="true" />
        <span>{{ isCarregando ? 'Atualizando...' : 'Atualizar lista' }}</span>
      </button>
    </header>

    <ul v-if="insights.length" class="insights-grid">
      <li v-for="item in insights" :key="item.label" class="insight-card">
        <component :is="item.icon" class="insight-card__icon" aria-hidden="true" />
        <div>
          <p class="insight-card__label">{{ item.label }}</p>
          <p class="insight-card__value">{{ item.value }}</p>
          <p v-if="item.helper" class="insight-card__helper">{{ item.helper }}</p>
        </div>
      </li>
    </ul>

    <section class="lista-wrapper">
      <header class="lista-header">
        <div class="lista-header__info">
          <h2 class="section-title">Posicoes cadastradas</h2>
          <p class="lista-subtitle">Detalhe cada alocacao, rentabilidade e vencimento em um unico lugar.</p>
          <p v-if="listaErro" class="erro erro--inline">{{ listaErro }}</p>
        </div>
        <button
          class="add-passivo-button"
          type="button"
          @click="criarNovaPosicao"
          :disabled="!!newCardId || isCarregando"
        >
          {{ newCardId ? 'Posicao em criacao' : 'Nova posicao' }}
        </button>
      </header>

      <ul v-if="cards.length" class="passivos-lista">
        <li
          v-for="item in cards"
          :key="item.id"
          :class="['passivo-card', { 'passivo-card--editing': isEditing(item.id) }]"
        >
          <div class="passivo-card__icon renda-fixa-card__icon" aria-hidden="true">
            <BanknotesIcon />
          </div>
          <div class="passivo-card__body">
            <div class="passivo-card__header">
              <div class="passivo-card__heading">
                <h3>{{ displayAtivo(item) }}</h3>
                <span class="passivo-card__saldo">{{ displayValor(item) }}</span>
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
                    @click="salvar(item.id)"
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
              <span>{{ displayTipo(item) }}</span>
              <span class="divider">Indexador {{ displayIndexador(item) }}</span>
              <span v-if="displayRentabilidade(item)" class="divider">{{ displayRentabilidade(item) }}</span>
            </p>
            <transition name="passivo-details">
              <div v-if="isExpanded(item.id)" class="passivo-card__details">
                <template v-if="isEditing(item.id)">
                  <div class="passivo-card__edit-grid">
                    <label class="field">
                      <span>Ativo</span>
                      <input v-model="drafts[item.id].ativo" placeholder="Tesouro Selic 2029" />
                    </label>
                    <label class="field">
                      <span>Tipo</span>
                      <select v-model="drafts[item.id].tipo">
                        <option v-for="option in tipoOptions" :key="option.value" :value="option.value">
                          {{ option.label }}
                        </option>
                      </select>
                    </label>
                    <label class="field">
                      <span>Indexador</span>
                      <select v-model="drafts[item.id].indexador">
                        <option v-for="option in indexadorOptions" :key="option.value" :value="option.value">
                          {{ option.label }}
                        </option>
                      </select>
                    </label>
                    <label class="field">
                      <span>Rentabilidade (% a.a.)</span>
                      <input
                        v-model.number="drafts[item.id].rentabilidade_aa"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="12.5"
                      />
                    </label>
                    <label class="field">
                      <span>Valor aplicado</span>
                      <input
                        v-model.number="drafts[item.id].valor"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="1000.00"
                      />
                    </label>
                    <label class="field">
                      <span>Distribuidor</span>
                      <input v-model="drafts[item.id].distribuidor" placeholder="Corretora XP" />
                    </label>
                    <label class="field">
                      <span>Moeda</span>
                      <select v-model="drafts[item.id].moeda">
                        <option v-for="option in moedaOptions" :key="option.value" :value="option.value">
                          {{ option.label }}
                        </option>
                      </select>
                    </label>
                    <label class="field">
                      <span>Data de compra</span>
                      <input v-model="drafts[item.id].data_inicio" type="date" />
                    </label>
                    <label class="field">
                      <span>Vencimento</span>
                      <input v-model="drafts[item.id].vencimento" type="date" />
                    </label>
                  </div>
                  <p v-if="erros[item.id]" class="erro passivo-card__erro">{{ erros[item.id] }}</p>
                </template>
                <template v-else>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Distribuidor</span>
                    <span class="passivo-card__detail-value">{{ displayDistribuidor(item) }}</span>
                  </div>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Data de compra</span>
                    <span class="passivo-card__detail-value">{{ displayDataInicio(item) }}</span>
                  </div>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Vencimento</span>
                    <span class="passivo-card__detail-value">{{ displayVencimento(item) }}</span>
                  </div>
                </template>
              </div>
            </transition>
          </div>
        </li>
      </ul>

      <div v-else class="empty-state" role="status">
        <FaceFrownIcon class="empty-state__icon" aria-hidden="true" />
        <p>Nenhuma posicao cadastrada ainda.</p>
        <p class="empty-state__helper">Registre uma aplicacao para acompanhar rentabilidade e vencimentos.</p>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { ArrowPathIcon, BanknotesIcon, FaceFrownIcon, CalendarDaysIcon } from '@heroicons/vue/24/outline';
import { usePortfolioStore } from '../store';
import { formatCurrency, formatDate, formatNumber } from '../utils/format';
import type {
  RendaFixaIndexadorValue,
  RendaFixaPosition,
  RendaFixaPositionInput,
  RendaFixaTipoValue,
} from '../types/rendaFixa';

type RendaFixaDraft = {
  ativo: string;
  tipo: RendaFixaTipoValue;
  indexador: RendaFixaIndexadorValue;
  rentabilidade_aa: number;
  distribuidor: string;
  valor: number;
  data_inicio: string;
  vencimento: string;
  moeda: string;
};

const tipoOptions: Array<{ value: RendaFixaTipoValue; label: string }> = [
  { value: 'tesouro_selic', label: 'Tesouro Selic' },
  { value: 'tesouro_ipca', label: 'Tesouro IPCA+' },
  { value: 'tesouro_prefixado', label: 'Tesouro Prefixado' },
  { value: 'cdb', label: 'CDB' },
  { value: 'lci', label: 'LCI' },
  { value: 'lca', label: 'LCA' },
  { value: 'debenture', label: 'Debenture' },
  { value: 'outros', label: 'Outros' },
];

const indexadorOptions: Array<{ value: RendaFixaIndexadorValue; label: string }> = [
  { value: 'pre', label: 'Pre-fixado' },
  { value: 'pos_cdi', label: 'Pos CDI' },
  { value: 'pos_ipca', label: 'Pos IPCA' },
  { value: 'pos_selic', label: 'Pos Selic' },
  { value: 'outros', label: 'Outros' },
];

const moedaOptions = [
  { value: 'brl', label: 'Real (BRL)' },
  { value: 'usd', label: 'Dolar (USD)' },
];

const portfolioStore = usePortfolioStore();
const { rendaFixa } = storeToRefs(portfolioStore);

const drafts = reactive<Record<string, RendaFixaDraft>>({});
const erros = reactive<Record<string, string>>({});
const expandedCards = ref<Set<string>>(new Set());
const editingId = ref<string | null>(null);
const savingId = ref<string | null>(null);
const removingId = ref<string | null>(null);
const newCardId = ref<string | null>(null);
const isCarregando = ref(false);
const listaErro = ref('');

const cards = computed<RendaFixaPosition[]>(() => {
  if (!newCardId.value) {
    return rendaFixa.value;
  }

  const draft = drafts[newCardId.value];
  if (!draft) {
    return rendaFixa.value;
  }

  const placeholder: RendaFixaPosition = {
    id: newCardId.value,
    ativo: draft.ativo,
    tipo: draft.tipo,
    indexador: draft.indexador,
    rentabilidade_aa: draft.rentabilidade_aa,
    distribuidor: draft.distribuidor || null,
    valor: draft.valor,
    data_inicio: draft.data_inicio,
    vencimento: draft.vencimento,
    moeda: draft.moeda,
  };

  return [placeholder, ...rendaFixa.value];
});

const isNew = (id: string | null | undefined) => id != null && id === newCardId.value;
const isEditing = (id: string | null | undefined) => !!id && editingId.value === id;
const isSaving = (id: string | null | undefined) => !!id && savingId.value === id;
const isRemovendo = (id: string | null | undefined) => !!id && removingId.value === id;
const isExpanded = (id: string | null | undefined) => !!id && expandedCards.value.has(id);

const ensureExpanded = (id: string | null | undefined) => {
  if (!id) {
    return;
  }
  const next = new Set(expandedCards.value);
  next.add(id);
  expandedCards.value = next;
};

const collapse = (id: string | null | undefined) => {
  if (!id) {
    return;
  }
  const next = new Set(expandedCards.value);
  next.delete(id);
  expandedCards.value = next;
};

const toInputDate = (value: string) => {
  if (!value) {
    return '';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value.slice(0, 10);
  }
  return date.toISOString().slice(0, 10);
};

const fromInputDate = (value: string) => {
  if (!value) {
    return new Date().toISOString();
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return `${value}T00:00:00Z`;
  }
  return date.toISOString();
};

const createDraft = (item: RendaFixaPosition): RendaFixaDraft => ({
  ativo: item.ativo ?? '',
  tipo: (item.tipo ?? 'outros') as RendaFixaTipoValue,
  indexador: (item.indexador ?? 'outros') as RendaFixaIndexadorValue,
  rentabilidade_aa: Number(item.rentabilidade_aa ?? 0),
  distribuidor: item.distribuidor ?? '',
  valor: Number(item.valor ?? 0),
  data_inicio: toInputDate(item.data_inicio ?? ''),
  vencimento: toInputDate(item.vencimento ?? ''),
  moeda: (item.moeda ?? 'brl').toLowerCase(),
});

const displayAtivo = (item: RendaFixaPosition) => {
  const id = item.id ?? '';
  if (isEditing(id) && drafts[id]) {
    return drafts[id].ativo.trim() || 'Novo titulo';
  }
  return item.ativo ?? 'Sem identificacao';
};

const displayValor = (item: RendaFixaPosition) => {
  const id = item.id ?? '';
  const moeda = (isEditing(id) && drafts[id] ? drafts[id].moeda : item.moeda) ?? 'brl';
  const valor = isEditing(id) && drafts[id] ? drafts[id].valor : item.valor ?? 0;
  return formatCurrency(valor ?? 0, moeda.toUpperCase());
};

const displayTipo = (item: RendaFixaPosition) => {
  const id = item.id ?? '';
  const value = (isEditing(id) && drafts[id] ? drafts[id].tipo : item.tipo) ?? 'outros';
  return tipoOptions.find((option) => option.value === value)?.label ?? 'Outro';
};

const displayIndexador = (item: RendaFixaPosition) => {
  const id = item.id ?? '';
  const value = (isEditing(id) && drafts[id] ? drafts[id].indexador : item.indexador) ?? 'outros';
  return indexadorOptions.find((option) => option.value === value)?.label ?? 'Outro';
};

const displayRentabilidade = (item: RendaFixaPosition) => {
  const id = item.id ?? '';
  const value = isEditing(id) && drafts[id] ? drafts[id].rentabilidade_aa : item.rentabilidade_aa;
  if (value === undefined || value === null) {
    return null;
  }
  return `${formatNumber(value, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}% a.a.`;
};

const displayDistribuidor = (item: RendaFixaPosition) => {
  const value = item.distribuidor ?? '';
  return value.trim() || '';
};

const displayDataInicio = (item: RendaFixaPosition) => formatDate(item.data_inicio);
const displayVencimento = (item: RendaFixaPosition) => formatDate(item.vencimento);

const toggleExpand = (id: string | null | undefined) => {
  if (!id) {
    return;
  }
  if (isExpanded(id)) {
    collapse(id);
  } else {
    ensureExpanded(id);
  }
};

const carregar = async () => {
  isCarregando.value = true;
  try {
    await portfolioStore.fetchRendaFixa();
    listaErro.value = '';
  } catch (error) {
    listaErro.value = 'Nao foi possivel carregar as posicoes. Tente novamente mais tarde.';
  } finally {
    isCarregando.value = false;
  }
};

const criarNovaPosicao = () => {
  if (newCardId.value) {
    editingId.value = newCardId.value;
    ensureExpanded(newCardId.value);
    return;
  }

  if (editingId.value && !isNew(editingId.value)) {
    cancelar(editingId.value);
  }

  const id = `nova-posicao-${Date.now()}`;
  newCardId.value = id;
  drafts[id] = {
    ativo: '',
    tipo: 'tesouro_selic',
    indexador: 'pos_selic',
    rentabilidade_aa: 0,
    distribuidor: '',
    valor: 0,
    data_inicio: new Date().toISOString().slice(0, 10),
    vencimento: new Date().toISOString().slice(0, 10),
    moeda: 'brl',
  };
  erros[id] = '';
  editingId.value = id;
  ensureExpanded(id);
};

const iniciarEdicao = (item: RendaFixaPosition) => {
  if (!item.id) {
    return;
  }

  if (editingId.value && editingId.value !== item.id) {
    cancelar(editingId.value);
  }

  drafts[item.id] = createDraft(item);
  erros[item.id] = '';
  editingId.value = item.id;
  ensureExpanded(item.id);
};

const cancelar = (id: string) => {
  delete drafts[id];
  delete erros[id];

  if (isNew(id)) {
    newCardId.value = null;
    collapse(id);
  }

  if (editingId.value === id) {
    editingId.value = null;
  }
};

const buildPayload = (draft: RendaFixaDraft): RendaFixaPositionInput => ({
  ativo: draft.ativo.trim(),
  tipo: draft.tipo,
  indexador: draft.indexador,
  rentabilidade_aa: Number(draft.rentabilidade_aa ?? 0),
  distribuidor: draft.distribuidor?.trim() ? draft.distribuidor.trim() : null,
  valor: Number(draft.valor ?? 0),
  data_inicio: fromInputDate(draft.data_inicio),
  vencimento: fromInputDate(draft.vencimento),
  moeda: draft.moeda.trim().toLowerCase() || 'brl',
});

const validarDraft = (draft: RendaFixaDraft): string | null => {
  if (!draft.ativo.trim()) {
    return 'Informe o nome do ativo.';
  }
  if (!draft.data_inicio) {
    return 'Informe a data de compra.';
  }
  if (!draft.vencimento) {
    return 'Informe o vencimento do titulo.';
  }
  if (draft.valor <= 0) {
    return 'Valor aplicado deve ser maior que zero.';
  }
  return null;
};

const salvar = async (id: string | null | undefined) => {
  if (!id) {
    return;
  }
  const draft = drafts[id];
  if (!draft) {
    return;
  }

  const erro = validarDraft(draft);
  if (erro) {
    erros[id] = erro;
    return;
  }

  erros[id] = '';
  savingId.value = id;

  const payload = buildPayload(draft);

  try {
    if (isNew(id)) {
      await portfolioStore.createRendaFixaPosition(payload);
      cancelar(id);
    } else {
      await portfolioStore.updateRendaFixaPosition(id, payload);
      cancelar(id);
      ensureExpanded(id);
    }
  } catch (error) {
    erros[id] = 'Nao foi possivel salvar a posicao agora.';
  } finally {
    savingId.value = null;
  }
};

const remover = async (id: string | null | undefined) => {
  if (!id) {
    return;
  }

  if (isNew(id)) {
    cancelar(id);
    return;
  }

  if (typeof window !== 'undefined') {
    const confirmado = window.confirm('Tem certeza que deseja remover esta posicao?');
    if (!confirmado) {
      return;
    }
  }

  removingId.value = id;
  try {
    await portfolioStore.deleteRendaFixaPosition(id);
    collapse(id);
    if (editingId.value === id) {
      editingId.value = null;
    }
  } catch (error) {
    erros[id] = 'Nao foi possivel remover a posicao.';
  } finally {
    removingId.value = null;
  }
};

const totalAplicado = computed(() => rendaFixa.value.reduce((acc, item) => acc + (item.valor ?? 0), 0));

const rentabilidadeMedia = computed(() => {
  if (!rendaFixa.value.length) {
    return 0;
  }
  const soma = rendaFixa.value.reduce((acc, item) => acc + (item.rentabilidade_aa ?? 0), 0);
  return soma / rendaFixa.value.length;
});

const proximoVencimento = computed(() => {
  if (!rendaFixa.value.length) {
    return null;
  }
  const dates = rendaFixa.value
    .map((item) => new Date(item.vencimento))
    .filter((date) => !Number.isNaN(date.getTime()));
  if (!dates.length) {
    return null;
  }
  const min = dates.sort((a, b) => a.getTime() - b.getTime())[0];
  return formatDate(min.toISOString());
});

const insights = computed(() => {
  if (!rendaFixa.value.length) {
    return [] as Array<{ label: string; value: string; helper?: string; icon: unknown }>;
  }

  return [
    {
      label: 'Total investido',
      value: formatCurrency(totalAplicado.value, 'BRL'),
      helper: `${rendaFixa.value.length} posicao(oes)` ,
      icon: BanknotesIcon,
    },
    {
      label: 'Rentabilidade media',
      value: `${formatNumber(rentabilidadeMedia.value, { minimumFractionDigits: 2 })}% a.a.`,
      helper: 'Considera apenas o valor informado nos cadastros',
      icon: ArrowPathIcon,
    },
    {
      label: 'Proximo vencimento',
      value: proximoVencimento.value ?? '',
      helper: proximoVencimento.value ? 'Prepare o reinvestimento com antecedencia.' : 'Cadastre novas posicoes.',
      icon: CalendarDaysIcon,
    },
  ];
});

onMounted(carregar);
</script>

<style src="../assets/portfolio.css"></style>
