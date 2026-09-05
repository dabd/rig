---
name: luthier
description: "Design a reasoning skill and evidence-based trial when explicitly asked to address a recurring reasoning failure."
disable-model-invocation: true
---

# luthier

Sessions play instruments; this builds them. Build when a recurring reasoning
failure would have been caught by a fixed procedure, and keep only on trial
evidence. Emit both: the draft, and the trial that can kill it.

## Inputs

`/luthier <problem statement>`: one paragraph naming a failure sessions keep
repeating. Field evidence (incident, bad review round, failed trial) is the
strongest input, so paste it in whole.

## Procedure

### 1. Name the failure, not the topic

Write it as one sentence: sessions do X where they should do Y, and the cost is
Z. Then cite one case where it already happened. A failure you cannot instance
is a hunch, and a skill built on it has no oracle later. Stop here and say so.

### 2. Check the lane

Read the descriptions of the installed skills. Lanes are disjoint by *question*,
not by topic: what happened before, what moves outward, what fails next, what
must stay true, what inputs break it. State the new question concisely and
check whether an installed skill already covers it. Shared topic is fine; a shared question
means you are editing an existing skill, not building one.

### 3. Fix the frame: operator x domain x evidence rule

- **Operator**: the reasoning move that addresses the failure. Inspect a
  relevant installed skill only when its description suggests a reusable
  method. Name the one you are
  specializing, or say why none fits.
- **Domain**: what it is pointed at. A diff, a module, a format, a rollout.
- **Evidence rule**: what makes a claim admissible, and this is the load-bearing
  one. The dominant precision failure in trials to date is verifying that an
  artifact *exists* and then asserting a *consequence* it does not support. Bind
  the consequence: reachability (on a live path from here), liveness (still true
  today), co-variance (do the two multiply, or move 1:1). Then name the label a
  claim carries when the evidence stops short: speculative, UNKNOWN, NOWHERE,
  CONTRADICTED. A skill that cannot say "I could not close this" will invent.

### 4. Pre-register the trial, before drafting the text

Write the protocol first. Drafting first lets the text choose its own exam.

- **Oracles**: representative inputs whose right answer is already recorded somewhere
  outside your judgment: git history, a merged PR, an incident review, a spec.
  Recall against that record is the score.
- **Null control**: one input where the honest output is "nothing here". A skill
  that fires on the control is a generator, not an instrument.
- **Trigger audit** (auto-invoked skills only): prompts that must fire it and
  prompts that must not. Phrase two must-fire prompts around the intent rather
  than the verb; bypasses arrive phrased as optimization.
- **Verdict criteria**: the numbers and shapes that mean KEEP, REPAIR, or DROP.
  Written now, applied unchanged later.

Blind means the answer is not visible in the trial context. Blinding always
hides something structural, so name what it hides and add a second phase
covering exactly that. Acceptance on presentation is not a precision oracle:
novel findings go to a verifier holding the repo context.

### 5. Draft in house shape

Use concise frontmatter with a capability and precise trigger. Preserve the
user's intended invocation mode: explicit-only skills use Claude's
`disable-model-invocation: true` and Codex's
`agents/openai.yaml` policy `allow_implicit_invocation: false`.
Keep purpose, essential constraints, and useful routing in the entrypoint.
Move substantial examples or mode-specific procedures to conditional references.

Give the output fixed fields, because the fields are the procedure: a field
nobody can fill is the finding, not a gap to paper over. Order the steps
cheapest first and say where to stop; a fast path for the easy case shortens
the report, never the verdict. Draw the anti-patterns from the step 1 failure,
from the must-not-fire prompts, and from how the operator degrades when empty.

A skill that gates an action already underway also states an interaction
contract: what each verdict means for the work, what new evidence could require
a user decision, and which work can continue under existing authorization.
Do not invalidate informed approval merely because it predates the verdict.

### 6. Trial, score, repair

Run the protocol. Score against the criteria as written. Collect the executor's
friction notes too: which step was ambiguous, skipped, or re-read. Every repair
worth making came from a friction note or a missed oracle, none from re-reading
the text. Repair, then re-run only the trials the repair could move.

### 7. Publication gate

The skill lands in a public repo: no employer, client, hostname, ticket id, or
private path in the body, examples, or description. Examples: public or synthetic.

## Rules

- **Revise for a concrete reason.** Use field evidence, failed trials,
  contradictory instructions, or an explicit change in user requirements.
  Recheck the cases the change could affect. Do not require a chain of other
  skills or generate speculative improvements merely to fill a review.
- **Null output is a result.** A one-off, something a standing instruction
  covers, a question an installed skill already asks: say which, and stop.
- One skill, one question. A second question is a second skill.
- **Composition**: name the installed skill that runs before or after this one,
  or state that none does. Do not invent a pairing to satisfy the line.

## Anti-patterns

- **Skill-shaped prose**: a domain essay with no procedure and no fields to fill.
- **Quota outputs**: a fixed N findings every run. The count is a ceiling.
- **Checks that cannot fail**: a rule no draft could turn red is decoration.
- **Encyclopedia scope**: covering the domain, not the step 1 failure sentence.
- **Polishing before evidence**: rewriting a draft that has never run.

## Output

Two artifacts, protocol first: the trial protocol (failure sentence, lane check,
oracle cases with their recorded answers, null control, trigger audit if any,
verdict criteria), then the SKILL.md draft at its install path, uncommitted
until it has a verdict.
