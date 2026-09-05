# Plan Documents Checklist

Additional checks for feature plan documents (master plans, JIRA breakdowns, phase docs). Apply these alongside the base audit checklist.

## Master Plan ↔ JIRA Breakdown

- Every phase in the master plan has a corresponding epic section in the JIRA breakdown, and vice versa
- Phase names/titles match exactly between documents
- Phase dependency declarations match (if master plan says Phase 2 depends on Phase 1, the breakdown should reflect the same)
- Story counts per phase match — count stories in the master plan table and in the breakdown section

## Story Consistency

- Each story ID (e.g., 1-1, 2-3) is unique and used consistently across documents
- Story summaries match between the master plan table and the breakdown's detailed section
- Story point estimates match between documents
- Story dependencies listed in the master plan table match those in the breakdown detail

## Dependency Graph Validity

- The dependency graph forms a valid DAG — no circular dependencies
- Every dependency reference (e.g., "depends on 1-2") points to a story that exists
- Cross-phase dependencies are consistent: if Story 2-1 depends on 1-2, then Phase 2 should depend on Phase 1
- The ASCII/text dependency graph (if present) matches the per-story dependency declarations
- Parallelization notes are consistent with the dependency graph — stories declared parallel must not depend on each other

## Estimates and Scope

- Story point totals per phase match the sum of individual story estimates
- In-scope and out-of-scope items don't contradict each other
- Items listed as out-of-scope don't appear as stories in any phase
- Key decisions are consistent with implementation notes (e.g., if "PostgreSQL" is chosen, stories shouldn't reference DynamoDB)

## Implementation Notes

- API endpoints referenced in implementation notes use consistent path patterns (e.g., `/api/v1/` prefix)
- Service/class names are consistent across stories that reference each other
- Database table or schema references match the schema story's implementation notes
- Auth/middleware requirements mentioned in one story are reflected where needed in dependent stories

## Phase Documents (if present)

- Phase-specific documents are consistent with the corresponding epic section in the breakdown
- Story details in phase docs don't contradict the master plan or breakdown
- Architecture or design decisions in phase docs align with the master plan's Key Decisions section
