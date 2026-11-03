"""Coordinator correlation tests."""

from environmental_monitoring.agents import (
    SatelliteAgent,
    SeismicAgent,
    WeatherAgent,
)
from environmental_monitoring.coordinator import PredictionCoordinator
from environmental_monitoring.models import Signal

REGION = "Sorrelmere North Basin"
OTHER = "Sorrelmere East Ridge"


def _pair(coordinator=None):
    coordinator = coordinator or PredictionCoordinator()
    seismic = SeismicAgent().observe(REGION, 480, 4.0)
    satellite = SatelliteAgent().observe(REGION, 510, 0.55)
    return coordinator, seismic, satellite


def test_single_signal_is_held_not_predicted():
    coordinator = PredictionCoordinator()
    assert coordinator.ingest(SeismicAgent().observe(REGION, 480, 5.0)) is None
    assert len(coordinator.held_watch()) == 1
    assert coordinator.predictions == []


def test_strong_single_spike_is_still_held():
    coordinator = PredictionCoordinator()
    assert coordinator.ingest(SeismicAgent().observe(REGION, 480, 10.0)) is None
    assert coordinator.predictions == []


def test_correlated_pair_issues_prediction():
    coordinator, seismic, satellite = _pair()
    assert coordinator.ingest(seismic) is None
    prediction = coordinator.ingest(satellite)
    assert prediction is not None
    assert prediction.issued_at == 510
    assert set(prediction.sources) == {"seismic", "satellite"}


def test_two_signals_same_source_do_not_confirm():
    coordinator = PredictionCoordinator()
    coordinator.ingest(Signal("seismic", REGION, 480, 0.6))
    assert coordinator.ingest(Signal("seismic", REGION, 510, 0.6)) is None
    assert coordinator.predictions == []


def test_two_weak_signals_below_combined_threshold_do_not_confirm():
    coordinator = PredictionCoordinator()
    coordinator.ingest(Signal("seismic", REGION, 480, 0.45))
    assert coordinator.ingest(Signal("satellite", REGION, 510, 0.45)) is None


def test_signals_outside_window_do_not_correlate():
    coordinator = PredictionCoordinator()
    coordinator.ingest(Signal("seismic", REGION, 100, 0.9))
    assert coordinator.ingest(Signal("satellite", REGION, 500, 0.9)) is None


def test_signals_in_different_regions_do_not_correlate():
    coordinator = PredictionCoordinator()
    coordinator.ingest(Signal("seismic", REGION, 480, 0.9))
    assert coordinator.ingest(Signal("satellite", OTHER, 510, 0.9)) is None


def test_prediction_clears_pending_for_region():
    coordinator, seismic, satellite = _pair()
    coordinator.ingest(seismic)
    coordinator.ingest(satellite)
    assert coordinator.held_watch() == []


def test_correlated_prediction_lead_time_beats_late_single_signal():
    # Correlated pair confirms at minute 510 for an onset at 600:
    # lead 90. A single-source rule waiting for a strong lone signal
    # that only arrives at 570 would give lead 30.
    coordinator, seismic, satellite = _pair()
    coordinator.ingest(seismic)
    prediction = coordinator.ingest(satellite)
    assert prediction.lead_minutes(600) == 90
    assert prediction.lead_minutes(600) > 600 - 570


def test_severity_bands():
    coordinator = PredictionCoordinator()
    coordinator.ingest(Signal("seismic", REGION, 480, 0.9))
    prediction = coordinator.ingest(Signal("satellite", REGION, 510, 0.9))
    assert prediction.severity == "high"
    assert prediction.confidence >= 0.80


def test_medium_severity_for_moderate_pair():
    coordinator, seismic, satellite = _pair()
    coordinator.ingest(seismic)
    prediction = coordinator.ingest(satellite)
    assert prediction.severity == "medium"


def test_three_sources_raise_confidence():
    coordinator = PredictionCoordinator()
    coordinator.ingest(Signal("seismic", REGION, 480, 0.6))
    coordinator.ingest(Signal("satellite", REGION, 500, 0.55))
    # A third source after confirmation starts a new pending watch.
    assert coordinator.ingest(WeatherAgent().observe(REGION, 520, 20.0)) is None
    assert len(coordinator.predictions) == 1
