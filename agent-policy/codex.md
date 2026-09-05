## Codex adapter

Use the current Codex tools for shared skill workflows. Consult official
OpenAI documentation when Codex-specific behavior or configuration needs
verification. Resolve configuration against the active profile, not an assumed
`~/.codex` directory. Change another agent's configuration only when in scope.

For explicit-only shared skills, preserve both Claude frontmatter and Codex's
`agents/openai.yaml` invocation policy. Use the installed prose plugin by its
available name rather than a versioned plugin-cache path.
