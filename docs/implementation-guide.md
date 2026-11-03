# Implementation guide

## Adapting this pattern

1. Replace the synthetic reading functions with your own adapters;
   keep each agent's detection floor explicit and tested.
2. Keep the coordinator's confirmation rule (distinct sources plus
   a combined threshold) and tune the window and threshold against
   your own labelled streams, reporting lead time and false-alarm
   rate for every tuning change.
3. Never remove the human gate from an escalation path. If an
   action must be automatic, scope it to internal, reversible
   steps (raising monitoring cadence) and keep external action
   gated.
4. Keep the audit chain append-only and verify it in tests after
   any change to the payload shape.

## Running

```bash
PYTHONPATH=src python3 -m pytest tests/
PYTHONPATH=src python3 run_demo.py
```
