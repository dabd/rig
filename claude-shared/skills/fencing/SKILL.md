---
name: fencing
description: Recover intent before removing or bypassing existing behavior whose purpose is unclear, including optimization around guards.
---

# fencing

Chesterton's fence as a procedure: do not remove code until you know why it
was built. Answers three questions: who built this, against what, and is that
constraint still alive.

## Inputs

- `/fencing <file:lines>`, `/fencing <symbol>`, or a pasted snippet, or
- auto: the user (or you) is about to delete, simplify, or bypass code whose
  reason is not stated nearby. Run this BEFORE the edit, not after.

## Procedure

1. Locate: resolve the target to file and lines on the current checkout.
2. Archaeology, cheapest first; stop at the first source that states the
   reason:
   a. `git log -L<start>,<end>:<file>` - follows the lines through renames
      and rewrites. If the commit it lands on does not mention the target
      (a refactor that merely moved the line), fall through to
      `git log -S '<identifier>'` before concluding anything.
   b. The introducing commit: full message plus the rest of its diff (the
      sibling changes often explain the guard).
   c. Linked artifacts: PR (`gh pr view <n>`), ticket ids in the message.
      An unresolvable link (migrated repo, dead tracker) is not a dead end:
      record it as searched-and-unresolvable and let the verdict say so.
   d. Tests that would fail if the code were removed: name them; do not run
      them yet.
   e. Upstream provenance, when the fence is built from library APIs: read
      the documentation of the exact calls involved and search the
      library's docs and issue tracker for the combination. A transplanted
      idiom carries its reason in the upstream docs, not in your repo's
      history, and a whole pattern arriving in one commit with no local
      rationale is the signature of a transplant.
   f. Semantic-owner descent: the layer you call is rarely the layer that
      defines the behavior. The test is ownership, not topic: if you can
      state what the change alters but cannot point to code in front of
      you that defines that behavior, the definition lives in a lower
      layer - descend the delegation chain to its owner and read that
      contract before any verdict. (Cancellation scope, backpressure, and
      evaluation order are typical examples; the test, not this list,
      decides.)
3. Constraint liveness: is the original condition still true today? Check
   the dependency, platform, caller, or bug it guarded against on the
   current tree, not the historical one.
4. Verdict, exactly one of:
   - KEEP: constraint alive; cite it.
   - REMOVE: the reason is recovered and it no longer holds. Two shapes:
     the constraint expired (cite what expired and when), or it never
     existed - accidental duplication or dead on arrival (cite evidence of
     redundancy or unreachability; a missing commit explanation is insufficient).
   - REMOVE WITH EYES OPEN: no reason recoverable. Before settling here,
     hypothesize: what must have been true for a competent engineer to
     write this? Investigate plausible candidate reasons (performance,
     transplanted idiom, workaround for a since-fixed bug, platform
     quirk) and spend one search on each - a hypothesis often names the
     archive the reason lives in. If they all come up empty, say so
     plainly, list what was searched (log, PRs, tickets, tests, upstream
     docs, including links that could not be resolved), and name the
     cheapest canary that would catch a regression: a test to add first,
     or a metric to watch after.

## Interaction contract (what a verdict does to the edit in flight)

This skill usually fires while an edit is already underway. The verdict
gates what happens next:

- Fast-path REMOVE: make the edit; state the recovered reason and its
  expiry in one line so the review trail carries it.
- KEEP: explain the live constraint and the failure a bare removal would
  cause. Preserve that constraint in an alternative implementation when this
  fulfills the authorized task. Earlier informed authorization remains valid.
  Ask only when the evidence introduces a material consequence or choice
  outside that authorization; continue independent preparation meanwhile.
- REMOVE WITH EYES OPEN: state the uncertainty and select verification that
  could expose the suspected regression. Proceed with reversible work within
  the authorized scope. Ask if completion needs new authority, unavailable
  evidence, or a materially different risk decision.

The verdict leads the response; it is never buried under a diff.

## Fast path

Reason recovered in one blame: answer in three lines or fewer. Clearly dead:
proceed with the edit. Clearly alive: preserve the constraint or explain the
new decision needed, using the interaction contract above. The full
report is for genuinely murky fences, contested verdicts, and callers who
asked for the trail.

Steps 2e and 2f are proportionate, not routine: run them when steps 2a-2d
recover no reason, or when the edit swaps a library API for a sibling.
Recovered-and-clear fences do not need an upstream excavation.

## Evidence rule

Every claim cites a commit, PR, ticket, test name, file:line, or an
upstream doc you actually fetched and can quote - an upstream source named
from memory is not a citation. "Probably legacy" is not a verdict. If the
evidence is thin, the verdict is REMOVE WITH EYES OPEN, not a confident
guess.

Three priors that bound the verdict:

- Rare-variant prior: code using the marked variant of a common API (the
  Weak, Unsafe, uncancelable, the longer stranger name) is presumed
  deliberate. An unexplained rare variant never gets plain REMOVE: recover
  the variant's documented semantics first, and if the difference is
  load-bearing on this path, the verdict is KEEP.
- Replacement semantics: a verdict that endorses replacing API A with API
  B states the A-vs-B semantic difference from the library's own
  documentation, not from memory.
- Hot-path uncertainty: an unrecovered reason remains REMOVE WITH EYES OPEN.
  Choose the canary by failure mechanism: a deterministic regression test for
  semantics, a focused benchmark for overhead, or load/soak verification for
  contention, saturation, or failures that need sustained traffic. Hot-path
  placement alone does not require a soak run.

## Anti-patterns

- Blocking trivial edits: renames, comment fixes, and imports whose removal
  cannot change what compiles need no fence check. Anything else with zero
  references still gets the fast path, not a skip: dead-looking code with a
  live reason is the whole point of this skill.
- Fencing your own fresh work: code introduced in the current session or the
  current unmerged change has no history to excavate; deleting it needs no
  fence check.
- Fencing a rollback: reverting a recent change to its prior known-good
  state is returning to the fence, not removing one. Never delay a revert,
  especially during incident response.
- History tourism: stop at the first commit that states the reason; the
  full lineage is not the deliverable.
- Verdict inflation: KEEP requires a live, named constraint. Reverence for
  old code is not a constraint.
