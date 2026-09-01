## Implementation

- Clone throwaway/agentic git repos under `~/projects/mystuff/agents/<repo>`, never
  under `/tmp` (macOS tmp_cleaner deletes /tmp entries idle ~3 days; it ate a `.git`
  on 2026-07-31). The `~/.gitconfig` includeIf on `~/projects/mystuff/` sets the
  personal author email there; `/tmp` clones silently use the wrong work email.
- `agents/` is janitor-managed (agents-gc): name disposable build caches with a
  `-cache` suffix. After a branch passes a milestone (review, freeze), push it to
  the backup bare repo `~/projects/mystuff/agents/.backups/<repo>.git` (create with
  `git init --bare` on first use) so unpushed commits never live in exactly one `.git`.
- If you find a pre-existing bug, performance concern, or behavior the task
  doesn't mention, don't fix, optimize, or extend it in this change unless the
  requested behavior cannot work without it; report it as a follow-up in your
  summary. Commit tests only where the task asks for them or the repo already
  keeps tests for this kind of change, sized like the neighboring test files.
  Scratch scripts and quick checks need not be kept.
- Edit files surgically rather than rewriting them whole when the end result
  is the same. Prefer the Edit tool or sed over heredoc rewrites.

@~/.claude-shared/prose-rules.md
