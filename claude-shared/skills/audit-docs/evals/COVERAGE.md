# Eval Coverage — audit-docs skill

## Overview

5 evals covering the core audit cycle behaviors. Each eval uses a fixture directory with planted documentation issues (or no issues) and verifies the skill's response.

## Test Infrastructure

| Component | Path | Purpose |
|-----------|------|---------|
| Runner | `workspace/run-eval.sh` | Runs one eval: copies fixture, builds prompt, invokes claude, diffs results |
| Parallel runner | `workspace/run-all-evals.sh` | Runs all evals with optional parallelism, checks assertions |
| Fixtures | `workspace/fixtures/` | Small doc sets with planted issues |
| Eval definitions | `evals/evals.json` | Scenario definitions with assertions |

## Architecture

Each eval:
1. Copies a fixture directory to a working location (originals stay pristine)
2. Injects `SKILL.md` as context + the user request pointing at the working copy
3. Runs `claude -p` with `--allowedTools "Bash,Read,Edit"`
4. Captures: assistant output, tool calls, raw stream
5. Diffs the working copy against the original to detect file changes
6. Checks assertions: output keywords, files modified/not-modified, files created

## Eval Scenarios

| ID | Name | Fixture | What it tests | Key assertions |
|----|------|---------|---------------|----------------|
| 1 | cross-ref-mismatch | `cross-ref-mismatch/` | Count inconsistency between files | Finds "5 vs 6" mismatch, fixes api-overview.md, re-audits |
| 2 | broken-link | `broken-link/` | References to non-existent files | Reports missing files, does NOT create them |
| 3 | type-drift | `type-drift/` | Interface name spelled differently across files | Finds naming drift, normalizes to source-of-truth definition |
| 4 | clean-pass | `clean-pass/` | No real issues present | Completes in 1 cycle, no file edits |
| 5 | low-only | `low-only/` | Only Low-severity style issues | Reports but does NOT fix, completes in 1 cycle |

## Assertion Types

| Type | Description | Check method |
|------|-------------|--------------|
| `output_contains` | Keywords that must ALL appear in assistant output | Case-insensitive grep |
| `output_contains_any` | At least ONE keyword must appear | Case-insensitive grep |
| `min_cycles` | Minimum audit cycles expected | Regex for cycle references + Edit heuristic |
| `max_cycles` | Maximum audit cycles allowed | Regex for cycle count exceeding limit |
| `files_modified` | Files that should have been edited | Appears in fixture diff |
| `files_not_modified` | Files that must NOT be edited | Does not appear in diff |
| `files_created` | Files created (empty = none should be) | comm against original file list |
| `files_not_created` | Specific files that must NOT be created | grep against new-files.txt |
| `behavioral` | Human-readable expected behaviors | Manual review of output |

## Skill Capabilities vs Coverage

| Capability | Eval |
|------------|------|
| File resolution (path) | All (1-5) |
| Cross-file consistency check | 1, 3 |
| Structural completeness (broken refs) | 2 |
| Severity classification | 1, 2, 3, 5 |
| Fix cycle (edit + re-audit) | 1, 3 |
| Low-severity no-fix rule | 5 |
| Clean pass termination | 4, 5 |
| No file invention | 2 |

## Running Evals

All paths below are relative to the skill root (`skills/audit-docs/`).

```bash
# Run all evals sequentially
./workspace/run-all-evals.sh

# Run all evals with parallelism
./workspace/run-all-evals.sh 3

# Run a single eval
./workspace/run-eval.sh --name cross-ref-mismatch \
  --fixture cross-ref-mismatch \
  --prompt "/audit-docs"

# Check results
cat workspace/results/cross-ref-mismatch/assistant-output.txt
cat workspace/results/cross-ref-mismatch/fixture-diff.patch
```

## Gaps / Future Work

- **Audit state persistence** — no eval tests `.audit-state.json` creation or contents
- **Dismissed issue filtering** — no eval sets up pre-existing state with dismissed entries
- **Incremental re-audit** — no eval verifies Cycle 2+ scope narrowing (modified + cross-refs only)
- **Domain-specific checklist loading** — no eval asserts that API or plan checklists were applied
- **Natural language resolution** — no eval tests "audit all plan documents" style input
- **Cross-reference expansion** — no eval tests automatic inclusion of referenced files
- **Multi-cycle convergence** — no eval has issues that require 3+ cycles to fix
- **max_cycles pause** — no eval tests the oscillation detection behavior
- **Config file** — no eval tests `~/.config/audit-docs/audit-docs.yaml` influence
- **Large file sets** — all fixtures are 2-3 files; no test of 10+ file audits
