# Notes: environmental monitoring as a multi-agent system

Distilled notes in original words. All examples use the fictional
operator Sorrelmere Environmental and synthetic regions; no real
operator, place, event, or sensor feed is referenced.

## Why several agents instead of one model

An environmental signal rarely arrives as a single clean fact. The
ground moves, the sky changes, and orbital imagery shifts, each on
its own cadence and each noisy in its own way. Splitting observation
across agents — one per sensing mode — keeps each agent's detection
rule simple, testable, and honest about its own floor: below that
floor, the agent says nothing rather than guessing.

## Why correlation is the confirmation

A lone spike proves only that one instrument moved. Two independent
instruments moving together, in the same place and close in time,
is a different kind of evidence: it survives the failure or
confusion of either one alone. That is why the coordinator treats
corroboration, not loudness, as the trigger — and why a strong
single spike is held on a watch list instead of becoming an alert.

## Why the human gate sits after prediction, not before it

Prediction is cheap and reversible; external action is not. The
gate therefore sits exactly at the boundary between "we think
something may happen" and "someone outside this system should act."
Approvals are named, single-use, scoped, and expiring, because a
vague, reusable, or stale permission is barely a permission at all.

## Why measurement is part of the system, not an afterthought

Lead time and false-alarm rate pull in opposite directions: predict
earlier and you predict wrong more often; wait for certainty and
the warning arrives too late. Reporting both on every stream, with
the held-back cases visible, is what lets a team tune that trade
instead of arguing about it from anecdotes.
