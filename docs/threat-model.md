# Threat model

## Risks considered

- **False escalation (spoofed or faulty sensor):** mitigated by the
  distinct-source correlation rule and the human gate; a single
  compromised feed cannot escalate on its own.
- **Gate bypass:** tested paths include bypass (no approval),
  absent approval, expired, mis-scoped, wrong-person, and reused
  approvals — all raise instead of escalating.
- **Ambiguous authorisation:** "yes, wait, no" and other
  non-exact consent are rejected as ambiguous, never treated as yes.
- **Audit tampering:** hash chaining makes a changed or deleted
  middle entry fail verification (tested).
- **PII leakage into logs:** redaction covers phone, SSN, card
  numbers, and email addresses (tested).
- **Cost overrun from bad inputs:** budget inputs reject negatives.

## Out of scope

This is a synthetic demo with no network, no real sensors, and no
real alerting channel. A production system would additionally need
authenticated sensor feeds, operator identity verification, and
rate-limited, audited external notification paths.
