"""Validate normalized findings and flag exceptions."""

from __future__ import annotations

from app.domain.enums import FindingStatus
from app.domain.models import ExceptionRecord, Finding
from app.domain.validation_rules import ALLOWED_CATEGORIES, validate_finding_fields


def validate_findings(findings: list[Finding]) -> tuple[list[Finding], list[ExceptionRecord]]:
    exceptions: list[ExceptionRecord] = []
    for finding in findings:
        row = {
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity,
            "category": finding.category,
            "source": finding.source,
        }
        issues = validate_finding_fields(row)
        if issues:
            finding.status = FindingStatus.EXCEPTION
            for issue in issues:
                exceptions.append(
                    ExceptionRecord(
                        finding_id=finding.id,
                        field=issue["field"],
                        message=issue["message"],
                        severity=issue.get("severity", "error"),
                        raw=row,
                    )
                )
        else:
            finding.status = FindingStatus.VALID
            if finding.category not in ALLOWED_CATEGORIES:
                finding.category = "general"
    return findings, exceptions
