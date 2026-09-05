---
name: audit-docs
description: Audit technical documents for cross-file correctness and contract consistency when explicitly requested.
disable-model-invocation: true
version: "1.0.0"
author: john.jenkins
keywords:
  - audit
  - documentation
  - validation
  - cross-reference
  - consistency
  - planning
license: Apache-2.0
---

# Documentation Audit Cycle

You are running an iterative deep audit of documentation or planning files. The cycle repeats until a clean pass — no exceptions, no shortcuts.

**Target**: $ARGUMENTS

## Usage

```
/audit-docs docs/plans/unified-automation-commands/
/audit-docs src/**/*.md
/audit-docs all plan documents
/audit-docs the UAC phase plans
/audit-docs
```

## Dependencies

| Dependency | Required | Install |
|-----------|----------|---------|
| `find` | Yes | Present on macOS/Linux |
| `grep` | Yes | Present on macOS/Linux |

---

## Step 0: Resolve Target Files

Resolve `$ARGUMENTS` into a concrete list of files. The input can be an explicit path, glob pattern, natural language description, or empty (auto-detect).

Read `references/resolve-targets.md` for the full resolution logic including natural language parsing, cross-reference expansion, and the confirmation flow.

Present the resolved file list and wait for user confirmation before proceeding.

### Load Audit State

After resolving the target directory, check for `.audit-state.json` in that directory. If it exists, read `references/audit-state.md` for the loading logic — it explains how to compare checksums, report what changed, and load dismissed entries and Low issues for use in later steps.

---

## The Audit Cycle

This is a **loop**. Execute steps 1–4 repeatedly. The cycle terminates ONLY when Step 1 produces zero Critical, High, or Medium issues. Fixing issues does NOT count as a clean pass — you must re-run Step 1 afterward.

```
┌─────────────────────────────────────────┐
│                                         │
│  Step 1 ──issues found──▶ Step 2        │
│  Audit                    Report & Ask  │
│    ▲                        │           │
│    │                        ▼           │
│    └────────────────────  Step 3        │
│                           Fix           │
│                                         │
│  Step 1 ──clean pass──▶  Step 4        │
│  Audit                    Done          │
│                                         │
└─────────────────────────────────────────┘
```

## Step 1: Deep Audit

Read `references/audit-checklist.md` for the base checklist covering cross-file consistency, internal consistency, structural completeness, architectural coherence, and code blocks in documentation.

### Cycle 1: Full Audit

On the first cycle, read ALL target files end-to-end. For each file, cross-reference against every other file in the audit scope. There are no shortcuts on the first pass — you need the complete picture.

### Cycle 2+: Incremental Audit

On subsequent cycles, only re-read files that could have changed or been affected by fixes:

1. **Modified files** — every file edited in the previous Step 3
2. **Cross-references** — any file in the audit scope that references a modified file (it may now be inconsistent with the fix)
3. **Referents** — any file that a modified file references (the fix may have introduced a new dependency)

Skip files outside this set — they are unchanged since the last clean read. This significantly reduces context usage on large doc sets while maintaining correctness, because every file that could possibly have a new issue is still covered.

Report the incremental scope at the start of each cycle:
```
Cycle C — re-auditing M of T files (X modified, Y cross-references)
```

If you're unsure whether a file is affected, include it — false inclusions are cheap, missed files are not.

### Domain-Specific Checks

After resolving targets, detect the document type and load the supplemental checklist. These add domain-specific checks on top of the base checklist — always apply both.

| Signal | Checklist |
|--------|-----------|
| Files in a `plans/` directory, or contain phase/epic/story tables, JIRA breakdown sections | `references/checklist-plans.md` |
| Files describe API endpoints, contain HTTP methods, request/response schemas, or OpenAPI references | `references/checklist-api.md` |
| Neither pattern matches | Base checklist only |

If the audit scope contains a mix (e.g., plan docs that include API specs), load both supplemental checklists.

## Step 2: Report and Ask

Present findings grouped by severity, then by file. Read `references/report-format.md` for the severity definitions and report template.

If the audit identified ambiguities that cannot be resolved by reading the files, present each question with context and options. Wait for the user to respond before proceeding. Do not ask questions about Low-severity issues.

### Filter Against Audit State

If audit state was loaded in Step 0, filter findings against the `dismissed` list and merge Low issues with carried-forward state. Read `references/audit-state.md` (Filtering section) for the matching and deduplication logic. When the user dismisses an issue or question during this step, add it to the dismissed list for persistence in Step 4.

If there are **zero Critical, High, or Medium issues**, skip to Step 4.

## Step 3: Fix Issues

Fix all Critical, High, and Medium issues from the report. Track which files you modify — this drives the incremental scope for the next cycle.

1. Make the change in the file
2. Verify the fix doesn't introduce new inconsistencies with other files
3. If a fix in one file requires a cascading change in another, make both changes

**Do NOT fix Low-severity issues.** They are informational only.

**After fixing, return to Step 1.** Do not assume the fixes are correct — the next audit pass will verify them.

## Step 4: Complete

Report the final state:

```
## Audit Complete

**Cycles run**: N
**Final state**: Clean — no Critical, High, or Medium issues
**Files audited**: [count]
**Low issues remaining**: [count] (not addressed per policy)
**Total issues fixed across all cycles**: [count]
```

### Save Audit State

After reporting, write or update `.audit-state.json` in the target directory. Read `references/audit-state.md` (Saving State section) for the full procedure — it covers checksums, Low issue persistence, dismissed entry carryforward, and fix counting.

---

## Rules

1. **Never skip the re-audit.** Every fix could introduce a new problem. The only proof of correctness is a clean Step 1 pass.
2. **Never downgrade severity to end the loop.** If something was Medium+ in cycle N, it stays Medium+ unless the user explicitly says otherwise.
3. **Re-read modified files.** On cycle 2+, re-read every file in the incremental scope (modified + cross-references). Do not rely on memory — re-read from disk. Files not in the incremental scope can be skipped.
4. **Batch fixes by file.** Make all changes to a file at once rather than editing it repeatedly.
5. **Track cycle count.** If you reach `max_cycles` (default 5) without converging, pause and ask the user — you may be oscillating between competing fixes.
6. **No cosmetic fixes.** Fix exactly what was flagged at Medium+ severity. Nothing more.
7. **Respect exclusions.** If config specifies `exclude` patterns, skip matching files.

---

## Configuration

Optionally reads `~/.config/audit-docs/audit-docs.yaml` for project-specific defaults. If the file doesn't exist, the skill works with built-in defaults.

```yaml
default_directory: docs/plans/
file_extensions: md,mdx
max_cycles: 5
fix_severities: critical,high,medium
auto_expand_crossrefs: true
exclude:
  - node_modules/
  - dist/
```

To set up configuration, run the installer:
```bash
bash <skill-path>/scripts/install.sh
```
