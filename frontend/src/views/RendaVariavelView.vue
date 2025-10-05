<template>
  <section class="passivos-page renda-variavel-page">
    <header class="page-header">
      <div class="page-title">
        <p class="page-breadcrumb">Renda variavel · {{ pageTitle }}</p>
        <h1>{{ pageTitle }}</h1>
        <p class="page-description">{{ pageDescription }}</p>
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
          <p class="lista-subtitle">Controle quantidade, preco medio e peso da categoria na carteira.</p>
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
          <div class="passivo-card__icon renda-variavel-card__icon" aria-hidden="true">
            <ChartPieIcon />
          </div>
          <div class="passivo-card__body">
            <div class="passivo-card__header">
              <div class="passivo-card__heading">
                <h3>{{ displayTicker(item) }}</h3>
                <span class="passivo-card__saldo">{{ displayValorAtual(item) }}</span>
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
              <span>{{ categoryLabel }}</span>
              <span class="divider">{{ displayQuantidade(item) }}</span>
              <span class="divider">Peso {{ displayPeso(item) }}</span>
            </p>
            <transition name="passivo-details">
              <div v-if="isExpanded(item.id)" class="passivo-card__details">
                <template v-if="isEditing(item.id)">
                  <div class="passivo-card__edit-grid">
                    <label class="field">
                      <span>Ticker</span>
                      <input v-model="drafts[item.id].ticker" placeholder="ITUB4" />
                    </label>
                    <label class="field">
                      <span>Quantidade</span>
                      <input
                        v-model.number="drafts[item.id].quantidade"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="100"
                      />
                    </label>
                    <label class="field">
                      <span>Preco medio</span>
                      <input
                        v-model.number="drafts[item.id].preco_medio"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="28.50"
                      />
                    </label>
                    <label class="field">
                      <span>Ultima cotacao</span>
                      <input
                        v-model.number="drafts[item.id].cotacao_atual"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="30.10"
                      />
                    </label>
                    <label class="field">
                      <span>Peso desejado (%)</span>
                      <input
                        v-model.number="drafts[item.id].peso_desejado_percentual"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="18"
                      />
                    </label>
                  </div>
                  <p v-if="erros[item.id]" class="erro passivo-card__erro">{{ erros[item.id] }}</p>
                </template>
                <template v-else>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Valor investido</span>
                    <span class="passivo-card__detail-value">{{ displayValorInvestido(item) }}</span>
                  </div>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Resultado</span>
                    <span class="passivo-card__detail-value">{{ displayResultado(item) }}</span>
                  </div>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Performance</span>
                    <span class="passivo-card__detail-value">{{ displayPerformance(item) }}</span>
                  </div>
                  <div class="passivo-card__detail">
                    <span class="passivo-card__detail-label">Atualizado em</span>
                    <span class="passivo-card__detail-value">{{ displayAtualizado(item) }}</span>
                  </div>
                </template>
              </div>
            </transition>
          </div>
        </li>
      </ul>

      <div v-else class="empty-state" role="status">
        <FaceFrownIcon class="empty-state__icon" aria-hidden="true" />
        <p>Nenhuma posicao cadastrada para {{ pageTitle.toLowerCase() }}.</p>
        <p class="empty-state__helper">
          Cadastre novas posicoes para acompanhar evolucao, proventos e rebalanceamentos.
        </p>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { ArrowPathIcon, ChartPieIcon, FaceFrownIcon, BanknotesIcon } from '@heroicons/vue/24/outline';
import { usePortfolioStore } from '../store';
import { formatCurrency, formatPercent, formatNumber, formatDate } from '../utils/format';
import type {
  RendaVariavelCategory,
  RendaVariavelPosition,
  RendaVariavelPositionInput,
  RendaVariavelTipoValue,
} from '../types/rendaVariavel';

const CATEGORY_META: Record<
  RendaVariavelCategory,
  { title: string; description: string; currency: 'BRL' | 'USD' }
> = {
  acoes: {
    title: 'Acoes',
    description: 'Siga empresas listadas na B3 e ajuste a alocacao conforme a tese.',
    currency: 'BRL',
  },
  fiis: {
    title: 'FIIs',
    description: 'Compare dividendos e vacancia dos fundos imobiliarios da carteira.',
    currency: 'BRL',
  },
  stocks: {
    title: 'Stocks',
    description: 'Acompanhe exposicao internacional em empresas listadas nas bolsas dos EUA.',
    currency: 'USD',
  },
  reits: {
    title: 'REITs',
    description: 'Monitore fundos imobiliarios americanos e distribuicoes em dolar.',
    currency: 'USD',
  },
  etf: {
    title: 'ETF',
    description: 'Controle ETFs que replicam indices e ajudam na diversificacao.',
    currency: 'BRL',
  },
};

