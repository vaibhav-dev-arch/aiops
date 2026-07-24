"""Build UC1 output package artifacts."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from openpyxl import Workbook

from app.domain.models import ExceptionRecord, Finding


def build_structured_findings_csv(findings: list[Finding]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["id", "title", "description", "severity", "category", "source", "status"],
    )
    writer.writeheader()
    for f in findings:
        writer.writerow(
            {
                "id": f.id,
                "title": f.title,
                "description": f.description,
                "severity": f.severity,
                "category": f.category,
                "source": f.source,
                "status": f.status.value if hasattr(f.status, "value") else f.status,
            }
        )
    return buf.getvalue().encode("utf-8")


def build_structured_findings_xlsx(findings: list[Finding]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Findings"
    headers = ["id", "title", "description", "severity", "category", "source", "status"]
    ws.append(headers)
    for f in findings:
        ws.append(
            [
                f.id,
                f.title,
                f.description,
                f.severity,
                f.category,
                f.source,
                f.status.value if hasattr(f.status, "value") else f.status,
            ]
        )
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def build_exceptions_json(exceptions: list[ExceptionRecord]) -> bytes:
    payload = [e.model_dump(mode="json") for e in exceptions]
    return json.dumps(payload, indent=2).encode("utf-8")


def build_reviewer_log_csv(findings: list[Finding]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["finding_id", "title", "status", "decision", "comment"],
    )
    writer.writeheader()
    for f in findings:
        writer.writerow(
            {
                "finding_id": f.id,
                "title": f.title,
                "status": f.status.value if hasattr(f.status, "value") else f.status,
                "decision": "",
                "comment": "",
            }
        )
    return buf.getvalue().encode("utf-8")


def package_summary(findings: list[Finding], exceptions: list[ExceptionRecord]) -> dict[str, Any]:
    return {
        "finding_count": len(findings),
        "exception_count": len(exceptions),
        "by_severity": _count_by(findings, "severity"),
        "by_status": _count_by(findings, "status"),
    }


def _count_by(findings: list[Finding], attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for f in findings:
        key = getattr(f, attr)
        key_s = key.value if hasattr(key, "value") else str(key)
        counts[key_s] = counts.get(key_s, 0) + 1
    return counts
