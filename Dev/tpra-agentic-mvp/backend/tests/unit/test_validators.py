"""Unit tests for validators."""

from app.agents.structured_findings.normalizer import normalize_rows
from app.agents.structured_findings.validators import validate_findings
from app.domain.enums import FindingStatus


def test_validate_required_and_severity():
    rows = [
        {"title": "OK", "severity": "high", "category": "identity"},
        {"title": "", "severity": "nope", "category": "identity"},
        {"title": "Weird cat", "severity": "low", "category": "unknown-cat"},
    ]
    findings = normalize_rows(rows)
    # empty title becomes "Untitled finding"
    findings, exceptions = validate_findings(findings)
    assert any(f.status == FindingStatus.EXCEPTION for f in findings)
    assert any(e.field == "severity" for e in exceptions)
    # unrecognized category alone is info-level from rules; title present so may still be valid
    weird = next(f for f in findings if f.title == "Weird cat")
    # category info exception still marks exception status because validate_finding_fields returns issues
    assert weird.status == FindingStatus.EXCEPTION
