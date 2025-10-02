# Carteira Web

Este projeto serve para manter minha carteira organizada, tanto passivos como ativos.

# Requisitos basicos

- Aplicacao web utilizando:
    - Backend: Python + Flask
    - Frontend: Vue.js
    - Database: Firestore (Google Cloud) e alguma versao para docker para rodar local.
    - Outro: Docker + docker compose.
- Sempre utilizar o bom senso e as boas praticas de cada linguagem e de engenharia de software.
- O projeto vai rodar no Google Cloud. Isso eh importante de ser lembrado quando estruturar o projeto.

# Requisitos de negocio

- Vai precisar de uma tela inicial.
- Vai precisar de uma tela de passivos (alguns insights e a lista de passivos).
- Vai precisar de uma tela de renda variavel (alguns insights e a lista de ativos por tipos).
    - Tipos: FIIs, Acoes (acoes = acoes no brasil), Stocks (stocks = acoes nos EUA), ETFs, REITs, Fundos de Investimento, etc.
- Vai precisar de uma tela de renda fixa (alguns insights e a lista de ativos por tipos).
    - Tipos: CBD, Debentures, Tesouro Direto (varias modalidades), LCI, LCA, etc.

OBS.: os detalhes de quais atributos cada tipo vai precisar vamos definir mais tarde. O importante eh entender por cima quais tipos vamos precisar suportar.

# Arquitetura proposta

## Visao geral

- Aplicacao dividida em dois servicos: `backend` (API Flask) e `frontend` (SPA Vue.js), orquestrados via Docker Compose em desenvolvimento e implantados como servicos independentes no Google Cloud (ex.: Cloud Run + Firestore).
- Comunicacao entre frontend e backend via REST/JSON sobre HTTPS; autenticacao futura pode usar Firebase Auth para integracao nativa com Firestore.
- Observabilidade baseada em logging estruturado no backend e integracao com Google Cloud Logging; telemetria do frontend via Google Analytics ou similar (a definir).

## Backend (Python + Flask)

- Estrutura modular com blueprints separados por dominio (`passivos`, `renda_variavel`, `renda_fixa`, etc.).
- Camadas distintas para configuracao (`config.py`), servicos de aplicacao (`services/`) e adaptadores de dados (`repositories/`) que encapsulam o acesso ao Firestore.
- Uso de schemas/pydantic ou Marshmallow (a definir) para validacao e serializacao de dados trafegando pelas rotas.
- Integracao com Firestore via biblioteca oficial do Google; em desenvolvimento, o Firebase Emulator Suite roda dentro do compose.
- Testes unitarios com pytest, organizados em `tests/`, cobrindo rotas, regras de negocio e integracao com repositorios.

## Frontend (Vue.js)

- Aplicacao SPA com Vue 3 + Vite, organizando rotas por dominio: `Home`, `Passivos`, `Renda Variavel`, `Renda Fixa`.
- Estado global gerenciado com Pinia, mantendo caches de listas e filtros; comunicacao com backend via servico centralizado (`services/apiClient.ts`).
- Componentizacao seguindo Atomic Design simplificado: componentes basicos em `components/base`, componentes de dominio em `components/domain`.
- Testes unitarios/componentes com Vitest + Vue Test Utils; testes end-to-end futuros com Playwright ou Cypress.

## Dados e infraestrutura

- Firestore como banco principal; colecoes por tipo de ativo/passivo e subcolecoes para historico de movimentacoes.
- Docker Compose para desenvolvimento local com servicos: `backend`, `frontend`, `firestore-emulator` e uma rede compartilhada.
- CI/CD (a definir) orquestrando testes, lint e deploy para Google Cloud (Cloud Run para backend, Firebase Hosting ou Cloud Run para frontend).

## Configuracao de ambiente

- Copiar `.env.example` para `.env` e ajustar os valores conforme necessario (o Docker Compose carrega esse arquivo automaticamente).
- O backend utiliza `python-dotenv` para carregar variaveis quando executado fora do Docker Compose, garantindo a mesma configuracao entre execucao local e containers.
- Variaveis sensiveis (credenciais de acesso ao Google Cloud, por exemplo) nao devem ser commitadas; manter apenas no `.env` local ou em sistemas de segredos do ambiente de deploy.

