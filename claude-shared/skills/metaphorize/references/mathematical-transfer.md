# Mathematical transfer

Use a source formula only when its assumptions have counterparts in the target.
Document each variable, its units, and the mapping. Separate exact identities,
model-dependent relationships, and loose heuristics.

For example, a queueing analogy can transfer Little's Law, L = lambda * W,
when the target has a stable flow with consistently defined arrivals, items,
and elapsed time. An issue tracker with 20 arrivals/day and a hypothetical
5-day mean residence time would have 100 items on average under those
assumptions. This does not establish a waiting-time distribution or prove
that changing priorities improves throughput.

Check conservation, dimensions, stability, ordering, and resource constraints
where relevant. State any adapter, such as converting source priority levels
into target classes, and identify what information the conversion loses.

When calibration is requested, identify observable parameters, available data,
an appropriate estimation method, and a representative held-out check. Missing
data remains missing; a worked hypothetical calculation is not validation.

When evaluation is requested, choose a metric connected to the user's outcome,
a baseline, and a counter-metric for a foreseeable tradeoff. Set thresholds
from domain evidence or user requirements. Do not create a measurement program
for a conceptual mapping request or assign a universal mapping-quality score.

Deliver the applicable formulas, assumptions, a worked transfer, and the
breakpoints that matter. Use a formula shelf or metric sheet only if the user
needs a reusable quantitative artifact.
