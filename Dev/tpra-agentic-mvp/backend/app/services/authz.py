"""Role-based access control helpers."""

from __future__ import annotations

from app.core.exceptions import AuthzError
from app.domain.enums import UserRole
from app.domain.models import UserContext

# action -> minimum roles allowed
ROLE_PERMISSIONS: dict[str, set[UserRole]] = {
    "workspace:create": {UserRole.ANALYST, UserRole.REVIEWER, UserRole.APPROVER, UserRole.ADMIN},
    "workspace:read": {UserRole.ANALYST, UserRole.REVIEWER, UserRole.APPROVER, UserRole.ADMIN},
    "workspace:delete": {UserRole.ADMIN, UserRole.APPROVER},
    "file:upload": {UserRole.ANALYST, UserRole.REVIEWER, UserRole.APPROVER, UserRole.ADMIN},
    "file:download": {UserRole.ANALYST, UserRole.REVIEWER, UserRole.APPROVER, UserRole.ADMIN},
    "agent:run": {UserRole.ANALYST, UserRole.REVIEWER, UserRole.APPROVER, UserRole.ADMIN},
    "reviewer:decide": {UserRole.REVIEWER, UserRole.APPROVER, UserRole.ADMIN},
    "audit:read": {UserRole.ANALYST, UserRole.REVIEWER, UserRole.APPROVER, UserRole.ADMIN},
}


def require_permission(user: UserContext, action: str) -> None:
    allowed = ROLE_PERMISSIONS.get(action)
    if allowed is None:
        raise AuthzError(f"Unknown action: {action}")
    if user.role not in allowed:
        raise AuthzError(f"Role '{user.role.value}' cannot perform '{action}'")
