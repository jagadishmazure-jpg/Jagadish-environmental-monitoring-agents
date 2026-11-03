"""Sensor agents. Each turns a synthetic reading into a Signal, or
nothing when the reading is below its detection floor. Agents never
issue predictions or escalate anything themselves."""

from __future__ import annotations

from environmental_monitoring.models import Signal


class SeismicAgent:
    source = "seismic"

    def observe(self, region: str, at_minute: int, magnitude: float) -> Signal | None:
        """Magnitude >= 3.0 registers; strength caps at 0.95, so one
        seismic reading alone can never confirm an event."""
        if magnitude < 3.0:
            return None
        strength = min(0.95, 0.15 * magnitude)
        return Signal(self.source, region, at_minute, strength,
                      f"seismic magnitude {magnitude}")


class SatelliteAgent:
    source = "satellite"

    def observe(self, region: str, at_minute: int, anomaly: float) -> Signal | None:
        """Anomaly score in [0, 1]; scores below 0.40 are background."""
        if anomaly < 0.40:
            return None
        strength = min(0.95, anomaly)
        return Signal(self.source, region, at_minute, strength,
                      f"satellite anomaly {anomaly}")


class WeatherAgent:
    source = "weather"

    def observe(self, region: str, at_minute: int, pressure_drop_hpa: float) -> Signal | None:
        """Pressure drops under 8 hPa are ordinary weather, not signal."""
        if pressure_drop_hpa < 8.0:
            return None
        strength = min(0.95, pressure_drop_hpa / 40.0)
        return Signal(self.source, region, at_minute, strength,
                      f"pressure drop {pressure_drop_hpa} hPa")