# Tarefas

1. Documentar o modelo de dados inicial no Firestore (coleções, atributos obrigatórios, enums de tipos) e alinhar contratos de API.
2. Implementar a camada de repositórios integrada ao Firestore Emulator, com testes cobrindo operações básicas e tratamento de erros.
2.1 A integracao com o banco de dados deve ficar desacoplada do codigo principal, de forma que possamos facilmente trocar o client se necessario. Ou seja, uma interface para manter o codigo sem saber que por baixo dos panos tem Firestore.
3. Desenvolver serviços e rotas reais para `passivos`, `renda_variavel` e `renda_fixa`, incluindo filtros e respostas estruturadas.
4. Conectar o frontend ao backend via `apiClient` + Pinia, renderizando listas e estados de carregamento/erro nas views principais.
5. Configurar pipelines de qualidade (lint, `pytest`, `npm run test:unit`) e preparar um esqueleto de CI/CD para builds e deploy.

## Modelo de dados (Firestore)

- `passivos`
  - **id** (string, gerado pelo Firestore)
  - **nome** (string, obrigatório)
  - **categoria** (string, enum: `financiamento`, `emprestimo`, `cartao`, `outros`)
  - **saldo_atual** (number, obrigatório)
  - **taxa_juros_aa** (number, opcional, % anual)
  - **vencimento** (timestamp, opcional)
  - **observacoes** (string, opcional)
- `renda_variavel_positions`
  - **id** (string)
  - **ticker** (string, obrigatório)
  - **tipo** (string, enum: `fii`, `acao_br`, `stock_us`, `etf`, `reit`, `fundo_investimento`, `outros`)
  - **quantidade** (number, obrigatório)
  - **preco_medio** (number, obrigatório)
  - **cotacao_atual** (number, obrigatório)
  - **total_compra** (number, calculado)
  - **total_mercado** (number, calculado)
  - **resultado_monetario** (number, calculado)
  - **performance_percentual** (number, calculado)
  - **peso_percentual** (number, calculado por tipo)
  - **peso_desejado_percentual** (number, configurável)
  - **atualizado_em** (timestamp, obrigatório)
- `renda_variavel_trades`
  - **id** (string)
  - **position_id** (string, referência à coleção `renda_variavel_positions`)
  - **tipo_operacao** (string, enum: `compra`, `venda`)
  - **data** (timestamp, obrigatório)
  - **quantidade** (number, obrigatório)
  - **cotacao** (number, obrigatório)
  - **total** (number, obrigatório)
  - **preco_medio_no_ato** (number, obrigatório para vendas)
  - **resultado_monetario** (number, obrigatório para vendas)
  - **performance_percentual** (number, obrigatório para vendas)
- `renda_variavel_proventos`
  - **id** (string)
  - **position_id** (string)
  - **tipo_provento** (string, enum: `dividendo`, `jcp`, `rendimento`, `outros`)
  - **data** (timestamp, obrigatório)
  - **valor_monetario** (number, obrigatório)
  - **moeda** (string, enum: `brl`, `usd`)
- `renda_fixa_positions`
  - **id** (string)
  - **ativo** (string, obrigatório)
  - **tipo** (string, enum: `cdb`, `lci`, `lca`, `tesouro_prefixado`, `tesouro_ipca`, `tesouro_selic`, `debenture`, `outros`)
  - **indexador** (string, enum: `pre`, `pos_cdi`, `pos_ipca`, `pos_selic`, `outros`)
  - **rentabilidade_aa** (number, obrigatório, % a.a.)
  - **distribuidor** (string, opcional)
  - **valor** (number, obrigatório)
  - **data_inicio** (timestamp, obrigatório)
  - **vencimento** (timestamp, obrigatório)
  - **moeda** (string, padrão `brl`)
