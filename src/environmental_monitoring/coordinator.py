"""PredictionCoordinator: correlation is the confirmation rule.

A prediction is issued only when at least two *distinct* sources have
signalled the same region inside the correlation window and their
combined strength reaches 1.0. A lone spike, however strong, stays on
the watch list: it is held back, not predicted and never escalated.
This is why correlated signals raise lead time in practice -- two
moderate signals confirm each other early, while a single-source rule
would have to wait for one sensor to grow strong enough alone.
"""

from __future__ import annotations

from environmental_monitoring.models import Prediction, Signal

WINDOW_MINUTES = 180
COMBINED_THRESHOLD = 1.0


def _severity(confidence: float) -> str:
    if confidence >= 0.80:
        return "high"
    if confidence >= 0.65:
        return "medium"
    return "low"


class PredictionCoordinator:
    def __init__(self, window: int = WINDOW_MINUTES,
                 threshold: float = COMBINED_THRESHOLD) -> None:
        self.window = window
        self.threshold = threshold
        self._pending: dict[str, list[Signal]] = {}
        self.predictions: list[Prediction] = []
        self._counter = 0

    def ingest(self, signal: Signal) -> Prediction | None:
        pending = [s for s in self._pending.get(signal.region, [])
                   if signal.at_minute - s.at_minute <= self.window]
        pending.append(signal)
        self._pending[signal.region] = pending
        sources = {s.source for s in pending}
        combined = sum(s.strength for s in pending)
        if len(sources) >= 2 and combined >= self.threshold:
            self._counter += 1
            confidence = min(0.95, combined / 2.0 + 0.10 * (len(sources) - 1))
            prediction = Prediction(
                prediction_id=f"P{self._counter:03d}",
                region=signal.region,
                issued_at=signal.at_minute,
                sources=tuple(sorted(sources)),
                confidence=round(confidence, 3),
                severity=_severity(confidence),
            )
            self.predictions.append(prediction)
            self._pending[signal.region] = []
            return prediction
        return None

    def held_watch(self) -> list[Signal]:
        """Single-source signals currently held back, not predicted."""
        out: list[Signal] = []
        for signals in self._pending.values():
            out.extend(signals)
        return out
