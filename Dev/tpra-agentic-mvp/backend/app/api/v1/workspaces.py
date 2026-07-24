from fastapi import APIRouter, Depends, status

from app.api.deps import current_user, workspace_service
from app.domain.models import UserContext
from app.schemas.api import WorkspaceCreate, WorkspaceResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    service: WorkspaceService = Depends(workspace_service),
    user: UserContext = Depends(current_user),
) -> list[WorkspaceResponse]:
    return [WorkspaceResponse.model_validate(w.model_dump(mode="json")) for w in service.list(user)]


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    body: WorkspaceCreate,
    service: WorkspaceService = Depends(workspace_service),
    user: UserContext = Depends(current_user),
) -> WorkspaceResponse:
    ws = service.create(name=body.name, description=body.description, user=user, metadata=body.metadata)
    return WorkspaceResponse.model_validate(ws.model_dump(mode="json"))


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: str,
    service: WorkspaceService = Depends(workspace_service),
    user: UserContext = Depends(current_user),
) -> WorkspaceResponse:
    ws = service.get(workspace_id, user)
    return WorkspaceResponse.model_validate(ws.model_dump(mode="json"))


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: str,
    service: WorkspaceService = Depends(workspace_service),
    user: UserContext = Depends(current_user),
) -> None:
    service.delete(workspace_id, user)
