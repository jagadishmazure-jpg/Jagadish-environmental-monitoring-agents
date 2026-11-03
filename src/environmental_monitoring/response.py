"""Response and remediation plans, covering prevent / detect /
respond / recover, plus governance and measurement hooks.

Plans are advisory until a human gate approves escalation: executing
without an approved escalation raises instead of acting.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from environmental_monitoring.gates import Escalation
from environmental_monitoring.models import Alert

_PHASES = ("prevent", "detect", "respond", "recover")


@dataclass
class ResponsePlan:
    alert_id: str
    severity: str
    actions: dict[str, list[str]] = field(default_factory=dict)
    executed: bool = False


def build_plan(alert: Alert) -> ResponsePlan:
    severity = alert.prediction.severity
    actions = {
        "prevent": [
            "Raise monitoring cadence for the affected region.",
            "Pre-position field crews and check sensor health.",
        ],
        "detect": [
            "Keep correlating incoming signals against this prediction.",
            "Log every new signal to the hash-chained audit trail.",
        ],
        "respond": [
            "Notify the duty officer through the human gate only.",
            "No external action until a named approval is granted.",
        ],
        "recover": [
            "Stand down monitoring cadence once the window closes.",
            "File the all-clear report with lead time and outcome.",
        ],
    }
    if severity == "high":
        actions["respond"].append("Escalate to the regional coordinator on approval.")
    return ResponsePlan(alert.alert_id, severity, actions)


def execute_plan(plan: ResponsePlan, escalation: Escalation | None) -> ResponsePlan:
    """Execution requires an approved escalation for this alert."""
    if escalation is None or escalation.alert_id != plan.alert_id:
        raise PermissionError("response requires an approved escalation")
    plan.executed = True
    return plan
