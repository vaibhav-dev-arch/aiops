"""FastAPI dependency injection."""

from __future__ import annotations

from fastapi import Depends, Request

from app.agents.agent_registry import AgentRegistry
from app.core.config import Settings, get_settings
from app.domain.models import UserContext
from app.providers.registry import ProviderRegistry, get_registry
from app.repositories.audit_repository import AuditRepository
from app.repositories.file_repository import FileRepository
from app.repositories.reviewer_log_repository import ReviewerLogRepository
from app.repositories.run_repository import RunRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agent_service import AgentService
from app.services.file_service import FileService
from app.services.reviewer_log_service import ReviewerLogService
from app.services.workspace_service import WorkspaceService


def settings_dep() -> Settings:
    return get_settings()


def registry_dep() -> ProviderRegistry:
    return get_registry()


def current_user(request: Request, registry: ProviderRegistry = Depends(registry_dep)) -> UserContext:
    headers = {k: v for k, v in request.headers.items()}
    return registry.auth.authenticate(headers)


def workspace_service(registry: ProviderRegistry = Depends(registry_dep)) -> WorkspaceService:
    return WorkspaceService(
        WorkspaceRepository(registry.metadata),
        AuditRepository(registry.metadata),
    )


def file_service(registry: ProviderRegistry = Depends(registry_dep)) -> FileService:
    return FileService(
        FileRepository(registry.metadata),
        WorkspaceRepository(registry.metadata),
        registry.storage,
        AuditRepository(registry.metadata),
    )


def reviewer_log_service(registry: ProviderRegistry = Depends(registry_dep)) -> ReviewerLogService:
    return ReviewerLogService(
        ReviewerLogRepository(registry.metadata),
        WorkspaceRepository(registry.metadata),
        AuditRepository(registry.metadata),
    )


def agent_service(registry: ProviderRegistry = Depends(registry_dep)) -> AgentService:
    fs = FileService(
        FileRepository(registry.metadata),
        WorkspaceRepository(registry.metadata),
        registry.storage,
        AuditRepository(registry.metadata),
    )
    return AgentService(
        runs=RunRepository(registry.metadata),
        workspaces=WorkspaceRepository(registry.metadata),
        files=FileRepository(registry.metadata),
        file_service=fs,
        audit=AuditRepository(registry.metadata),
        providers=registry,
        agent_registry=AgentRegistry(),
    )


def audit_repo(registry: ProviderRegistry = Depends(registry_dep)) -> AuditRepository:
    return AuditRepository(registry.metadata)
