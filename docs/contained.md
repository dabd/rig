# Project deletion protection

The standalone `jig` command selects the native Codex or Claude sandbox.
Run it from a Git project:

```sh
jig codex
jig codex-personal
jig claude
jig claude-personal
```

The launcher calls the existing profile shell functions, retaining normal
authentication, conversation history and native memory. Writes are limited to
the project and narrow caches. Existing safety hooks supplement protection
inside the writable project. SOS saves the protected command and reapplies it
on recovery when its Jig launcher support is installed.

Install the reviewed standalone package using `uv tool install /path/to/jig`.
Optional companion/cache roots are private entries in
`~/.config/jig/config.json`. No provider, credential or memory overlay is
required. Ordinary native commands are still available; use `jig` for
protected sessions.

The old `contained` command remains a compatibility alias for saved SOS records.

The old `rig-contained-source` helper and staged source preparation are retired
experiments. They are not part of the current product or its startup path.
