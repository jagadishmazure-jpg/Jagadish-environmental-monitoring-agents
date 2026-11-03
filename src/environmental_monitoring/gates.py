"""Human gate for alert triage.

Alerts are NEVER auto-escalated to external action. Escalation needs
a named-person, single-use, scoped, expiring approval whose consent
is an unambiguous "yes". Low-confidence alerts, ambiguous or
self-contradicting consent ("yes, wait, no"), expired, mis-scoped,
or already-used approvals are all rejected, and bypassing the gate
raises instead of escalating.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from environmental_monitoring.models import Alert, Approval

MIN_CONFIDENCE = 0.65


class GateError(Exception):
    pass


class AmbiguousConsent(GateError):
    pass


class LowConfidence(GateError):
    pass


class ExpiredApproval(GateError):
    pass


class ApprovalMismatch(GateError):
    pass


class ApprovalUsed(GateError):
    pass


@dataclass(frozen=True)
class Escalation:
    alert_id: str
    approver: str
    scope: str
    at_minute: int


class HumanGate:
    def __init__(self) -> None:
        self._approvals: dict[str, Approval] = {}

    def request(self, approver: str, alert: Alert, scope: str,
                consent: str, now: int, ttl: int = 60) -> Approval:
        """Create an approval. Raises on every invalid shape so that a
        bad approval can never exist to be used later."""
        if not approver or not approver.strip():
            raise GateError("approver must be a named person")
        if consent.strip().lower() != "yes":
            raise AmbiguousConsent(
                "consent must be an unambiguous 'yes'; "
                "hesitation or contradiction is not approval")
        if alert.prediction.confidence < MIN_CONFIDENCE:
            raise LowConfidence(
                f"confidence {alert.prediction.confidence} below "
                f"gate floor {MIN_CONFIDENCE}")
        approval = Approval(approver.strip(), alert.alert_id, scope,
                            now, now + ttl)
        self._approvals[alert.alert_id] = approval
        return approval

    def reject(self, alert: Alert) -> Alert:
        alert.status = "rejected"
        return alert

    def escalate(self, alert: Alert, approval: Approval | None,
                 approver: str, scope: str, now: int) -> Escalation:
        """Escalate only with a live, matching, unused approval."""
        if approval is None:
            raise GateError("escalation without approval is blocked")
        if approval.alert_id != alert.alert_id:
            raise ApprovalMismatch("approval is for a different alert")
        if approval.approver != approver:
            raise ApprovalMismatch("approval belongs to another person")
        if approval.scope != scope:
            raise ApprovalMismatch("approval scope does not match")
        if approval.consumed:
            raise ApprovalUsed("approval is single-use and already spent")
        if now > approval.expires_at:
            raise ExpiredApproval("approval has expired")
        self._approvals[alert.alert_id] = replace(approval, consumed=True)
        alert.status = "escalated"
        return Escalation(alert.alert_id, approver, scope, now)
