"""Custom exception hierarchy for structured API errors."""

from __future__ import annotations


class TPRAError(Exception):
    """Base application error."""

    def __init__(self, message: str, *, code: str = "tpra_error", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class ValidationError(TPRAError):
    def __init__(self, message: str, *, code: str = "validation_error"):
        super().__init__(message, code=code, status_code=422)


class AuthzError(TPRAError):
    def __init__(self, message: str = "Not authorized", *, code: str = "authz_error"):
        super().__init__(message, code=code, status_code=403)


class NotFoundError(TPRAError):
    def __init__(self, message: str, *, code: str = "not_found"):
        super().__init__(message, code=code, status_code=404)
