# Audit State

The skill persists lightweight state between invocations via a `.audit-state.json` file in the target directory. This prevents re-flagging dismissed issues, tracks Low issues across runs, and surfaces what changed since the last audit.

## File Location

Place `.audit-state.json` in the root of the audit target directory. For example, if auditing `docs/plans/notification-system/`, the state file is `docs/plans/notification-system/.audit-state.json`.

If the target is a set of files across multiple directories, use the nearest common ancestor directory.

## Schema

```json
{
  "last_audit": "2026-05-01T14:30:00Z",
  "last_result": "clean",
  "cycles_run": 2,
  "files_audited": [
    "notification-system.md",
    "jira-epic-breakdown.md"
  ],
  "file_checksums": {
    "notification-system.md": "sha256:abc123...",
    "jira-epic-breakdown.md": "sha256:def456..."
  },
  "low_issues": [
    {
      "id": "L1",
      "file": "notification-system.md",
      "description": "Minor heading capitalization inconsistency",
      "first_seen": "2026-04-28T10:00:00Z"
    }
  ],
  "dismissed": [
    {
      "id": "Q1",
      "file": "jira-epic-breakdown.md",
      "description": "Story 2-3 estimate seems low",
      "reason": "User confirmed 2 points is correct",
      "dismissed_at": "2026-04-28T10:15:00Z"
    }
  ],
  "issues_fixed_total": 5
}
```

### Fields

| Field | Purpose |
|-------|---------|
| `last_audit` | ISO 8601 timestamp of the most recent audit completion |
| `last_result` | `"clean"` or `"issues_remaining"` — whether the last run ended with a clean pass |
| `cycles_run` | Number of audit cycles in the last run |
| `files_audited` | List of file paths (relative to state file) audited in the last run |
| `file_checksums` | SHA-256 checksums of each file at the end of the last audit — used to detect changes since last run |
| `low_issues` | Low-severity issues from the most recent audit (carried forward, not fixed) |
| `dismissed` | Issues or questions the user explicitly dismissed with a reason — never re-flag these |
| `issues_fixed_total` | Cumulative count of issues fixed across all runs |

## Loading State (Step 0)

When the audit target is resolved, check for `.audit-state.json` in the target directory. If it exists:

1. Read it and report what changed since the last audit:
   - Compare `file_checksums` against current file contents to identify which files changed
   - Report: `"Last audit: [date]. [N] files changed since then. [M] Low issues carried forward."`
2. Load `dismissed` entries — these will be filtered out in Step 2
3. Load `low_issues` — these carry forward and appear in the report without re-discovery

If the state file doesn't exist, this is a first run. Proceed normally.

## Filtering (Step 2)

When building the audit report, check each finding against the `dismissed` list. Match on file + description similarity (the exact wording may differ slightly between runs). If a finding matches a dismissed entry, exclude it from the report entirely — do not even mention it.

For Low issues, merge newly discovered Low issues with `low_issues` from state. Deduplicate by file + description.

## Saving State (Step 4)

After reporting the final state, write or update `.audit-state.json`:

1. Set `last_audit` to the current timestamp
2. Set `last_result` based on whether the run ended clean
3. Set `cycles_run` to the number of cycles in this run
4. Set `files_audited` to the current audit scope
5. Compute `file_checksums` for all audited files using `shasum -a 256`
6. Set `low_issues` to all Low issues from the final cycle (replacing prior entries)
7. Carry forward `dismissed` entries unchanged
8. Increment `issues_fixed_total` by the count of fixes made in this run

## Dismissing Issues

When the user responds to a question (Step 2) by saying it's not an issue, or tells you to ignore a finding, add it to `dismissed` with their reason. This persists across runs — the user should never have to dismiss the same thing twice.
