"""Map findings to TPRA report template sections."""

from __future__ import annotations

from typing import Any

from app.domain.models import Finding

SECTION_MAP = {
    "identity": "Identity & Access Management",
    "cloud": "Cloud Security",
    "network": "Network Security",
    "logging": "Logging & Monitoring",
    "application": "Application Security",
    "data": "Data Protection",
    "governance": "Governance & Compliance",
    "general": "General Observations",
}


def map_findings_to_sections(findings: list[Finding]) -> dict[str, list[dict[str, Any]]]:
    sections: dict[str, list[dict[str, Any]]] = {name: [] for name in SECTION_MAP.values()}
    for f in findings:
        section = SECTION_MAP.get(f.category, SECTION_MAP["general"])
        sections.setdefault(section, []).append(f.model_dump(mode="json"))
    # Drop empty sections for cleaner reports
    return {k: v for k, v in sections.items() if v}
