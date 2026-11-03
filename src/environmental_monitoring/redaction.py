"""PII redaction for log and alert text. The checklist covers phone
numbers, SSNs, card numbers, and email addresses -- not just phone/SSN."""

from __future__ import annotations

import re

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_PHONE = re.compile(r"\b(?:\+?1[-. ]?)?(?:\(?\d{3}\)?[-. ]?)\d{3}[-. ]?\d{4}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def _card_has_digits(match: re.Match) -> str:
    digits = re.sub(r"\D", "", match.group(0))
    if 13 <= len(digits) <= 19:
        return "[REDACTED:CARD]"
    return match.group(0)


def redact_text(text: str) -> str:
    text = _EMAIL.sub("[REDACTED:EMAIL]", text)
    text = _SSN.sub("[REDACTED:SSN]", text)
    text = _CARD.sub(_card_has_digits, text)
    text = _PHONE.sub("[REDACTED:PHONE]", text)
    return text
