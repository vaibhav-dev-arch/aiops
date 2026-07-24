"""Workspace lifecycle service."""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import NotFoundError
from app.domain.models import AuditEvent, UserContext, Workspace
from app.repositories.audit_repository import AuditRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.authz import require_permission


class WorkspaceService:
    def __init__(self, workspaces: WorkspaceRepository, audit: AuditRepository):
        self.workspaces = workspaces
        self.audit = audit

    def create(self, *, name: str, description: str, user: UserContext, metadata: dict | None = None) -> Workspace:
        require_permission(user, "workspace:create")
        ws = Workspace(
            name=name,
            description=description,
            created_by=user.user_id,
            metadata=metadata or {},
        )
        self.workspaces.save(ws)
        self.audit.save(
            AuditEvent(
                workspace_id=ws.id,
                actor=user.user_id,
                action="workspace.create",
                resource_type="workspace",
                resource_id=ws.id,
                details={"name": name},
            )
        )
        return ws

    def list(self, user: UserContext) -> list[Workspace]:
        require_permission(user, "workspace:read")
        return self.workspaces.list()

    def get(self, workspace_id: str, user: UserContext) -> Workspace:
        require_permission(user, "workspace:read")
        ws = self.workspaces.get(workspace_id)
        if not ws:
            raise NotFoundError(f"Workspace not found: {workspace_id}")
        return ws

    def delete(self, workspace_id: str, user: UserContext) -> None:
        require_permission(user, "workspace:delete")
        ws = self.get(workspace_id, user)
        self.workspaces.delete(ws.id)
        self.audit.save(
            AuditEvent(
                workspace_id=ws.id,
                actor=user.user_id,
                action="workspace.delete",
                resource_type="workspace",
                resource_id=ws.id,
            )
        )

    def touch(self, workspace_id: str) -> None:
        ws = self.workspaces.get(workspace_id)
        if ws:
            ws.updated_at = datetime.now(timezone.utc)
            self.workspaces.save(ws)
