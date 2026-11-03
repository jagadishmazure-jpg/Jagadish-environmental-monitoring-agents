"""Demo pipeline over a synthetic stream (fictional regions, no real
events, no real sensor data).

Stream: 5 true events, each preceded by a seismic signal 120 minutes
before onset and a satellite signal 90 minutes before onset, so the
coordinator confirms at onset-90 (lead time 90). One correlated pair
with no following event is the single false alarm. Two lone spikes
are held back and never become predictions.
"""

from __future__ import annotations

from environmental_monitoring.agents import (
    SatelliteAgent,
    SeismicAgent,
    WeatherAgent,
)
from environmental_monitoring.audit import AuditLog
from environmental_monitoring.budget import estimate_cost
from environmental_monitoring.coordinator import PredictionCoordinator
from environmental_monitoring.gates import HumanGate
from environmental_monitoring.measurement import Measurement
from environmental_monitoring.models import Alert, SyntheticEvent
from environmental_monitoring.response import build_plan, execute_plan

NORTH = "Sorrelmere North Basin"
EAST = "Sorrelmere East Ridge"


def run_demo() -> dict:
    seismic, satellite, weather = SeismicAgent(), SatelliteAgent(), WeatherAgent()
    coordinator = PredictionCoordinator()
    audit = AuditLog()
    events = [
        SyntheticEvent(f"E{i+1}", NORTH if i % 2 == 0 else EAST, onset, "tremor")
        for i, onset in enumerate([600, 1200, 1800, 2400, 3000])
    ]
    for event in events:
        for signal in (
            seismic.observe(event.region, event.onset_minute - 120, 4.0),
            satellite.observe(event.region, event.onset_minute - 90, 0.55),
            weather.observe(event.region, event.onset_minute - 60, 20.0),
        ):
            if signal is None:
                continue
            prediction = coordinator.ingest(signal)
            audit.append({"signal": signal.source, "region": signal.region,
                          "at": signal.at_minute})
            if prediction is not None:
                audit.append({"prediction": prediction.prediction_id,
                              "region": prediction.region,
                              "confidence": prediction.confidence})
    # False alarm: a correlated pair with no event behind it.
    for signal in (
        seismic.observe(NORTH, 3500, 4.0),
        satellite.observe(NORTH, 3530, 0.55),
    ):
        prediction = coordinator.ingest(signal)
        audit.append({"signal": signal.source, "region": signal.region,
                      "at": signal.at_minute})
        if prediction is not None:
            audit.append({"prediction": prediction.prediction_id,
                          "region": prediction.region,
                          "confidence": prediction.confidence})
    # Lone spikes in different regions: each stays single-source, so
    # both are held back and never become predictions.
    for signal in (
        seismic.observe(EAST, 4000, 5.0),
        satellite.observe(NORTH, 4100, 0.80),
    ):
        coordinator.ingest(signal)
        audit.append({"signal": signal.source, "region": signal.region,
                      "at": signal.at_minute})

    measurement = Measurement.evaluate(coordinator.predictions, events)
    alerts = [Alert(f"A{i+1}", p, explanation="correlated signals")
              for i, p in enumerate(coordinator.predictions)]
    gate = HumanGate()
    escalated = 0
    plans_executed = 0
    first = alerts[0]
    approval = gate.request("Duty Officer A. Reyes", first,
                            "notify-region-team", "yes", now=first.prediction.issued_at)
    escalation = gate.escalate(first, approval, "Duty Officer A. Reyes",
                               "notify-region-team", now=first.prediction.issued_at + 5)
    escalated += 1
    plan = build_plan(first)
    execute_plan(plan, escalation)
    plans_executed += 1
    audit.append({"escalated": first.alert_id, "approver": "Duty Officer A. Reyes"})
    return {
        "events": len(events),
        "predictions": measurement.predictions,
        "matched": measurement.matched,
        "false_alarms": measurement.false_alarms,
        "false_alarm_rate": round(measurement.false_alarm_rate, 4),
        "mean_lead_minutes": measurement.mean_lead_minutes,
        "detection_rate": measurement.detection_rate,
        "held_back": len(coordinator.held_watch()),
        "alerts": len(alerts),
        "escalated": escalated,
        "plans_executed": plans_executed,
        "audit_entries": len(audit.entries),
        "audit_verified": audit.verify(),
        "budget_demo": estimate_cost({"sensors": 1200.0, "compute": 300.0}),
    }
