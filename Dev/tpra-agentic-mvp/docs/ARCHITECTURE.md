# Architecture

The TPRA Agentic MVP follows clean architecture with provider abstraction so the same codebase runs locally or on Azure.

## Layers

1. **API** (`app/api`) — FastAPI routes and request/response schemas
2. **Services** (`app/services`) — orchestration, authz, workspace/file/agent lifecycle
3. **Agents** (`app/agents`) — UC1/UC2 sequential workflow graphs
4. **Domain** (`app/domain`) — canonical models and validation rules
5. **Providers** (`app/providers`) — storage, metadata, LLM, auth, document intelligence adapters
6. **Repositories** (`app/repositories`) — metadata persistence over the metadata provider

## Agent registry

`foundry/agents.yaml` is the source of truth for agent IDs, capabilities, and prompt references.

## Workflow engine

`app/agents/graph.py` runs ordered named steps against shared state, records traces, and supports short-circuit via `StopWorkflow`.

## Provider switching

Set providers in `backend/config.yaml` or via environment variables (`STORAGE_PROVIDER`, `METADATA_PROVIDER`, `LLM_PROVIDER`, `AUTH_PROVIDER`, `DOC_INTEL_PROVIDER`).
