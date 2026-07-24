"""Domain enumerations."""

from __future__ import annotations

from enum import Enum


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FindingStatus(str, Enum):
    VALID = "valid"
    EXCEPTION = "exception"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalLevel(str, Enum):
    NONE = "none"
    REVIEWER = "reviewer"
    APPROVER = "approver"


class UserRole(str, Enum):
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    APPROVER = "approver"
    ADMIN = "admin"


class ProviderType(str, Enum):
    LOCAL = "local"
    AZURE = "azure"
    SQLITE = "sqlite"
    COSMOS = "cosmos"
    MOCK = "mock"
    AZURE_OPENAI = "azure_openai"
    FOUNDRY = "foundry"
    DEV = "dev"
    CLIENT_SSO = "client_sso"


class AgentId(str, Enum):
    UC1 = "uc1_structured_findings"
    UC2 = "uc2_draft_report"
