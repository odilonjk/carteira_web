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

1. Entender os requisitos do sistema.
2. Desenhar uma arquitetura para esse sistema.
3. Criar a estrutura inicial (pastas para backend considenrando boas praticas pythonicas e pastas para frontend considerando boas praticas de vue.js).
