"""Human-gate tests: bypass, reject, absent, and edge paths."""

import pytest

from environmental_monitoring.gates import (
    AmbiguousConsent,
    ApprovalMismatch,
    ApprovalUsed,
    ExpiredApproval,
    GateError,
    HumanGate,
    LowConfidence,
)
from environmental_monitoring.models import Alert, Prediction

SCOPE = "notify-region-team"


def _alert(confidence=0.75, alert_id="A1"):
    prediction = Prediction("P001", "Sorrelmere North Basin", 510,
                            ("seismic", "satellite"), confidence, "medium")
    return Alert(alert_id, prediction)


def _approved(gate, alert, now=510):
    approval = gate.request("Duty Officer A. Reyes", alert, SCOPE, "yes", now=now)
    return approval


def test_valid_approval_escalates():
    gate, alert = HumanGate(), _alert()
    approval = _approved(gate, alert)
    escalation = gate.escalate(alert, approval, "Duty Officer A. Reyes", SCOPE, 515)
    assert alert.status == "escalated"
    assert escalation.approver == "Duty Officer A. Reyes"


def test_bypass_without_approval_is_blocked():
    gate, alert = HumanGate(), _alert()
    with pytest.raises(GateError):
        gate.escalate(alert, None, "Duty Officer A. Reyes", SCOPE, 515)
    assert alert.status == "pending"


def test_absent_approval_path_never_escalates():
    gate, alert = HumanGate(), _alert()
    # No request was ever made; escalating with a stranger object fails.
    with pytest.raises((GateError, ApprovalMismatch)):
        gate.escalate(alert, None, "Duty Officer A. Reyes", SCOPE, 515)


def test_explicit_rejection_marks_alert():
    gate, alert = HumanGate(), _alert()
    assert gate.reject(alert).status == "rejected"


def test_consent_no_is_rejected():
    gate, alert = HumanGate(), _alert()
    with pytest.raises(AmbiguousConsent):
        gate.request("Duty Officer A. Reyes", alert, SCOPE, "no", now=510)


def test_self_contradicting_consent_is_rejected():
    gate, alert = HumanGate(), _alert()
    with pytest.raises(AmbiguousConsent):
        gate.request("Duty Officer A. Reyes", alert, SCOPE, "yes, wait, no", now=510)


def test_hesitant_consent_is_rejected():
    gate, alert = HumanGate(), _alert()
    with pytest.raises(AmbiguousConsent):
        gate.request("Duty Officer A. Reyes", alert, SCOPE, "yes, wait", now=510)


def test_low_confidence_alert_cannot_be_approved():
    gate, alert = HumanGate(), _alert(confidence=0.60)
    with pytest.raises(LowConfidence):
        gate.request("Duty Officer A. Reyes", alert, SCOPE, "yes", now=510)


def test_unnamed_approver_is_rejected():
    gate, alert = HumanGate(), _alert()
    with pytest.raises(GateError):
        gate.request("   ", alert, SCOPE, "yes", now=510)


def test_expired_approval_is_rejected():
    gate, alert = HumanGate(), _alert()
    approval = _approved(gate, alert, now=510)  # expires at 570
    with pytest.raises(ExpiredApproval):
        gate.escalate(alert, approval, "Duty Officer A. Reyes", SCOPE, 571)


def test_approval_at_expiry_minute_still_valid():
    gate, alert = HumanGate(), _alert()
    approval = _approved(gate, alert, now=510)
    assert gate.escalate(alert, approval, "Duty Officer A. Reyes", SCOPE, 570)


def test_scope_mismatch_is_rejected():
    gate, alert = HumanGate(), _alert()
    approval = _approved(gate, alert)
    with pytest.raises(ApprovalMismatch):
        gate.escalate(alert, approval, "Duty Officer A. Reyes", "other-scope", 515)


def test_approver_mismatch_is_rejected():
    gate, alert = HumanGate(), _alert()
    approval = _approved(gate, alert)
    with pytest.raises(ApprovalMismatch):
        gate.escalate(alert, approval, "Someone Else", SCOPE, 515)


def test_approval_is_single_use():
    gate, alert = HumanGate(), _alert()
    approval = _approved(gate, alert)
    gate.escalate(alert, approval, "Duty Officer A. Reyes", SCOPE, 515)
    # The stored approval is now consumed; reusing the spent copy fails.
    from dataclasses import replace
    spent = replace(approval, consumed=True)
    with pytest.raises(ApprovalUsed):
        gate.escalate(alert, spent, "Duty Officer A. Reyes", SCOPE, 516)


def test_approval_for_other_alert_is_rejected():
    gate = HumanGate()
    first, second = _alert(alert_id="A1"), _alert(alert_id="A2")
    approval = _approved(gate, first)
    with pytest.raises(ApprovalMismatch):
        gate.escalate(second, approval, "Duty Officer A. Reyes", SCOPE, 515)
