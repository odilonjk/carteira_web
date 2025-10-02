# Repository Guidelines

## Project Structure & Module Organization
- Root splits into `backend/` (Flask API) and `frontend/` (Vue 3 SPA); `docker-compose.yml` orchestrates local services plus the Firestore emulator.
- Backend keeps config in `app/config.py`, blueprints in `app/routes/`, services in `app/services/`, repositories wrapping Firestore in `app/repositories/`, and tests in `backend/tests/`.
- Frontend source stays under `src/` with views in `src/views/`, the Pinia store in `src/store/`, API helpers in `src/services/`, and tests in `frontend/tests/` (`unit/` now, `e2e/` reserved).

## Build, Test, and Development Commands
- `docker compose up --build` runs the full stack; `docker compose down --volumes` resets Firestore data.
- Backend: `cd backend && flask --app app run --debug` for live reload, `pytest` for automated checks.
- Frontend: `cd frontend && npm install` once, then `npm run dev -- --host` to serve, `npm run build` for production bundles, `npm run test:unit` for Vitest.

## Coding Style & Naming Conventions
- Python modules follow PEP 8, stay fully typed, and use lowercase snake case names (`renda_variavel`). Keep domain logic inside services and repositories, exposing slim route handlers.
- Vue SFCs use 2-space indentation, `<script setup lang="ts">`, and PascalCase filenames (`PassivosView.vue`). Stores and helpers export named functions; prefer camelCase for variables and UPPER_SNAKE_CASE for env keys.

## Testing Guidelines
- Place backend tests alongside their feature folder when possible, named `test_*.py`, and reuse fixtures from `backend/tests/conftest.py`.
- Frontend specs belong in `frontend/tests/unit/*.spec.ts`; stub Axios via Vitest mocks to isolate components.
- Run `pytest` and `npm run test:unit` before each PR; target coverage of health endpoints, passivos/renda flows, and view rendering.

## Commit & Pull Request Guidelines
- History is empty so far—start with Conventional Commits (`feat: add renda fixa view`) to keep the log searchable.
- Pull requests should explain scope, link any issue, and attach screenshots or CLI output when UI or API responses change.
- Rebase onto `main`, confirm `docker compose up` succeeds, and check formatting before requesting review.

## Environment & Configuration
- Duplicate `.env.example` to `.env` in the repo root (and service folders if they diverge); Compose loads it automatically.
- When running services directly, export `FIRESTORE_EMULATOR_HOST=localhost:8080` to stay on the emulator and keep secrets out of version control.
