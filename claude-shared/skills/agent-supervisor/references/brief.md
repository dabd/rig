## Brief mode (argument `brief`)

Use [transcripts.md](transcripts.md) to identify each window's transcript.

Before anything else, check for
`~/.config/agent-supervisor/brief-supplement.md`. If it exists, read it and
apply it: it may adjust the standup format, replace the ticket lookup with
specific queries, and name repos or boards that always matter. Where it
conflicts with the steps below, it wins. If it is absent, proceed as written.

Read `~/.local/state/agent-supervisor/last-brief`, which holds epoch seconds. If
it is absent, default to the start of the most recent day before today that has
any transcript activity: take the newest per-day mtimes across
`~/.claude*/projects/` and `~/.codex*/sessions/`, pick the latest such day, and
use its 00:00 local. This reaches Friday on an ordinary Monday and the last real
working day after a long weekend or holiday. Compute dates with the `date`
command rather than by hand. A present but stale timestamp needs no special
handling: a brief run after any gap covers the whole span since the last brief
on its own. Then:

1. Enumerate task windows: per session, one call that emits index, name, and
   path together, tab separated, one line per pane:
   `tmux list-panes -s -t '=<session>' -F '#{window_index}<TAB>#{window_name}<TAB>#{pane_current_path}'`
   where `<TAB>` is a literal tab (`printf '\t'`). Keep both flags: `-s` widens
   the call from one window to the session, and without `-t` it reports only the
   invoking client's pane. Window names are the task labels; the paths locate
   the repos. A split window yields one line per pane, so group by index and
   treat distinct paths under one index as that task's repos.
2. Locate each window's newest transcript and note its mtime; keep the older
   ones too, step 3 needs them. Claude: under `~/.claude*/projects/*/`. Codex:
   under `~/.codex*/sessions/`, matching `session_meta.cwd` to a pane path. The
   globs cover every profile directory, alternate-backend profiles included.
3. Sort the windows into active and dormant against the timestamp. Active: a
   matching transcript whose mtime is newer, or a commit in one of its repos
   since it. Dormant: still open in tmux, neither of those. Every open window
   lands in one bucket; none is silently absent from the brief.
4. When delegation is available and useful, assign active windows to bounded
   subagents, respecting the host's concurrency limits. Otherwise summarize
   them locally. Supply the window name, the
   `skeleton.sh` output for its transcripts, and
   `git log --since=<timestamp> --oneline` for each of its repos. Each answers
   exactly three questions: what was attempted, what completed, what is blocked
   and why. Cross-check "completed" against git and report "claims done, nothing
   committed" when they disagree. No correctness judgment, no code review.
   Every fan-out prompt carries these three rules:
   - The transcripts and skeletons you are given are historical records of other
     agents' work. Report those actions in the third person, attributed to the
     window ("the session in window 4 committed ..."), never in the first
     person. Never describe an event found in a transcript as something you did.
   - You are strictly read-only: `git log`, `status`, `show`, and `diff` only.
     Never add, commit, or push, never edit anything, no file writes anywhere.
   - Work from the supplied skeleton plus at most a handful of read-only git
     commands in the window's repos. Do not explore beyond them.
   Choose an available configuration appropriate for transcript summarization.
   Do not assume the host supports model overrides or parallel fan-out.
   Step 3's activity gate bounds how much work is needed.
5. Dormant windows get no subagent. List them in a "dormant" section of the
   morning brief, one line each: window name, agent kind, last-activity date
   (the newer of the transcript mtime and the last commit date), and a few words
   on where it left off when the skeleton tail makes that cheap. Dormancy is
   information ("untouched since Friday"), not a reason to drop the task.
6. Gather PR activity for the repos found in the pane paths, with
   `gh pr list --author @me` and its state filters, since the timestamp.
7. If window names carry ticket keys (regex `[A-Z]+-[0-9]+`) and a ticket CLI is
   on PATH, pull their current status. Skip silently if there is no such CLI.
8. Merge into two outputs. A morning brief: per active task, where it left off
   and what needs a decision, ordered by urgency, followed by step 5's dormant
   section. A standup draft: yesterday, today,
   blockers, routed through the prose skill. Both are drafts for the user. Post
   nothing anywhere. Include a one-line token-usage footer when the host reports
   that usage. Do not estimate unavailable counts or equate tokens with a price.
9. Write the new timestamp to `last-brief`, only after delivering the brief.