const CATEGORY_TIPO: Record<RendaVariavelCategory, RendaVariavelTipoValue> = {
  acoes: 'acao_br',
  fiis: 'fii',
  stocks: 'stock_us',
  reits: 'reit',
  etf: 'etf',
};

type RendaVariavelDraft = {
  ticker: string;
  quantidade: number;
  preco_medio: number;
  cotacao_atual: number;
  peso_desejado_percentual: number;
};

const props = defineProps<{ category: RendaVariavelCategory }>();

const portfolioStore = usePortfolioStore();
const { rendaVariavel } = storeToRefs(portfolioStore);

const drafts = reactive<Record<string, RendaVariavelDraft>>({});
const erros = reactive<Record<string, string>>({});
const expandedCards = ref<Set<string>>(new Set());
const editingId = ref<string | null>(null);
const savingId = ref<string | null>(null);
const removingId = ref<string | null>(null);
const newCardId = ref<string | null>(null);
const isCarregando = ref(false);
const listaErro = ref('');

const categoryDetails = computed(() => CATEGORY_META[props.category]);
const currency = computed(() => categoryDetails.value.currency);
const pageTitle = computed(() => categoryDetails.value.title);
const pageDescription = computed(() => categoryDetails.value.description);
const categoryLabel = computed(() => categoryDetails.value.title);

const currentItems = computed(() => rendaVariavel.value[props.category] ?? []);

