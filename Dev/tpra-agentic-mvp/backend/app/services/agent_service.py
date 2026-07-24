"""Agent orchestration service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.agents.agent_registry import AgentRegistry
from app.agents.draft_report.graph import run_uc2
from app.agents.structured_findings.graph import run_uc1
from app.core.exceptions import NotFoundError, ValidationError
from app.domain.enums import AgentId, RunStatus
from app.domain.models import AuditEvent, Run, UserContext
from app.providers.registry import ProviderRegistry
from app.repositories.audit_repository import AuditRepository
from app.repositories.file_repository import FileRepository
from app.repositories.run_repository import RunRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.authz import require_permission
from app.services.file_service import FileService


class AgentService:
    def __init__(
        self,
        *,
        runs: RunRepository,
        workspaces: WorkspaceRepository,
        files: FileRepository,
        file_service: FileService,
        audit: AuditRepository,
        providers: ProviderRegistry,
        agent_registry: AgentRegistry,
    ):
        self.runs = runs
        self.workspaces = workspaces
        self.files = files
        self.file_service = file_service
        self.audit = audit
        self.providers = providers
        self.agent_registry = agent_registry

    def catalog(self) -> list[dict[str, Any]]:
        return self.agent_registry.list_agents()

    def run_agent(
        self,
        *,
        workspace_id: str,
        agent_id: str,
        input_file_ids: list[str],
        user: UserContext,
        options: dict[str, Any] | None = None,
    ) -> Run:
        require_permission(user, "agent:run")
        if not self.workspaces.get(workspace_id):
            raise NotFoundError(f"Workspace not found: {workspace_id}")
        if agent_id not in {AgentId.UC1.value, AgentId.UC2.value, "uc1", "uc2"}:
            # also accept short aliases
            if agent_id not in {a["id"] for a in self.agent_registry.list_agents()}:
                raise ValidationError(f"Unknown agent_id: {agent_id}")

        normalized_id = self._normalize_agent_id(agent_id)
        run = Run(
            workspace_id=workspace_id,
            agent_id=normalized_id,
            status=RunStatus.RUNNING,
            created_by=user.user_id,
            input_file_ids=input_file_ids,
            started_at=datetime.now(timezone.utc),
        )
        self.runs.save(run)
        self.audit.save(
            AuditEvent(
                workspace_id=workspace_id,
                actor=user.user_id,
                action="agent.run.start",
                resource_type="run",
                resource_id=run.id,
                details={"agent_id": normalized_id, "input_file_ids": input_file_ids},
            )
        )

        try:
            file_payloads = []
            for fid in input_file_ids:
                record = self.files.get(fid)
                if not record or record.workspace_id != workspace_id:
                    raise NotFoundError(f"Input file not found in workspace: {fid}")
                data = self.providers.storage.get_bytes(record.storage_key)
                file_payloads.append({"record": record, "data": data})

            ctx = {
                "workspace_id": workspace_id,
                "run_id": run.id,
                "user": user,
                "files": file_payloads,
                "options": options or {},
                "providers": self.providers,
                "file_service": self.file_service,
                "audit": self.audit,
            }

            if normalized_id == AgentId.UC1.value:
                result = run_uc1(ctx)
            else:
                result = run_uc2(ctx)

            run.status = RunStatus.SUCCEEDED
            run.result = result.get("response", {})
            run.output_file_ids = result.get("output_file_ids", [])
            run.step_traces = result.get("step_traces", [])
            run.finished_at = datetime.now(timezone.utc)
            self.runs.save(run)
            self.audit.save(
                AuditEvent(
                    workspace_id=workspace_id,
                    actor=user.user_id,
                    action="agent.run.succeed",
                    resource_type="run",
                    resource_id=run.id,
                    details={"output_file_ids": run.output_file_ids},
                )
            )
            return run
        except Exception as exc:  # noqa: BLE001 — persist failure then re-raise shape
            run.status = RunStatus.FAILED
            run.error = str(exc)
            run.finished_at = datetime.now(timezone.utc)
            self.runs.save(run)
            self.audit.save(
                AuditEvent(
                    workspace_id=workspace_id,
                    actor=user.user_id,
                    action="agent.run.fail",
                    resource_type="run",
                    resource_id=run.id,
                    details={"error": str(exc)},
                )
            )
            raise

    def get_run(self, run_id: str, user: UserContext) -> Run:
        require_permission(user, "workspace:read")
        run = self.runs.get(run_id)
        if not run:
            raise NotFoundError(f"Run not found: {run_id}")
        return run

    def list_runs(self, workspace_id: str, user: UserContext) -> list[Run]:
        require_permission(user, "workspace:read")
        if not self.workspaces.get(workspace_id):
            raise NotFoundError(f"Workspace not found: {workspace_id}")
        return self.runs.list_for_workspace(workspace_id)

    @staticmethod
    def _normalize_agent_id(agent_id: str) -> str:
        if agent_id in ("uc1", AgentId.UC1.value):
            return AgentId.UC1.value
        if agent_id in ("uc2", AgentId.UC2.value):
            return AgentId.UC2.value
        return agent_id
