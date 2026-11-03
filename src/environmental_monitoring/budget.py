"""Cost/budget guards: negative inputs are rejected, never clamped
silently, so a bad budget line cannot quietly become free."""

from __future__ import annotations


def validate_non_negative(value: float, label: str) -> float:
    if value < 0:
        raise ValueError(f"{label} must not be negative, got {value}")
    return value


def estimate_cost(items: dict[str, float]) -> float:
    total = 0.0
    for label, value in items.items():
        total += validate_non_negative(value, label)
    return total
