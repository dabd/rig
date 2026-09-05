---
name: agent-supervisor
description: Inspect coding-agent tmux sessions, monitor their status when requested, or prepare a brief from their activity.
---

# Agent supervisor

Observe agent sessions and report their state. Never write to another session,
answer its permission prompts, or dispatch work into it. A request for a status
report does not authorize controlling the fleet.

The executable helpers `sweep.sh` and `skeleton.sh` live beside this file.
Use their full paths. State is stored under
`~/.local/state/agent-supervisor/`; missing state is a normal first run.

Choose the requested workflow:
- Current status, a specific window, or monitoring: read
  [sweep.md](references/sweep.md). One-time questions get one fresh report;
  only monitoring requests establish a recurring loop.
- Morning brief or standup draft: read [brief.md](references/brief.md).
  Drafts stay with the user; publishing needs explicit authorization.
- Ambiguous transcript identity: use [transcripts.md](references/transcripts.md)
  and report uncertainty if it cannot be resolved.

## 6. Limits

- The brief sees agent transcripts and git activity only. Work done by hand,
  meetings, and chat context will not appear. It seeds the standup; the user
  writes the final version.
- Classification patterns drift as agent UIs change. `unknown` states are
  pattern-tuning signals, not errors.
- Change detection ignores known volatile output only, currently the
  esc-to-interrupt status line and its ticking timer. A pane running some other
  always-redrawing UI reports changed every sweep and will never look stuck.
- A tab character inside a tmux window name misparses the window listing. If a
  window's name or index looks wrong, check the name for a tab.

## 7. Errors

- `sweep.sh` exits 2 when tmux is not running or a named session does not
  exist. Relay its stderr message verbatim and stop. No retries.
- `skeleton.sh` exits 2 on an unreadable transcript. Relay and move on to the
  next window.
- No transcript found for a window: report "no agent history found" for that
  task and fall back to git evidence.
