from fastapi import APIRouter, Depends

from app.api.deps import agent_service, current_user
from app.domain.models import UserContext
from app.schemas.api import AgentCatalogItem
from app.services.agent_service import AgentService

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/agents", response_model=list[AgentCatalogItem])
def list_agents(
    service: AgentService = Depends(agent_service),
    _user: UserContext = Depends(current_user),
) -> list[AgentCatalogItem]:
    return [AgentCatalogItem.model_validate(a) for a in service.catalog()]
