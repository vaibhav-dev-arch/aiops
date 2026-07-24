"""Deterministic mock LLM for offline development and tests."""

from __future__ import annotations

from typing import Any

from app.providers.base import LLMProvider


class MockLLMProvider(LLMProvider):
    def generate(self, *, system: str, user: str, **kwargs: Any) -> str:
        # Produce a predictable TPRA narrative based on user prompt content
        findings_hint = ""
        if "finding" in user.lower() or "title" in user.lower():
            findings_hint = (
                "Based on the approved findings, several control gaps were identified "
                "across identity, cloud, and logging domains. "
            )
        return (
            f"[MOCK LLM DRAFT]\n"
            f"{findings_hint}"
            "This draft TPRA report summarizes third-party risk observations for human review. "
            "Critical and high severity items require remediation planning and residual risk acceptance. "
            "Medium items should be tracked through the vendor governance process.\n\n"
            "Executive Summary: The vendor assessment indicates partial alignment with expected "
            "security controls. Priority actions include enforcing MFA for privileged access, "
            "restricting public cloud storage exposure, and enabling comprehensive audit logging.\n\n"
            "Recommendations: Remediate critical findings within 30 days, validate compensating "
            "controls for exceptions, and schedule a follow-up reassessment after closure."
        )