- Edição direta de passivos: atualizar `saldo_atual` e `vencimento` conforme necessário, sem histórico de movimentações.

## Contratos de API (v1)

- `GET /passivos`
  - Resposta: `{ "items": Passivo[] }`
- `POST /passivos`
  - Request: `PassivoInput`
  - Resposta: `{ "item": Passivo }`
- `PUT /passivos/{id}` / `DELETE /passivos/{id}`
  - Operações de atualização e remoção; respostas `Passivo` ou `{ "status": "deleted" }`.
- `GET /renda-variavel`
  - Resposta: `{ "positions": Position[], "insights": InsightsResumo }`
- `POST /renda-variavel`
  - Request: `PositionInput`
  - Resposta: `{ "position": Position }`
- `POST /renda-variavel/{id}/trades`
  - Request: `TradeInput`
  - Resposta: `{ "trade": Trade, "position": PositionAtualizada }`
- `POST /renda-variavel/{id}/proventos`
  - Request: `ProventoInput`
  - Resposta: `{ "provento": Provento }`
- `GET /renda-fixa`
  - Resposta: `{ "items": RendaFixaPosition[] }`
- `POST /renda-fixa`
  - Request: `RendaFixaInput`
  - Resposta: `{ "item": RendaFixaPosition }`
- `DELETE /renda-fixa/{id}`
  - Resposta: `{ "status": "deleted" }`

Modelos-base para requests/respostas:

```
type Passivo = {
  id: string;
  nome: string;
  categoria: string;
  saldoAtual: number;
  taxaJurosAa?: number;
  vencimento?: string;
  observacoes?: string;
};

type Position = {
  id: string;
  ticker: string;
  tipo: string;
  quantidade: number;
  precoMedio: number;
  cotacaoAtual: number;
  totalCompra: number;
  totalMercado: number;
  resultadoMonetario: number;
  performancePercentual: number;
  pesoPercentual: number;
  pesoDesejadoPercentual: number;
  atualizadoEm: string;
};

type TradeInput = {
  tipoOperacao: "compra" | "venda";
  data: string;
  quantidade: number;
  cotacao: number;
  precoMedioNoAto?: number;
  resultadoMonetario?: number;
  performancePercentual?: number;
};

type RendaFixaPosition = {
  id: string;
  ativo: string;
  tipo: string;
  indexador: string;
  rentabilidadeAa: number;
  distribuidor?: string;
  valor: number;
  dataInicio: string;
  vencimento: string;
  moeda: string;
};
```

# Regras de negocio

- Para a renda variavel, todos os tipos devem conter isso: Ativo, Quantidade, Preço Médio, Cotação Atual, Total Compra, Total Mercado, Resultado (R$ ou U$ dependendo do caso), Performance %, Peso % (em relacao aos outros ativos do mesmo tipo),	Peso Desejado (em relacao aos outros ativos do mesmo tipo).
    - Exemplo: Ativo: HSML11, Quantidade: 80, Preco Medio: R$10, Cotacao Atual: R$20, Total Compra: R$800, Total Mercado: R$1600, Resultado: R$800, Performance: 100%, Peso: 100%, Peso Desejado: 25%.
- Novos registros de compra de qualquer renda variavel devem conter: Data, Ativo, Quantidade, Cotação, Total (R$ ou U$ dependendo do caso).
- Novos registros de venda de qualquer renda variavel devem conter: Data, Ativo, Quantidade, Preço Médio, Cotação Venda, Total Venda, Resultado (R$ ou U$), Performance %
- Registro de proventos recebidos (JCP,Rendimento, Dividendos, etc).
- Possibilidade de Editar ou Excluir registros/ativos.
- Para registros de renda fixa, usar: Data Início, Ativo, Tipo, Indexador, Rentabilidade a.a.,	Distribuidor, Vencimento, Valor.
    - Exemplo: 23/02/2023, CDB AGIBANK - FEV/2025, CDB, Prefixado, 14,55%, XP Investimentos, 24/02/2025, R$ 5.000,00
