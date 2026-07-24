"""Normalize vendor findings into the canonical TPRA schema."""

from __future__ import annotations

from typing import Any

from app.domain.enums import FindingStatus
from app.domain.models import Finding, new_id

FIELD_ALIASES = {
    "title": {"title", "finding", "name", "summary", "finding_title"},
    "description": {"description", "detail", "details", "desc", "observation"},
    "severity": {"severity", "risk", "priority", "sev"},
    "category": {"category", "domain", "control_domain", "area", "type"},
    "source": {"source", "vendor", "system", "origin"},
}

SEVERITY_MAP = {
    "crit": "critical",
    "critical": "critical",
    "1": "critical",
    "high": "high",
    "h": "high",
    "2": "high",
    "med": "medium",
    "medium": "medium",
    "m": "medium",
    "3": "medium",
    "low": "low",
    "l": "low",
    "4": "low",
    "info": "info",
    "informational": "info",
    "5": "info",
}


def _pick(row: dict[str, Any], canonical: str) -> str:
    aliases = FIELD_ALIASES[canonical]
    lower_map = {str(k).strip().lower(): v for k, v in row.items()}
    for alias in aliases:
        if alias in lower_map and str(lower_map[alias]).strip():
            return str(lower_map[alias]).strip()
    return ""


def normalize_rows(rows: list[dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    seen_titles: set[str] = set()
    for row in rows:
        title = _pick(row, "title") or "Untitled finding"
        dedupe_key = title.lower()
        if dedupe_key in seen_titles:
            continue
        seen_titles.add(dedupe_key)

        severity_raw = _pick(row, "severity").lower() or "medium"
        severity = SEVERITY_MAP.get(severity_raw, severity_raw if severity_raw else "medium")
        category = (_pick(row, "category") or "general").lower()
        finding = Finding(
            id=new_id("f"),
            title=title,
            description=_pick(row, "description"),
            severity=severity,
            category=category,
            source=_pick(row, "source"),
            status=FindingStatus.VALID,
            raw=dict(row),
        )
        findings.append(finding)
    return findings
