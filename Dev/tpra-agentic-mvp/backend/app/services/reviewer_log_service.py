"""Reviewer decision service."""

from __future__ import annotations

from app.core.exceptions import NotFoundError, ValidationError
from app.domain.models import AuditEvent, ReviewerDecision, UserContext
from app.repositories.audit_repository import AuditRepository
from app.repositories.reviewer_log_repository import ReviewerLogRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.authz import require_permission

ALLOWED_DECISIONS = {"approve", "reject", "comment"}


class ReviewerLogService:
    def __init__(
        self,
        reviewer_log: ReviewerLogRepository,
        workspaces: WorkspaceRepository,
        audit: AuditRepository,
    ):
        self.reviewer_log = reviewer_log
        self.workspaces = workspaces
        self.audit = audit

    def add_decision(
        self,
        *,
        workspace_id: str,
        finding_id: str,
        decision: str,
        comment: str,
        user: UserContext,
    ) -> ReviewerDecision:
        require_permission(user, "reviewer:decide")
        if not self.workspaces.get(workspace_id):
            raise NotFoundError(f"Workspace not found: {workspace_id}")
        decision_norm = decision.strip().lower()
        if decision_norm not in ALLOWED_DECISIONS:
            raise ValidationError(f"decision must be one of {sorted(ALLOWED_DECISIONS)}")
        entry = ReviewerDecision(
            workspace_id=workspace_id,
            finding_id=finding_id,
            decision=decision_norm,
            comment=comment,
            reviewer=user.user_id,
            role=user.role,
        )
        self.reviewer_log.save(entry)
        self.audit.save(
            AuditEvent(
                workspace_id=workspace_id,
                actor=user.user_id,
                action="reviewer.decide",
                resource_type="finding",
                resource_id=finding_id,
                details={"decision": decision_norm, "comment": comment},
            )
        )
        return entry

    def list(self, workspace_id: str, user: UserContext) -> list[ReviewerDecision]:
        require_permission(user, "workspace:read")
        if not self.workspaces.get(workspace_id):
            raise NotFoundError(f"Workspace not found: {workspace_id}")
        return self.reviewer_log.list_for_workspace(workspace_id)
