# Architecture

Agents observe; the coordinator confirms; the gate authorises;
the plan acts. No agent can escalate, and no prediction can reach
an external action without a named human approval.

```mermaid
flowchart TB
    Readings[Synthetic readings] --> Seismic[SeismicAgent]
    Readings --> Satellite[SatelliteAgent]
    Readings --> Weather[WeatherAgent]
    Seismic --> Coord[PredictionCoordinator]
    Satellite --> Coord
    Weather --> Coord
    Coord --> Watch[Watch list: held single-source spikes]
    Coord --> Pred[Predictions]
    Pred --> Alerts[Alerts]
    Alerts --> Gate[HumanGate]
    Gate --> Plan[ResponsePlan]
    Coord --> Audit[Hash-chained audit]
    Gate --> Audit
    Pred --> Measure[Measurement]
```

Key decisions are recorded in
[adr/0001-correlation-as-confirmation.md](adr/0001-correlation-as-confirmation.md).
