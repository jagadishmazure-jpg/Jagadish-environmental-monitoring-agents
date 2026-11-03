# ADR 0001: Correlation as confirmation

## Decision

A prediction requires at least two distinct sources in the same
region within 180 minutes whose combined strength reaches 1.0.

## Rationale

Single sensors spike for ordinary reasons. Requiring corroboration
keeps lone spikes on a watch list instead of turning them into
alerts, and two moderate signals confirm earlier than one sensor
growing strong alone — which is why correlated signals raise lead
time in the demo (90 minutes versus 30 for a late lone signal).

## Consequences

- Genuine single-sensor events are missed by design; the watch
  list exists so a human can still review them.
- Correlated noise produces false alarms (1 of 6 demo
  predictions); threshold tuning trades this against misses.
