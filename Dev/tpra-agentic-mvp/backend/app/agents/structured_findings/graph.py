"""UC1 Structured Findings Package Agent workflow."""

from __future__ import annotations

from typing import Any

from app.agents.graph import StopWorkflow, Workflow
from app.agents.structured_findings import package_builder, parsers
from app.agents.structured_findings.normalizer import normalize_rows
from app.agents.structured_findings.validators import validate_findings
from app.core.exceptions import ValidationError
from app.domain.models import AuditEvent
from app.services.authz import require_permission


def _validate(state: dict[str, Any]) -> None:
    if not state.get("files"):
        raise ValidationError("UC1 requires at least one input findings file")


def _authorize(state: dict[str, Any]) -> None:
    require_permission(state["user"], "agent:run")


def _load_files(state: dict[str, Any]) -> None:
    state["loaded_files"] = list(state.get("files") or [])


def _detect_types(state: dict[str, Any]) -> None:
    detected = []
    for item in state["loaded_files"]:
        name = item["record"].filename.lower()
        if name.endswith(".csv"):
            kind = "csv"
        elif name.endswith(".json"):
            kind = "json"
        elif name.endswith((".xlsx", ".xls")):
            kind = "xlsx"
        elif name.endswith(".docx"):
            kind = "docx"
        else:
            kind = "unknown"
        detected.append({"file_id": item["record"].id, "filename": item["record"].filename, "type": kind})
    state["detected_types"] = detected


def _extract_content(state: dict[str, Any]) -> None:
    rows: list[dict[str, Any]] = []
    for item in state["loaded_files"]:
        parsed = parsers.parse_bytes(item["data"], item["record"].filename)
        rows.extend(parsed)
    if not rows:
        raise StopWorkflow("No findings extracted from input files", status="failed")
    state["raw_rows"] = rows


def _normalize(state: dict[str, Any]) -> None:
    state["findings"] = normalize_rows(state["raw_rows"])


def _validate_fields(state: dict[str, Any]) -> None:
    findings, exceptions = validate_findings(state["findings"])
    state["findings"] = findings
    state["exceptions"] = exceptions


def _capture_reviewer_log(state: dict[str, Any]) -> None:
    state["reviewer_log_ready"] = True


def _build_package(state: dict[str, Any]) -> None:
    findings = state["findings"]
    file_service = state["file_service"]
    user = state["user"]
    workspace_id = state["workspace_id"]
    output_ids: list[str] = []

    xlsx = package_builder.build_structured_findings_xlsx(findings)
    csv_bytes = package_builder.build_structured_findings_csv(findings)
    rec = file_service.upload(
        workspace_id=workspace_id,
        filename="structured_findings.xlsx",
        data=xlsx,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        user=user,
        tags=["uc1", "package"],
    )
    output_ids.append(rec.id)
    rec2 = file_service.upload(
        workspace_id=workspace_id,
        filename="structured_findings.csv",
        data=csv_bytes,
        content_type="text/csv",
        user=user,
        tags=["uc1", "package"],
    )
    output_ids.append(rec2.id)
    state["package_file_ids"] = output_ids
    state.setdefault("output_file_ids", []).extend(output_ids)


def _exception_report(state: dict[str, Any]) -> None:
    exceptions = state.get("exceptions") or []
    payload = package_builder.build_exceptions_json(exceptions)
    rec = state["file_service"].upload(
        workspace_id=state["workspace_id"],
        filename="exceptions.json",
        data=payload,
        content_type="application/json",
        user=state["user"],
        tags=["uc1", "exceptions"],
    )
    state.setdefault("output_file_ids", []).append(rec.id)
    state["exceptions_file_id"] = rec.id


def _reviewer_log_output(state: dict[str, Any]) -> None:
    payload = package_builder.build_reviewer_log_csv(state["findings"])
    rec = state["file_service"].upload(
        workspace_id=state["workspace_id"],
        filename="reviewer_log.csv",
        data=payload,
        content_type="text/csv",
        user=state["user"],
        tags=["uc1", "reviewer_log"],
    )
    state.setdefault("output_file_ids", []).append(rec.id)
    state["reviewer_log_file_id"] = rec.id


def _audit_log(state: dict[str, Any]) -> None:
    state["audit"].save(
        AuditEvent(
            workspace_id=state["workspace_id"],
            actor=state["user"].user_id,
            action="uc1.complete",
            resource_type="run",
            resource_id=state["run_id"],
            details=package_builder.package_summary(state["findings"], state.get("exceptions") or []),
        )
    )


def _respond(state: dict[str, Any]) -> None:
    summary = package_builder.package_summary(state["findings"], state.get("exceptions") or [])
    state["response"] = {
        "agent": "uc1_structured_findings",
        "summary": summary,
        "findings": [f.model_dump(mode="json") for f in state["findings"]],
        "exceptions": [e.model_dump(mode="json") for e in state.get("exceptions") or []],
        "output_file_ids": state.get("output_file_ids", []),
    }


def build_uc1_workflow() -> Workflow:
    wf = Workflow(name="uc1_structured_findings")
    wf.add("validate", _validate)
    wf.add("authorize", _authorize)
    wf.add("load_files", _load_files)
    wf.add("detect_types", _detect_types)
    wf.add("extract_content", _extract_content)
    wf.add("normalize_findings", _normalize)
    wf.add("validate_fields", _validate_fields)
    wf.add("capture_reviewer_log", _capture_reviewer_log)
    wf.add("build_package", _build_package)
    wf.add("exception_report", _exception_report)
    wf.add("reviewer_log_output", _reviewer_log_output)
    wf.add("audit_log", _audit_log)
    wf.add("respond", _respond)
    return wf


def run_uc1(ctx: dict[str, Any]) -> dict[str, Any]:
    state = dict(ctx)
    state.setdefault("output_file_ids", [])
    state.setdefault("step_traces", [])
    build_uc1_workflow().run(state)
    return {
        "response": state.get("response", {}),
        "output_file_ids": state.get("output_file_ids", []),
        "step_traces": state.get("step_traces", []),
    }
