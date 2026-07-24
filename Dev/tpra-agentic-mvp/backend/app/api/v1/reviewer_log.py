from fastapi import APIRouter, Depends, status

from app.api.deps import current_user, reviewer_log_service
from app.domain.models import UserContext
from app.schemas.api import ReviewerDecisionCreate, ReviewerDecisionResponse
from app.services.reviewer_log_service import ReviewerLogService

router = APIRouter(tags=["reviewer-log"])


@router.post(
    "/workspaces/{workspace_id}/reviewer-log",
    response_model=ReviewerDecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_decision(
    workspace_id: str,
    body: ReviewerDecisionCreate,
    service: ReviewerLogService = Depends(reviewer_log_service),
    user: UserContext = Depends(current_user),
) -> ReviewerDecisionResponse:
    entry = service.add_decision(
        workspace_id=workspace_id,
        finding_id=body.finding_id,
        decision=body.decision,
        comment=body.comment,
        user=user,
    )
    return ReviewerDecisionResponse.model_validate(entry.model_dump(mode="json"))


@router.get("/workspaces/{workspace_id}/reviewer-log", response_model=list[ReviewerDecisionResponse])
def list_decisions(
    workspace_id: str,
    service: ReviewerLogService = Depends(reviewer_log_service),
    user: UserContext = Depends(current_user),
) -> list[ReviewerDecisionResponse]:
    return [
        ReviewerDecisionResponse.model_validate(e.model_dump(mode="json"))
        for e in service.list(workspace_id, user)
    ]
