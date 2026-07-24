from fastapi import APIRouter, Depends

from app.api.deps import registry_dep, settings_dep
from app.core.config import Settings
from app.providers.registry import ProviderRegistry
from app.schemas.api import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(settings_dep),
    registry: ProviderRegistry = Depends(registry_dep),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        providers=registry.provider_map(),
    )
