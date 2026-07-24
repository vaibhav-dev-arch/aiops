"""UC2 Draft TPRA Report Agent workflow."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from app.agents.draft_report.report_builder import build_report_docx
from app.agents.draft_report.template_mapper import map_findings_to_sections
from app.agents.graph import Workflow
from app.agents.structured_findings.parsers import parse_bytes
from app.core.exceptions import ValidationError
from app.domain.enums import FindingStatus
from app.domain.models import AuditEvent, Finding
from app.services.authz import require_permission


def _read_prompt(rel: str, default: str) -> str:
    from app.core.config import get_settings

    path = get_settings().prompts_root / rel if get_settings().prompts_root else None
    if path and path.exists():
        return path.read_text(encoding="utf-8")
    return default


def _validate(state: dict[str, Any]) -> None:
    if not state.get("files"):
        raise ValidationError("UC2 requires an approved findings package input")


def _authorize(state: dict[str, Any]) -> None:
    require_permission(state["user"], "agent:run")


def _load_package(state: dict[str, Any]) -> None:
    from app.domain.models import new_id

    findings: list[Finding] = []
    for item in state["files"]:
        name = item["record"].filename.lower()
        data = item["data"]
        if name.endswith(".json"):
            payload = json.loads(data.decode("utf-8"))
            rows = payload.get("findings", payload if isinstance(payload, list) else [])
            for row in rows:
                if isinstance(row, dict):
                    if "id" not in row or not row["id"]:
                        row = {**row, "id": new_id("f")}
                    findings.append(Finding.model_validate(row))
                else:
                    findings.append(Finding(title=str(row)))
        else:
            rows = parse_bytes(data, item["record"].filename)
            for row in rows:
                status = row.get("status", FindingStatus.VALID.value)
                findings.append(
                    Finding(
                        id=row.get("id") or row.get("finding_id") or new_id("f"),
                        title=row.get("title") or "Untitled",
                        description=row.get("description") or "",
                        severity=(row.get("severity") or "medium").lower(),
                        category=(row.get("category") or "general").lower(),
                        source=row.get("source") or "",
                        status=(
                            FindingStatus(status)
                            if status in FindingStatus._value2member_map_
                            else FindingStatus.VALID
                        ),
                        raw=row,
                    )
                )
    state["findings"] = findings


def _check_approvals(state: dict[str, Any]) -> None:
    findings: list[Finding] = state["findings"]
    # Treat valid / approved as eligible; exception findings flagged as missing approval context
    approved = []
    pending = []
    for f in findings:
        if f.status in (FindingStatus.APPROVED, FindingStatus.VALID):
            approved.append(f)
        else:
            pending.append(f)
    state["approved_findings"] = approved
    state["pending_findings"] = pending


def _load_template(state: dict[str, Any]) -> None:
    state["template_name"] = "TPRA Draft Report Template v1"


def _map_sections(state: dict[str, Any]) -> None:
    state["sections"] = map_findings_to_sections(state["approved_findings"])


def _populate_report(state: dict[str, Any]) -> None:
    system = _read_prompt(
        "draft_report/v1/system.md",
        "You are a TPRA report drafting assistant. Write clear, professional narrative sections.",
    )
    findings_json = json.dumps([f.model_dump(mode="json") for f in state["approved_findings"]], indent=2)
    user = _read_prompt(
        "draft_report/v1/user.md",
        "Draft a TPRA narrative using these approved findings:\n{{findings}}",
    ).replace("{{findings}}", findings_json)
    narrative = state["providers"].llm.generate(system=system, user=user)
    state["narrative"] = narrative


def _detect_missing_inputs(state: dict[str, Any]) -> None:
    missing: list[str] = []
    if not state.get("approved_findings"):
        missing.append("No approved/valid findings available for report generation")
    for f in state.get("pending_findings") or []:
        missing.append(f"Finding {f.id} ({f.title}) not approved — status={f.status.value}")
    required_cats = {"identity", "cloud", "logging"}
    present = {f.category for f in state.get("approved_findings") or []}
    for cat in sorted(required_cats - present):
        missing.append(f"No findings provided for expected category: {cat}")
    state["missing_inputs"] = missing


def _missing_input_report(state: dict[str, Any]) -> None:
    text = "\n".join(state.get("missing_inputs") or []) or "None"
    rec = state["file_service"].upload(
        workspace_id=state["workspace_id"],
        filename="missing_inputs.txt",
        data=text.encode("utf-8"),
        content_type="text/plain",
        user=state["user"],
        tags=["uc2", "missing_inputs"],
    )
    state.setdefault("output_file_ids", []).append(rec.id)


def _summary(state: dict[str, Any]) -> None:
    docx = build_report_docx(
        title="Draft Third Party Risk Assessment Report",
        narrative=state.get("narrative") or "",
        sections=state.get("sections") or {},
        missing_inputs=state.get("missing_inputs") or [],
    )
    rec = state["file_service"].upload(
        workspace_id=state["workspace_id"],
        filename="draft_tpra_report.docx",
        data=docx,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        user=state["user"],
        tags=["uc2", "report"],
    )
    state.setdefault("output_file_ids", []).append(rec.id)
    state["report_file_id"] = rec.id
    state["summary"] = {
        "approved_count": len(state.get("approved_findings") or []),
        "pending_count": len(state.get("pending_findings") or []),
        "section_count": len(state.get("sections") or {}),
        "missing_input_count": len(state.get("missing_inputs") or []),
        "report_file_id": rec.id,
    }


def _audit_log(state: dict[str, Any]) -> None:
    state["audit"].save(
        AuditEvent(
            workspace_id=state["workspace_id"],
            actor=state["user"].user_id,
            action="uc2.complete",
            resource_type="run",
            resource_id=state["run_id"],
            details=state.get("summary") or {},
        )
    )


def _respond(state: dict[str, Any]) -> None:
    state["response"] = {
        "agent": "uc2_draft_report",
        "summary": state.get("summary") or {},
        "narrative_preview": (state.get("narrative") or "")[:500],
        "missing_inputs": state.get("missing_inputs") or [],
        "output_file_ids": state.get("output_file_ids", []),
    }


def build_uc2_workflow() -> Workflow:
    wf = Workflow(name="uc2_draft_report")
    wf.add("validate", _validate)
    wf.add("authorize", _authorize)
    wf.add("load_package", _load_package)
    wf.add("check_approvals", _check_approvals)
    wf.add("load_template", _load_template)
    wf.add("map_sections", _map_sections)
    wf.add("populate_report", _populate_report)
    wf.add("detect_missing_inputs", _detect_missing_inputs)
    wf.add("missing_input_report", _missing_input_report)
    wf.add("summary", _summary)
    wf.add("audit_log", _audit_log)
    wf.add("respond", _respond)
    return wf


def run_uc2(ctx: dict[str, Any]) -> dict[str, Any]:
    state = dict(ctx)
    state.setdefault("output_file_ids", [])
    state.setdefault("step_traces", [])
    build_uc2_workflow().run(state)
    return {
        "response": state.get("response", {}),
        "output_file_ids": state.get("output_file_ids", []),
        "step_traces": state.get("step_traces", []),
    }
