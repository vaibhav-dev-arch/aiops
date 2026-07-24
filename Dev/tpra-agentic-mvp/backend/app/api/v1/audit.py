from fastapi import APIRouter, Depends

from app.api.deps import audit_repo, current_user
from app.domain.models import UserContext
from app.repositories.audit_repository import AuditRepository
from app.schemas.api import AuditEventResponse
from app.services.authz import require_permission

router = APIRouter(tags=["audit"])


@router.get("/audit", response_model=list[AuditEventResponse])
def list_audit(
    workspace_id: str | None = None,
    repo: AuditRepository = Depends(audit_repo),
    user: UserContext = Depends(current_user),
) -> list[AuditEventResponse]:
    require_permission(user, "audit:read")
    events = repo.list_for_workspace(workspace_id)
    # newest first
    events_sorted = sorted(events, key=lambda e: e.created_at, reverse=True)
    return [AuditEventResponse.model_validate(e.model_dump(mode="json")) for e in events_sorted]


@router.get("/workspaces/{workspace_id}/audit", response_model=list[AuditEventResponse])
def list_workspace_audit(
    workspace_id: str,
    repo: AuditRepository = Depends(audit_repo),
    user: UserContext = Depends(current_user),
) -> list[AuditEventResponse]:
    require_permission(user, "audit:read")
    events = repo.list_for_workspace(workspace_id)
    events_sorted = sorted(events, key=lambda e: e.created_at, reverse=True)
    return [AuditEventResponse.model_validate(e.model_dump(mode="json")) for e in events_sorted]
