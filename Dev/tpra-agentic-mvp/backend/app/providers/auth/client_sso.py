"""Client SSO auth stub (JWT/OIDC)."""

from __future__ import annotations

from app.core.exceptions import AuthzError
from app.domain.models import UserContext
from app.providers.base import AuthProvider


class ClientSSOAuthProvider(AuthProvider):
    def authenticate(self, headers: dict[str, str]) -> UserContext:
        normalized = {k.lower(): v for k, v in headers.items()}
        auth = normalized.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            raise AuthzError("Missing Bearer token for client SSO")
        raise AuthzError(
            "Client SSO stub — wire OIDC JWT validation for production.",
        )
