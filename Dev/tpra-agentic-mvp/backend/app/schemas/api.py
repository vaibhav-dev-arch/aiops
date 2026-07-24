"""API request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str
    providers: dict[str, str]
    version: str = "0.1.0"


class AgentCatalogItem(BaseModel):
    id: str
    name: str
    description: str
    capabilities: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    model: str | None = None


class WorkspaceCreate(BaseModel):
    name: str
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class FileResponse(BaseModel):
    id: str
    workspace_id: str
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime
    uploaded_by: str
    tags: list[str] = Field(default_factory=list)


class AgentRunRequest(BaseModel):
    agent_id: str
    input_file_ids: list[str] = Field(default_factory=list)
    options: dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    id: str
    workspace_id: str
    agent_id: str
    status: str
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_by: str
    input_file_ids: list[str] = Field(default_factory=list)
    output_file_ids: list[str] = Field(default_factory=list)
    step_traces: list[dict[str, Any]] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ReviewerDecisionCreate(BaseModel):
    finding_id: str
    decision: str
    comment: str = ""


class ReviewerDecisionResponse(BaseModel):
    id: str
    workspace_id: str
    finding_id: str
    decision: str
    comment: str
    reviewer: str
    role: str
    created_at: datetime


class AuditEventResponse(BaseModel):
    id: str
    workspace_id: str | None = None
    actor: str
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
