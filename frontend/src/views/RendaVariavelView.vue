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
                  <div class="detail-summary-row">
                    <div
                      v-for="summary in buildSummaryEntries(item)"
                      :key="summary.label"
                      class="detail-summary-item"
                    >
                      <span class="detail-summary-item__label">{{ summary.label }}</span>
                      <span class="detail-summary-item__value">{{ summary.value }}</span>
                    </div>
                  </div>

                  <section class="transactions-block">
                    <header class="transactions-header">
                      <h3>Transacoes</h3>
                      <button
                        v-if="canCreateTransaction(item) && creatingTransactionFor !== item.id"
                        class="transactions-header__button"
                        type="button"
                        @click="abrirFormularioTransacao(item)"
                      >
                        Nova transacao
                      </button>
                    </header>

                    <p v-if="tradesErrors[item.id ?? '']" class="erro transactions-error">
                      {{ tradesErrors[item.id ?? ''] }}
                    </p>

                    <form
                      v-if="creatingTransactionFor === item.id && item.id"
                      class="transaction-form"
                      @submit.prevent="salvarTransacao(item.id!)"
                    >
                      <div class="transaction-form__grid">
                        <label class="field">
                          <span>Tipo</span>
                          <select v-model="transactionDrafts[item.id!].tipo_operacao">
                            <option value="compra">Compra</option>
                            <option value="venda">Venda</option>
                          </select>
                        </label>
                        <label class="field">
                          <span>Data</span>
                          <input v-model="transactionDrafts[item.id!].data" type="datetime-local" />
                        </label>
                        <label class="field">
                          <span>Quantidade</span>
                          <input
                            v-model.number="transactionDrafts[item.id!].quantidade"
                            type="number"
                            min="0"
                            step="0.01"
                          />
                        </label>
                        <label class="field">
                          <span>Cotacao</span>
                          <input
                            v-model.number="transactionDrafts[item.id!].cotacao"
                            type="number"
                            min="0"
                            step="0.01"
                          />
                        </label>
                      </div>
                      <p v-if="transactionErrors[item.id!]" class="erro transactions-error">
                        {{ transactionErrors[item.id!] }}
                      </p>
                      <div class="transaction-form__actions">
                        <button
                          class="passivo-card__save"
                          type="submit"
                          :disabled="transactionSavingId === item.id"
                        >
                          {{ transactionSavingId === item.id ? 'Salvando...' : 'Salvar transacao' }}
                        </button>
                        <button
                          class="passivo-card__cancel"
                          type="button"
                          @click="cancelarTransacao(item.id!)"
                          :disabled="transactionSavingId === item.id"
                        >
                          Cancelar
                        </button>
                      </div>
                    </form>

                    <div v-else-if="tradesLoading[item.id ?? '']" class="transactions-loading">
                      Carregando transacoes...
                    </div>

                    <table
                      v-else-if="tradesForPosition(item.id).length"
                      class="transactions-table"
                    >
                      <thead>
                        <tr>
                          <th scope="col">Data</th>
                          <th scope="col">Tipo</th>
                          <th scope="col">Quantidade</th>
                          <th scope="col">Cotacao</th>
                          <th scope="col">Total</th>
                          <th scope="col">Resultado</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="trade in tradesForPosition(item.id)" :key="trade.id ?? trade.data">
                          <td>{{ formatDateTime(trade.data) }}</td>
                          <td>{{ displayTradeTipo(trade.tipo_operacao) }}</td>
                          <td>{{ formatNumber(trade.quantidade) }}</td>
                          <td>{{ formatCurrency(trade.cotacao, displayTradeCurrency()) }}</td>
                          <td>{{ formatCurrency(trade.total, displayTradeCurrency()) }}</td>
                          <td>
                            {{
                              trade.resultado_monetario !== null
                                ? formatCurrency(trade.resultado_monetario, displayTradeCurrency())
                                : '—'
                            }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <p v-else class="transactions-empty">Nenhuma transacao registrada ainda.</p>
                  </section>
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
import { formatCurrency, formatPercent, formatNumber, formatDate, formatDateTime } from '../utils/format';
import type {
  RendaVariavelCategory,
  RendaVariavelPosition,
  RendaVariavelPositionInput,
  RendaVariavelTipoValue,
  RendaVariavelTrade,
  RendaVariavelTradeInput,
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
const { rendaVariavel, rendaVariavelTrades } = storeToRefs(portfolioStore);

const drafts = reactive<Record<string, RendaVariavelDraft>>({});
const erros = reactive<Record<string, string>>({});
const tradesLoading = reactive<Record<string, boolean>>({});
const tradesErrors = reactive<Record<string, string>>({});
type TransactionDraft = {
  tipo_operacao: RendaVariavelTradeInput['tipo_operacao'];
  data: string;
  quantidade: number;
  cotacao: number;
};
const transactionDrafts = reactive<Record<string, TransactionDraft>>({});
const transactionErrors = reactive<Record<string, string>>({});
const creatingTransactionFor = ref<string | null>(null);
const transactionSavingId = ref<string | null>(null);
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
  if (!isNew(id)) {
    void loadTradesForPosition(id);
  }
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

const tradesForPosition = (id: string | null | undefined): RendaVariavelTrade[] => {
  if (!id) {
    return [];
  }
  return rendaVariavelTrades.value[id] ?? [];
};

const loadTradesForPosition = async (id: string | null | undefined) => {
  if (!id) {
    return;
  }

  if (tradesLoading[id] || rendaVariavelTrades.value[id]) {
    return;
  }

  tradesLoading[id] = true;
  tradesErrors[id] = '';
  try {
    await portfolioStore.fetchRendaVariavelTrades(props.category, id);
  } catch (error) {
    tradesErrors[id] = 'Nao foi possivel carregar as transacoes.';
  } finally {
    tradesLoading[id] = false;
  }
};

const buildSummaryEntries = (item: RendaVariavelPosition) => [
  { label: 'Valor investido', value: displayValorInvestido(item) },
  { label: 'Resultado', value: displayResultado(item) },
  { label: 'Performance', value: displayPerformance(item) },
  { label: 'Atualizado em', value: displayAtualizado(item) },
];

const canCreateTransaction = (item: RendaVariavelPosition) =>
  !!item.id && !isNew(item.id) && !isEditing(item.id);

const defaultTransactionDraft = (item: RendaVariavelPosition): TransactionDraft => ({
  tipo_operacao: 'compra',
  data: new Date().toISOString().slice(0, 16),
  quantidade: 0,
  cotacao: Number(item.cotacao_atual ?? 0),
});

const abrirFormularioTransacao = (item: RendaVariavelPosition) => {
  if (!item.id) {
    return;
  }
  void loadTradesForPosition(item.id);
  if (!transactionDrafts[item.id]) {
    transactionDrafts[item.id] = defaultTransactionDraft(item);
  }
  transactionErrors[item.id] = '';
  creatingTransactionFor.value = item.id;
};

const cancelarTransacao = (id: string) => {
  delete transactionDrafts[id];
  delete transactionErrors[id];
  creatingTransactionFor.value = null;
  transactionSavingId.value = null;
};

const validarTransacaoDraft = (
  position: RendaVariavelPosition,
  draft: TransactionDraft,
) => {
  if (draft.quantidade <= 0) {
    return 'Informe uma quantidade maior que zero.';
  }
  if (draft.cotacao <= 0) {
    return 'Informe a cotacao da transacao.';
  }
  if (draft.tipo_operacao === 'venda' && draft.quantidade > (position.quantidade ?? 0)) {
    return 'Quantidade vendida maior que a quantidade em carteira.';
  }
  return null;
};

const salvarTransacao = async (id: string) => {
  const draft = transactionDrafts[id];
  const position = currentItems.value.find((item) => item.id === id);

  if (!draft || !position) {
    return;
  }

  const erro = validarTransacaoDraft(position, draft);
  if (erro) {
    transactionErrors[id] = erro;
    return;
  }

  transactionErrors[id] = '';
  transactionSavingId.value = id;

  const payload: RendaVariavelTradeInput = {
    tipo_operacao: draft.tipo_operacao,
    quantidade: Number(draft.quantidade),
    cotacao: Number(draft.cotacao),
    data: draft.data ? new Date(draft.data).toISOString() : undefined,
  };

  try {
    await portfolioStore.createRendaVariavelTrade(props.category, id, payload);
    cancelarTransacao(id);
    ensureExpanded(id);
  } catch (error) {
    const message =
      (error as { response?: { data?: { error?: string } } }).response?.data?.error ??
      'Nao foi possivel registrar a transacao.';
    transactionErrors[id] = message;
  } finally {
    transactionSavingId.value = null;
  }
};

const displayTradeTipo = (tipo: RendaVariavelTrade['tipo_operacao']) =>
  tipo === 'compra' ? 'Compra' : 'Venda';

const displayTradeCurrency = () => (currency.value === 'USD' ? 'USD' : 'BRL');

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
  if (draft.quantidade < 0) {
    return 'Quantidade nao pode ser negativa.';
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
    creatingTransactionFor.value = null;
    transactionSavingId.value = null;
    Object.keys(transactionDrafts).forEach((key) => delete transactionDrafts[key]);
    Object.keys(transactionErrors).forEach((key) => delete transactionErrors[key]);
    Object.keys(tradesErrors).forEach((key) => delete tradesErrors[key]);
    Object.keys(tradesLoading).forEach((key) => delete tradesLoading[key]);
    portfolioStore.rendaVariavelTrades = {};
    expandedCards.value = new Set();
    await carregar();
  },
);

onMounted(() => {
  void carregar();
});
</script>

<style src="../assets/portfolio.css"></style>
