# Report Format

Present findings in a structured report. Group by severity, then by file.

## Severity Levels

| Severity | Criteria | Action |
|----------|----------|--------|
| **Critical** | Broken contracts: type mismatch at interface boundary, impossible dependency, fundamentally wrong architecture | Must fix |
| **High** | Incorrect but not broken: wrong count, stale reference, missing error handling per established pattern | Must fix |
| **Medium** | Inconsistency that could confuse an implementer: naming drift, pattern deviation, ambiguous specification | Must fix |
| **Low** | Style, formatting, minor wording issues, optional improvements | Report only — do NOT fix |

## Report Template

```
## Audit Cycle N — Report

**Files audited**: [count]
**Issues found**: [critical] Critical, [high] High, [medium] Medium, [low] Low

### Critical

#### C1: [Short description]
- **File**: `path/to/file.md` (line ~N)
- **Contradicts**: `path/to/other.md` (line ~M)
- **Problem**: [Precise description of the inconsistency]
- **Fix**: [Specific corrective action]

### High

#### H1: [Short description]
...

### Medium

#### M1: [Short description]
...

### Low

#### L1: [Short description]
...
(Low issues are reported but will not be fixed)

### Questions

Do not ask questions about Low-severity issues — they are informational only.

#### Q1: [Ambiguity description]
- **Context**: [What you found]
- **Options**: [Possible interpretations]
- **Needed**: [What information would resolve this]
```

If there are **zero Critical, High, or Medium issues**, state this clearly and proceed to completion.
