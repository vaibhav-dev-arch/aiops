"""Development auth — trusts identity from HTTP headers."""

from __future__ import annotations

from app.domain.enums import UserRole
from app.domain.models import UserContext
from app.providers.base import AuthProvider


class DevAuthProvider(AuthProvider):
    def authenticate(self, headers: dict[str, str]) -> UserContext:
        # Normalize header keys
        normalized = {k.lower(): v for k, v in headers.items()}
        user_id = normalized.get("x-user-id") or normalized.get("x-dev-user") or "dev-user"
        display = normalized.get("x-user-name") or normalized.get("x-dev-name") or "Dev User"
        role_raw = (normalized.get("x-user-role") or normalized.get("x-dev-role") or "analyst").lower()
        try:
            role = UserRole(role_raw)
        except ValueError:
            role = UserRole.ANALYST
        email = normalized.get("x-user-email")
        return UserContext(user_id=user_id, display_name=display, role=role, email=email)
