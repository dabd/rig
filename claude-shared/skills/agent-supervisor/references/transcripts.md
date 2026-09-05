## 5. Finding a window's transcript

For sweep follow-ups and briefs, take the window's `pane_current_path`:

- Claude: the project slug is that path with every `/` and `.` replaced by `-`.
  Prefix match it against the directory names under `~/.claude*/projects/`.
- Codex: grep the `session_meta` lines under `~/.codex*/sessions/` for a
  matching `cwd`.

Both globs cover every profile directory, alternate-backend profiles included.

A path match is a candidate set, not an identification: many windows often
share one repo root, so a single slug directory can hold dozens of sessions.
Disambiguate by content: take the candidates modified in the relevant span,
grep them for distinctive tokens from the window name and from the window's
pane tail, and pick the one whose matches are recent and consistent. When no
candidate matches confidently, report "transcript ambiguous" for that window
instead of narrating another session's work - a misattributed brief is worse
than a gap.
