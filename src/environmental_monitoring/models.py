"""Plain data types. Times are integer minutes on a synthetic clock."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Signal:
    """One agent's observation. ``strength`` is in [0, 1]; a single
    signal can never reach the coordinator's combined threshold of 1.0
    on its own, which is what holds single-sensor spikes back."""

    source: str  # "seismic" | "satellite" | "weather"
    region: str
    at_minute: int
    strength: float
    detail: str = ""


@dataclass(frozen=True)
class SyntheticEvent:
    """A ground-truth event in a synthetic stream (never a real event)."""

    event_id: str
    region: str
    onset_minute: int
    kind: str


@dataclass(frozen=True)
class Prediction:
    prediction_id: str
    region: str
    issued_at: int
    sources: tuple
    confidence: float
    severity: str  # "low" | "medium" | "high"

    def lead_minutes(self, onset_minute: int) -> int:
        return onset_minute - self.issued_at


@dataclass
class Alert:
    alert_id: str
    prediction: Prediction
    status: str = "pending"  # pending | escalated | rejected | stood_down
    explanation: str = ""


@dataclass(frozen=True)
class Approval:
    approver: str  # named person, never a role alone
    alert_id: str
    scope: str
    issued_at: int
    expires_at: int
    consumed: bool = False
