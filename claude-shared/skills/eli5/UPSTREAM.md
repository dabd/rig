# Upstream

Vendored verbatim from the `eli5` plugin in the community marketplace
`anthropics/claude-plugins-community`, path `eli5/skills/eli5/SKILL.md`,
at commit `a727be1c7bd6064419b6f60d71993a19198adc17` (fetched 2026-08-27).

Author: Thariq Shihipar. License: MIT (per `eli5/.claude-plugin/plugin.json`).

Vendored rather than installed as a plugin because a plugin reaches only a
Claude profile: codex reads skills from its own `skills/` directory, and the
work profile's `settings.json` is not repo-managed. One copy here serves all
four profiles (see the README's Architecture section).

To update: refetch the file above and bump the commit pin.
