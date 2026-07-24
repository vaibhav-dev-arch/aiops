"""Business validation rules for findings."""

from __future__ import annotations

from typing import Any

REQUIRED_FIELDS = ("title", "severity", "category")
ALLOWED_SEVERITIES = {"critical", "high", "medium", "low", "info"}
ALLOWED_CATEGORIES = {
    "identity",
    "cloud",
    "network",
    "logging",
    "application",
    "data",
    "governance",
    "general",
}


def validate_finding_fields(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return list of exception dicts for a finding row."""
    exceptions: list[dict[str, Any]] = []
    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or str(value).strip() == "":
            exceptions.append(
                {
                    "field": field,
                    "message": f"Missing required field: {field}",
                    "severity": "error",
                }
            )

    severity = str(row.get("severity", "")).strip().lower()
    if severity and severity not in ALLOWED_SEVERITIES:
        exceptions.append(
            {
                "field": "severity",
                "message": f"Invalid severity '{severity}'. Allowed: {sorted(ALLOWED_SEVERITIES)}",
                "severity": "warning",
            }
        )

    category = str(row.get("category", "")).strip().lower()
    if category and category not in ALLOWED_CATEGORIES:
        exceptions.append(
            {
                "field": "category",
                "message": f"Unrecognized category '{category}' — will map to 'general'",
                "severity": "info",
            }
        )
    return exceptions
