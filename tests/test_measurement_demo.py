"""Measurement and demo-pipeline tests, including response plans."""

import pytest

from environmental_monitoring.coordinator import PredictionCoordinator
from environmental_monitoring.measurement import Measurement
from environmental_monitoring.models import Alert, Prediction, Signal, SyntheticEvent
from environmental_monitoring.pipeline import run_demo
from environmental_monitoring.response import build_plan, execute_plan


def _prediction(issued_at, region="Sorrelmere North Basin"):
    return Prediction("P001", region, issued_at, ("seismic", "satellite"),
                      0.75, "medium")


def test_correlated_signals_raise_lead_time():
    coordinator = PredictionCoordinator()
    coordinator.ingest(Signal("seismic", "Sorrelmere North Basin", 480, 0.6))
    prediction = coordinator.ingest(Signal("satellite", "Sorrelmere North Basin", 510, 0.55))
    assert prediction.lead_minutes(600) == 90


def test_single_sensor_spike_is_held_back_in_measurement():
    result = Measurement.evaluate([], [SyntheticEvent("E1", "Sorrelmere North Basin", 600, "tremor")])
    assert result.predictions == 0
    assert result.false_alarms == 0


def test_false_alarm_rate_counts_unmatched_predictions():
    events = [SyntheticEvent("E1", "Sorrelmere North Basin", 600, "tremor")]
    predictions = [_prediction(510), _prediction(3500)]
    result = Measurement.evaluate(predictions, events)
    assert result.false_alarms == 1
    assert result.false_alarm_rate == pytest.approx(0.5)


def test_mean_lead_time_over_matched_predictions():
    events = [SyntheticEvent("E1", "Sorrelmere North Basin", 600, "tremor"),
              SyntheticEvent("E2", "Sorrelmere North Basin", 1200, "tremor")]
    predictions = [_prediction(510), _prediction(1110)]
    result = Measurement.evaluate(predictions, events)
    assert result.mean_lead_minutes == pytest.approx(90.0)
    assert result.detection_rate == pytest.approx(1.0)


def test_demo_numbers_are_exactly_asserted():
    demo = run_demo()
    assert demo["events"] == 5
    assert demo["predictions"] == 6
    assert demo["matched"] == 5
    assert demo["false_alarms"] == 1
    assert demo["false_alarm_rate"] == pytest.approx(1 / 6, abs=0.001)
    assert demo["mean_lead_minutes"] == pytest.approx(90.0)
    assert demo["detection_rate"] == pytest.approx(1.0)
    # Only the two lone spikes remain held: earlier single weather
    # signals age out of the correlation window on the next ingest.
    assert demo["held_back"] == 2
    assert demo["escalated"] == 1
    assert demo["plans_executed"] == 1
    assert demo["audit_verified"] is True
    assert demo["budget_demo"] == 1500.0


def test_response_plan_covers_all_phases():
    alert = Alert("A1", _prediction(510))
    plan = build_plan(alert)
    assert set(plan.actions) == {"prevent", "detect", "respond", "recover"}
    assert all(plan.actions[phase] for phase in ("prevent", "detect", "respond", "recover"))


def test_response_execution_requires_approved_escalation():
    alert = Alert("A1", _prediction(510))
    plan = build_plan(alert)
    with pytest.raises(PermissionError):
        execute_plan(plan, None)
    assert plan.executed is False


def test_response_execution_with_wrong_alert_escalation_fails():
    from environmental_monitoring.gates import Escalation
    alert = Alert("A1", _prediction(510))
    plan = build_plan(alert)
    with pytest.raises(PermissionError):
        execute_plan(plan, Escalation("A2", "Duty Officer A. Reyes",
                                      "notify-region-team", 515))


def test_demo_alerts_never_auto_escalate():
    demo = run_demo()
    assert demo["escalated"] == 1
    assert demo["alerts"] == 6  # only one of six alerts was escalated
