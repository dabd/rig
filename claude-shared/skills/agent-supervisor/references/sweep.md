## 2. Sweep mode (default)

Run `sweep.sh [session ...]`. With no arguments it sweeps every tmux session.
It prints one JSON object:

```
{generated_at, sessions:[{session, windows:[
  {index, name, agent, profile, state, changed, unchanged_sweeps,
   possibly_stuck, tail}]}]}
```

`agent` is `claude`, `codex`, `shell`, or `other`. `profile` names the agent's
config-dir profile, read from the pane's process environment (the wrappers set
CLAUDE_CONFIG_DIR / CODEX_HOME): `personal` for the -personal dirs, `default`
for the stock dirs (the work profile on this machine), and `""` when no
process in the pane's tree carries the variable (agent gone, or launched bare)
or the kind is not an agent. `state` is
`waiting_permission`, `working`, `idle`, `exited`, or `unknown`.
`possibly_stuck` is true when a `working` pane produced no real output for 3 or
more consecutive sweeps. `tail` is populated only when the window changed, when
the state is `waiting_permission`, `exited`, or `unknown`, or when
`possibly_stuck` is true; otherwise it is `[]`.

Report deltas only, one line per notable window, naming session, index, name:

- finished: `working` last sweep, `idle` now.
- newly waiting on the user: `waiting_permission`, or newly `idle`. Say what it
  is asking for, from the tail.
- `possibly_stuck`: give the sweep count and the last thing it printed.
- `exited`: the pane's foreground process is a plain shell, so the agent is
  gone. That is inferred from the pane, not from an observed process exit, so
  say "pane is back to a shell", not "the process crashed".
- `unknown`: show the tail and stop there. Do not guess a state. The patterns
  live in `classify_pane` in `sweep.sh`, and an `unknown` on a live agent pane
  is a signal to tune them, not something to explain away.

After a tmux restore: a sweep run right after a tmux server restart or a session
recovery often shows several `exited` windows at once. A window whose name reads
like a task rather than a shell name (`zsh`, `bash`, and the like) but whose
state is `exited` is most likely an agent session lost in the restore, not
finished work. List those separately, under "possibly lost in restore", and
suggest the user resume them with whatever session-recovery tooling they use.

Say nothing about unchanged `working` or `idle` windows. If nothing is notable,
say so in one line and no more. For a monitoring request, sweep again 15 to 20 minutes later, on a
timer the session already has (a recurring-prompt mechanism, or a backgrounded
sleep whose completion wakes you). Never block on a foreground sleep; it locks
the user out. Loop until the user says stop or the requested terminal condition is met.
For a one-time status question, report one fresh sweep and finish.

## 3. Ad-hoc questions between sweeps

For anything about current state ("what's stuck?", "is window 4 waiting?"),
re-run `sweep.sh`. Do not answer from the previous sweep; it is minutes stale.

For depth on one window ("what happened with X"), pane scrollback is too
shallow. Find that window's transcript using [transcripts.md](transcripts.md), then run
`skeleton.sh <transcript.jsonl>`. It prints the narrative only, auto-detecting
Claude and Codex JSONL: each event begins a line, as `[<iso-ts>] USER: <text>`,
`[<iso-ts>] ASSISTANT: <text>`, or `[<iso-ts>] TOOL: <name>`, text truncated to
500 characters. Narrative text containing newlines continues across following
lines, so do not parse it as strictly one line per event. Tool outputs and file
contents never appear.

If the skeleton is not enough, spawn one subagent to read the relevant span of
the raw transcript, tool outputs included, and report a summary rather than the
content. This is the only deep-dive path, it is expensive, and it runs on
explicit request only.
