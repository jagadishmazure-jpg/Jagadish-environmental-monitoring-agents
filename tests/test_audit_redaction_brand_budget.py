"""Audit chain, PII redaction, brand guard, and budget-guard tests."""

import pytest

from environmental_monitoring.audit import AuditLog
from environmental_monitoring.brand import blocklist_size, check_text
from environmental_monitoring.budget import estimate_cost, validate_non_negative
from environmental_monitoring.redaction import redact_text


def test_audit_chain_verifies():
    log = AuditLog()
    log.append({"signal": "seismic"})
    log.append({"prediction": "P001"})
    assert log.verify() is True
    assert len(log.entries) == 2


def test_audit_tamper_breaks_verification():
    log = AuditLog()
    log.append({"signal": "seismic"})
    log.append({"prediction": "P001"})
    log.entries[0].payload["signal"] = "satellite"
    assert log.verify() is False


def test_audit_hash_links_entries():
    log = AuditLog()
    first = log.append({"a": 1})
    second = log.append({"b": 2})
    assert second.prev_hash == first.entry_hash


def test_redact_email():
    out = redact_text("contact duty@example.org for details")
    assert "duty@example.org" not in out
    assert "[REDACTED:EMAIL]" in out


def test_redact_card_number():
    out = redact_text("card 4111 1111 1111 1111 on file")
    assert "4111" not in out
    assert "[REDACTED:CARD]" in out


def test_redact_card_number_dashed():
    out = redact_text("card 5500-0055-5555-5559 on file")
    assert "5500" not in out
    assert "[REDACTED:CARD]" in out


def test_redact_phone():
    out = redact_text("call +1 555-123-4567 now")
    assert "555-123-4567" not in out
    assert "[REDACTED:PHONE]" in out


def test_redact_ssn():
    out = redact_text("ssn 123-45-6789 in note")
    assert "123-45-6789" not in out
    assert "[REDACTED:SSN]" in out


def test_redact_leaves_clean_text_alone():
    text = "correlated seismic and satellite signals in North Basin"
    assert redact_text(text) == text


def test_brand_blocklist_non_empty():
    assert blocklist_size() > 0


def test_brand_check_flags_blocked_and_allows_fictional():
    assert check_text("this uses fablefield today") is True
    assert check_text("Sorrelmere Environmental monitoring report") is False


def test_budget_rejects_negative():
    with pytest.raises(ValueError):
        validate_non_negative(-5.0, "sensors")


def test_budget_zero_is_allowed():
    assert validate_non_negative(0.0, "sensors") == 0.0


def test_cost_estimate_sums_and_rejects_negative_line():
    assert estimate_cost({"sensors": 1200.0, "compute": 300.0}) == 1500.0
    with pytest.raises(ValueError):
        estimate_cost({"sensors": 1200.0, "compute": -1.0})
