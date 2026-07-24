from fastapi import APIRouter, Depends, status

from app.api.deps import agent_service, current_user
from app.core.exceptions import TPRAError
from app.domain.models import UserContext
from app.schemas.api import AgentRunRequest, AgentRunResponse
from app.services.agent_service import AgentService

router = APIRouter(tags=["agents"])


def _to_response(run) -> AgentRunResponse:
    return AgentRunResponse.model_validate(run.model_dump(mode="json"))


@router.post(
    "/workspaces/{workspace_id}/agents/runs",
    response_model=AgentRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_run(
    workspace_id: str,
    body: AgentRunRequest,
    service: AgentService = Depends(agent_service),
    user: UserContext = Depends(current_user),
) -> AgentRunResponse:
    try:
        run = service.run_agent(
            workspace_id=workspace_id,
            agent_id=body.agent_id,
            input_file_ids=body.input_file_ids,
            user=user,
            options=body.options,
        )
    except TPRAError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise TPRAError(str(exc), code="agent_run_failed", status_code=500) from exc
    return _to_response(run)


@router.get("/workspaces/{workspace_id}/agents/runs", response_model=list[AgentRunResponse])
def list_runs(
    workspace_id: str,
    service: AgentService = Depends(agent_service),
    user: UserContext = Depends(current_user),
) -> list[AgentRunResponse]:
    return [_to_response(r) for r in service.list_runs(workspace_id, user)]


@router.get("/agents/runs/{run_id}", response_model=AgentRunResponse)
def get_run(
    run_id: str,
    service: AgentService = Depends(agent_service),
    user: UserContext = Depends(current_user),
) -> AgentRunResponse:
    return _to_response(service.get_run(run_id, user))
