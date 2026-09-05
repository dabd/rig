---
name: code-simplifier
description: Simplify changed code when requested or when a specific complexity problem needs behavior-preserving cleanup.
---

# Code Simplifier

Improve the code changed in the current task without changing its behavior.

## Scope

- Focus on the current diff or code modified during this session.
- Read nearby code and applicable `AGENTS.md` files before editing.
- Keep bug-fix cleanup minimal and local. Do not turn a fix into a broader refactor.
- Leave unrelated code untouched unless the user explicitly broadens the scope.

## Simplify

- Reduce unnecessary nesting, indirection, duplication, and temporary state.
- Prefer clear names and explicit control flow over clever or compressed code.
- Remove redundant abstractions and comments that merely restate the code.
- Consolidate closely related logic when doing so improves readability.
- Avoid nested ternaries and dense one-liners.
- Preserve useful abstractions, separation of concerns, and debuggability.

## Preserve behavior

- Keep public APIs, outputs, error behavior, side effects, and performance-sensitive semantics intact.
- Do not suppress type errors or weaken validation to make the code appear simpler.
- Do not remove tests or reduce coverage.
- Match the repository's established language, framework, formatting, and testing conventions.

## Verify

1. Inspect the resulting diff for accidental scope or behavior changes.
2. Run the narrowest relevant formatter, type check, and tests.
3. Re-read the changed code as if writing it from scratch; fix any remaining concrete concern.
4. Report only significant simplifications and verification results.
