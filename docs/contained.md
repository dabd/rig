# Project deletion protection

The standalone `contained` command selects the native Codex or Claude sandbox.
Run it from a Git project:

```sh
contained codex
contained codex-personal
contained claude
contained claude-personal
```

The launcher calls the existing profile shell functions, retaining normal
authentication, conversation history and native memory. Writes are limited to
the project and narrow caches. Existing safety hooks supplement protection
inside the writable project. SOS saves the protected command and reapplies it
on recovery when its contained-launcher support is installed.

Install the reviewed standalone package using `uv tool install /path/to/contained-core`.
Optional companion/cache roots are private entries in
`~/.config/contained/config.json`. No provider, credential or memory overlay is
required. Ordinary native commands are still available; use `contained` for
protected sessions.

The old `rig-contained-source` helper and staged source preparation are retired
experiments. They are not part of the current product or its startup path.
