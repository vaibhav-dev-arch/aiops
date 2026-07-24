"""Minimal sequential state-graph workflow engine."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class StopWorkflow(Exception):
    """Short-circuit remaining steps."""

    def __init__(self, message: str = "stopped", *, status: str = "stopped"):
        super().__init__(message)
        self.message = message
        self.status = status


StepFn = Callable[[dict[str, Any]], None]


@dataclass
class Workflow:
    name: str
    steps: list[tuple[str, StepFn]] = field(default_factory=list)

    def add(self, name: str, fn: StepFn) -> "Workflow":
        self.steps.append((name, fn))
        return self

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        traces: list[dict[str, Any]] = state.setdefault("step_traces", [])
        for step_name, fn in self.steps:
            started = time.perf_counter()
            trace: dict[str, Any] = {"name": step_name, "status": "running"}
            try:
                fn(state)
                trace["status"] = "succeeded"
            except StopWorkflow as stop:
                trace["status"] = stop.status
                trace["message"] = stop.message
                trace["duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
                traces.append(trace)
                state["stopped"] = True
                state["stop_message"] = stop.message
                break
            except Exception as exc:  # noqa: BLE001
                trace["status"] = "failed"
                trace["error"] = str(exc)
                trace["duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
                traces.append(trace)
                raise
            else:
                trace["duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
                traces.append(trace)
        return state
