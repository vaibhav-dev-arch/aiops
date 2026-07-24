"""Unit tests for normalizer."""

from app.agents.structured_findings.normalizer import normalize_rows


def test_normalize_aliases_and_severity():
    rows = [
        {"Finding": "MFA Gap", "Risk": "H", "Domain": "identity", "Vendor": "v1", "Details": "missing MFA"},
        {"title": "MFA Gap", "severity": "high", "category": "identity"},  # duplicate title skipped
        {"name": "Open Bucket", "priority": "1", "area": "cloud", "source": "scan"},
    ]
    findings = normalize_rows(rows)
    assert len(findings) == 2
    assert findings[0].title == "MFA Gap"
    assert findings[0].severity == "high"
    assert findings[0].category == "identity"
    assert findings[0].source == "v1"
    assert findings[1].severity == "critical"
    assert findings[1].id.startswith("f-")
