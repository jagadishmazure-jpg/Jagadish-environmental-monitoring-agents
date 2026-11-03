"""Measurement over synthetic event streams: prediction lead time
and false-alarm rate, computed only from matched predictions."""

from __future__ import annotations

from dataclasses import dataclass

from environmental_monitoring.models import Prediction, SyntheticEvent


@dataclass
class MeasurementResult:
    predictions: int
    matched: int
    false_alarms: int
    false_alarm_rate: float
    mean_lead_minutes: float | None
    detection_rate: float


class Measurement:
    @staticmethod
    def evaluate(predictions: list[Prediction], events: list[SyntheticEvent],
                 horizon: int = 240) -> MeasurementResult:
        leads: list[int] = []
        matched_events: set[str] = set()
        false_alarms = 0
        for prediction in predictions:
            match = None
            for event in events:
                if (event.region == prediction.region
                        and 0 <= event.onset_minute - prediction.issued_at <= horizon):
                    match = event
                    break
            if match is None:
                false_alarms += 1
            else:
                matched_events.add(match.event_id)
                leads.append(prediction.lead_minutes(match.onset_minute))
        total = len(predictions)
        mean_lead = (sum(leads) / len(leads)) if leads else None
        return MeasurementResult(
            predictions=total,
            matched=len(matched_events),
            false_alarms=false_alarms,
            false_alarm_rate=(false_alarms / total) if total else 0.0,
            mean_lead_minutes=mean_lead,
            detection_rate=(len(matched_events) / len(events)) if events else 0.0,
        )
