# Migration Guide — Local → Client DaVinci

1. Copy `.env.client.example` to `.env` and fill Azure credentials.
2. Switch `backend/config.yaml` providers to Azure (or use `config.client.example.yaml`).
3. Provision infra with `infra/bicep/main.bicep` and stage parameters.
4. Publish prompts with `scripts/upload_prompts.py`.
5. Create Foundry agents with `scripts/create_foundry_agents.py`.
6. Replace `AUTH_PROVIDER=dev` with `client_sso` and wire OIDC JWT validation.
7. Deploy via `azure-pipelines/azure-pipelines.yml` progressive stages.
