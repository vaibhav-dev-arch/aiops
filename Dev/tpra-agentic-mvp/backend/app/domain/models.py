"""Canonical domain models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.domain.enums import FindingStatus, RunStatus, UserRole


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: new_id("f"))
    title: str
    description: str = ""
    severity: str = "medium"
    category: str = "general"
    source: str = ""
    status: FindingStatus = FindingStatus.VALID
    raw: dict[str, Any] = Field(default_factory=dict)


class ExceptionRecord(BaseModel):
    finding_id: str | None = None
    field: str
    message: str
    severity: str = "error"
    raw: dict[str, Any] = Field(default_factory=dict)


class Workspace(BaseModel):
    id: str = Field(default_factory=lambda: new_id("ws"))
    name: str
    description: str = ""
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    created_by: str = "system"
    metadata: dict[str, Any] = Field(default_factory=dict)


class FileRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("file"))
    workspace_id: str
    filename: str
    content_type: str = "application/octet-stream"
    size: int = 0
    storage_key: str
    uploaded_at: datetime = Field(default_factory=_utcnow)
    uploaded_by: str = "system"
    tags: list[str] = Field(default_factory=list)


class Run(BaseModel):
    id: str = Field(default_factory=lambda: new_id("run"))
    workspace_id: str
    agent_id: str
    status: RunStatus = RunStatus.PENDING
    created_at: datetime = Field(default_factory=_utcnow)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_by: str = "system"
    input_file_ids: list[str] = Field(default_factory=list)
    output_file_ids: list[str] = Field(default_factory=list)
    step_traces: list[dict[str, Any]] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ReviewerDecision(BaseModel):
    id: str = Field(default_factory=lambda: new_id("rv"))
    workspace_id: str
    finding_id: str
    decision: str  # approve | reject | comment
    comment: str = ""
    reviewer: str
    role: UserRole = UserRole.REVIEWER
    created_at: datetime = Field(default_factory=_utcnow)


class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("aud"))
    workspace_id: str | None = None
    actor: str
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utcnow)


class UserContext(BaseModel):
    user_id: str
    display_name: str
    role: UserRole = UserRole.ANALYST
    email: str | None = None
