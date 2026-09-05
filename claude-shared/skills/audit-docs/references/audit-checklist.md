# Audit Checklist

Read ALL target files end-to-end. Do not skim, do not sample. For each file, cross-reference against every other file in the target set.

## Cross-File Consistency

- Type names, interface names, function signatures — do they match across files that reference them?
- Import paths — do referenced files/modules actually exist? Are paths correct?
- Dependency chains — if File A says it depends on File B's output, does File B actually produce that?
- Command/enum/constant names — are they spelled identically everywhere they appear?
- Counts — if one file says "7 commands" and another lists 6, that's an inconsistency

## Internal Consistency

- Do code blocks compile conceptually? Are types used correctly?
- Are function signatures consistent between definition and usage sites?
- Do examples match the interfaces they claim to implement?
- Are return types consistent with what callers expect?

## Structural Completeness

- Are there references to sections, files, or types that don't exist?
- Are there TODO/TBD/placeholder markers that should have been resolved?
- Are there dangling cross-references (links to anchors that don't exist)?
- Are there files mentioned in an index that don't exist, or files that exist but aren't indexed?

## Architectural Coherence

- Do patterns established in one file contradict patterns in another?
- Are responsibilities clearly delineated or do files claim overlapping ownership?
- Are dependency directions consistent (no circular dependencies unless intentional)?
- Do phase/story dependencies form a valid DAG?

## Code Blocks in Documentation

- Import statements referencing non-existent modules
- Type mismatches between producer and consumer
- Missing parameters, wrong parameter order, or wrong parameter types
- Strategy/registry/handler wiring that doesn't match the declared interfaces
- Error handling patterns that differ from the established convention

## Audit Discipline

- Read each file completely before making judgments — do not flag something as "missing" if it appears later in the same file
- When flagging an issue, cite both the source location and the contradicting location
- If something looks wrong but you're not certain, classify it as a question rather than an error
- Track false positives from prior cycles — do not re-flag issues that were already determined to be correct
