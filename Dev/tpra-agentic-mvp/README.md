# Client TPRA Agentic MVP

Human-in-the-loop agentic platform for Third Party Risk Assessment (TPRA).

## Agents

- **UC1 — Structured Findings Package Agent**: Ingests Excel/CSV/JSON/DOCX findings, normalizes to a canonical schema, validates, and packages outputs.
- **UC2 — Draft TPRA Report Agent**: Takes approved findings, maps to a report template, drafts narrative via LLM, and produces a DOCX draft.

## Architecture

Build once, run anywhere via a **provider registry**:

| Concern | Local | Azure |
|---------|-------|-------|
| Storage | Filesystem | Blob Storage |
| Metadata | SQLite | Cosmos DB |
| LLM | Mock | Azure OpenAI / Foundry |
| Auth | Dev headers | Client SSO |
| Doc Intel | Local parsers | Azure Document Intelligence |

## Quickstart (local)

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.local.example ../.env
uvicorn app.main:app --reload --app-dir .
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Or: `docker compose up --build`

## Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

## Repository layout

- `backend/` — FastAPI API, agents, providers
- `frontend/` — React + Vite + TypeScript UI
- `prompts/` — Versioned agent prompts
- `foundry/` — Agent registry & Foundry deployment defs
- `scripts/` — Deploy helpers
- `infra/bicep/` — Azure IaC
- `azure-pipelines/` — CI/CD
- `docs/` — Architecture & migration guides