const cards = computed<RendaVariavelPosition[]>(() => {
  if (!newCardId.value) {
    return currentItems.value;
  }
  const draft = drafts[newCardId.value];
  if (!draft) {
    return currentItems.value;
  }

  const totalCompra = draft.quantidade * draft.preco_medio;
  const totalMercado = draft.quantidade * draft.cotacao_atual;
  const resultadoMonetario = totalMercado - totalCompra;
  const performancePercentual = draft.preco_medio
    ? (draft.cotacao_atual / draft.preco_medio - 1) * 100
    : 0;
  const totalExistente = currentItems.value.reduce(
    (acc, item) => acc + (item.total_mercado ?? 0),
    0,
  );
  const totalCarteira = totalExistente + totalMercado;
  const pesoPercentual = totalCarteira > 0 ? (totalMercado / totalCarteira) * 100 : 0;

  const placeholder: RendaVariavelPosition = {
    id: newCardId.value,
    ticker: draft.ticker,
    tipo: CATEGORY_TIPO[props.category],
    quantidade: draft.quantidade,
    preco_medio: draft.preco_medio,
    cotacao_atual: draft.cotacao_atual,
    total_compra: totalCompra,
    total_mercado: totalMercado,
    resultado_monetario: resultadoMonetario,
    performance_percentual: performancePercentual,
    peso_percentual: pesoPercentual,
    peso_desejado_percentual: draft.peso_desejado_percentual,
    atualizado_em: new Date().toISOString(),
  };

  return [placeholder, ...currentItems.value];
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

const createDraft = (item: RendaVariavelPosition): RendaVariavelDraft => ({
  ticker: item.ticker ?? '',
  quantidade: Number(item.quantidade ?? 0),
  preco_medio: Number(item.preco_medio ?? 0),
  cotacao_atual: Number(item.cotacao_atual ?? 0),
  peso_desejado_percentual: Number(item.peso_desejado_percentual ?? 0),
});

const displayTicker = (item: RendaVariavelPosition) => {
  const id = item.id ?? '';
  if (isEditing(id) && drafts[id]) {
    return drafts[id].ticker.trim().toUpperCase() || 'Novo ticker';
  }
  return item.ticker ?? 'Sem ticker';
};

const displayQuantidade = (item: RendaVariavelPosition) => {
  const id = item.id ?? '';
  const value = isEditing(id) && drafts[id] ? drafts[id].quantidade : item.quantidade ?? 0;
  return `${formatNumber(value)} unidades`;
};

const calculateProjectedWeight = (id: string | null | undefined): number => {
  if (!id) {
    return 0;
  }

  const draft = drafts[id];
  if (!draft) {
    const existing = currentItems.value.find((item) => item.id === id);
    return existing?.peso_percentual ?? 0;
  }

  const draftMarketValue = draft.quantidade * draft.cotacao_atual;
  const totalOutros = currentItems.value.reduce((acc, item) => {
    if (item.id === id) {
      return acc;
    }
    return acc + (item.total_mercado ?? 0);
  }, 0);

  const totalCarteira = totalOutros + draftMarketValue;
  return totalCarteira > 0 ? (draftMarketValue / totalCarteira) * 100 : 0;
};

const getPesoAtual = (item: RendaVariavelPosition) => {
  const id = item.id ?? '';
  if (drafts[id]) {
    return calculateProjectedWeight(id);
  }
  return item.peso_percentual ?? 0;
};

const displayPeso = (item: RendaVariavelPosition) => formatPercent(getPesoAtual(item), 2);

const displayValorInvestido = (item: RendaVariavelPosition) =>
  formatCurrency(item.total_compra ?? 0, currency.value);

const displayValorAtual = (item: RendaVariavelPosition) =>
  formatCurrency(item.total_mercado ?? 0, currency.value);

const displayResultado = (item: RendaVariavelPosition) =>
  formatCurrency(item.resultado_monetario ?? 0, currency.value);

const displayPerformance = (item: RendaVariavelPosition) => formatPercent(item.performance_percentual ?? 0, 2);

const displayAtualizado = (item: RendaVariavelPosition) => formatDate(item.atualizado_em);

const carregar = async () => {
  isCarregando.value = true;
  try {
    await portfolioStore.fetchRendaVariavelByCategory(props.category);
    listaErro.value = '';
  } catch (error) {
    listaErro.value = 'Nao foi possivel carregar as posicoes.';
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

  const id = `nova-renda-variavel-${Date.now()}`;
  newCardId.value = id;
  drafts[id] = {
    ticker: '',
    quantidade: 0,
    preco_medio: 0,
    cotacao_atual: 0,
    peso_desejado_percentual: 0,
  };
  erros[id] = '';
  editingId.value = id;
  ensureExpanded(id);
};

const iniciarEdicao = (item: RendaVariavelPosition) => {
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

const validarDraft = (draft: RendaVariavelDraft) => {
  if (!draft.ticker.trim()) {
    return 'Informe o ticker do ativo.';
  }
  if (draft.quantidade <= 0) {
    return 'Quantidade deve ser maior que zero.';
  }
  if (draft.preco_medio < 0 || draft.cotacao_atual < 0) {
    return 'Valores monetarios nao podem ser negativos.';
  }
  return null;
};

const buildPayload = (draft: RendaVariavelDraft): RendaVariavelPositionInput => {
  const quantidade = Number(draft.quantidade ?? 0);
  const precoMedio = Number(draft.preco_medio ?? 0);
  const cotacaoAtual = Number(draft.cotacao_atual ?? 0);
  const totalCompra = quantidade * precoMedio;
  const totalMercado = quantidade * cotacaoAtual;
  const resultadoMonetario = totalMercado - totalCompra;
  const performancePercentual = precoMedio === 0 ? 0 : (cotacaoAtual / precoMedio - 1) * 100;

  return {
    ticker: draft.ticker.trim().toUpperCase(),
    quantidade,
    preco_medio: precoMedio,
    cotacao_atual: cotacaoAtual,
    total_compra: totalCompra,
    total_mercado: totalMercado,
    resultado_monetario: resultadoMonetario,
    performance_percentual: performancePercentual,
    peso_desejado_percentual: Number(draft.peso_desejado_percentual ?? 0),
    atualizado_em: new Date().toISOString(),
  };
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
      await portfolioStore.createRendaVariavelPosition(props.category, payload);
      cancelar(id);
    } else {
      await portfolioStore.updateRendaVariavelPosition(props.category, id, payload);
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
    await portfolioStore.deleteRendaVariavelPosition(props.category, id);
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

const totalInvestido = computed(() => currentItems.value.reduce((acc, item) => acc + (item.total_compra ?? 0), 0));
const totalValorAtual = computed(() => currentItems.value.reduce((acc, item) => acc + (item.total_mercado ?? 0), 0));
const totalResultado = computed(() => currentItems.value.reduce((acc, item) => acc + (item.resultado_monetario ?? 0), 0));

const insights = computed(() => {
  if (!currentItems.value.length) {
    return [] as Array<{ label: string; value: string; helper?: string; icon: unknown }>;
  }

  return [
    {
      label: 'Valor investido',
      value: formatCurrency(totalInvestido.value, currency.value),
      helper: `${currentItems.value.length} posicao(oes)`,
      icon: BanknotesIcon,
    },
    {
      label: 'Valor atual',
      value: formatCurrency(totalValorAtual.value, currency.value),
      helper: `Resultado ${formatCurrency(totalResultado.value, currency.value)}`,
      icon: ChartPieIcon,
    },
    {
      label: 'Peso somado',
      value: formatPercent(
        currentItems.value.reduce((acc, item) => acc + (item.peso_percentual ?? 0), 0),
        2,
      ),
      helper: 'Considera apenas os pesos informados',
      icon: ArrowPathIcon,
    },
  ];
});

watch(
  () => props.category,
  async () => {
    editingId.value = null;
    newCardId.value = null;
    Object.keys(drafts).forEach((key) => delete drafts[key]);
    Object.keys(erros).forEach((key) => delete erros[key]);
    expandedCards.value = new Set();
    await carregar();
  },
);

onMounted(() => {
  void carregar();
});
</script>

<style src="../assets/portfolio.css"></style>
