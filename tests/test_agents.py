"""Agent signal tests."""

from environmental_monitoring.agents import (
    SatelliteAgent,
    SeismicAgent,
    WeatherAgent,
)

REGION = "Sorrelmere North Basin"


def test_seismic_below_floor_is_silent():
    assert SeismicAgent().observe(REGION, 100, 2.9) is None


def test_seismic_at_floor_registers():
    signal = SeismicAgent().observe(REGION, 100, 3.0)
    assert signal is not None and signal.source == "seismic"


def test_seismic_strength_scales_with_magnitude():
    low = SeismicAgent().observe(REGION, 100, 4.0)
    high = SeismicAgent().observe(REGION, 100, 6.0)
    assert low.strength < high.strength


def test_seismic_strength_never_reaches_combined_threshold_alone():
    signal = SeismicAgent().observe(REGION, 100, 10.0)
    assert signal.strength < 1.0


def test_satellite_below_floor_is_silent():
    assert SatelliteAgent().observe(REGION, 100, 0.39) is None


def test_satellite_at_floor_registers():
    signal = SatelliteAgent().observe(REGION, 100, 0.40)
    assert signal is not None and signal.strength == 0.40


def test_satellite_strength_capped_below_threshold():
    signal = SatelliteAgent().observe(REGION, 100, 1.0)
    assert signal.strength < 1.0


def test_weather_below_floor_is_silent():
    assert WeatherAgent().observe(REGION, 100, 7.9) is None


def test_weather_at_floor_registers():
    signal = WeatherAgent().observe(REGION, 100, 8.0)
    assert signal is not None and signal.source == "weather"


def test_weather_strength_scales_with_drop():
    low = WeatherAgent().observe(REGION, 100, 12.0)
    high = WeatherAgent().observe(REGION, 100, 32.0)
    assert low.strength < high.strength


def test_agents_preserve_region_and_time():
    signal = SeismicAgent().observe(REGION, 777, 4.0)
    assert signal.region == REGION and signal.at_minute == 777


def test_signal_detail_names_the_reading():
    signal = SatelliteAgent().observe(REGION, 100, 0.55)
    assert "0.55" in signal.detail
