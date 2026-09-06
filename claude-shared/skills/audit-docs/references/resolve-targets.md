# Resolve Target Files

Before the audit loop begins, resolve `$ARGUMENTS` into a concrete list of files.

## Input Types

| Input type | Example | How to resolve |
|------------|---------|----------------|
| Explicit path | `docs/plans/unified-automation-commands/` | List all files in that directory (recursive) |
| Glob pattern | `src/**/*.md` | Expand the glob |
| Natural language | `all plan documents`, `the UAC plans`, `phase 3 docs` | Search the project for matching files (see below) |
| Empty | _(nothing)_ | Auto-detect: look for `docs/`, `plans/`, or architecture files |

## Natural Language Resolution

When the input is descriptive rather than a path:

1. **Search for candidate files** using `find`, `grep`, and project structure:
   - Look at directory names that match keywords (`plans`, `docs`, `api`, `architecture`)
   - Look at file names that match keywords (`phase-3`, `playback`, `login`)
   - Look at file contents (headings, frontmatter) for topic matches
   - Check for index files (`README.md`, `index.md`) that list related documents

2. **Build the file list** from matches. Include files that are:
   - Directly referenced by name in the input
   - In directories that match the input's intent
   - Cross-referenced by the matched files (if File A references File B, include File B)

3. **Present the resolved list to the user** before starting the audit:
   ```
   Resolved "$ARGUMENTS" to N files:
     - path/to/file1.md
     - path/to/file2.md
     - ...
   ```

4. **Proceed within the requested scope.** Ask only when plausible targets
   differ materially or the proposed audit would exceed the user's request.

## Cross-Reference Expansion

After the initial list is resolved, scan those files for references to other files not in the list. If a document under audit references an external file for types, interfaces, or contracts, **add that file to the audit set** — otherwise you can't verify the cross-reference is correct.

Present any additions:
```
Added N cross-referenced files:
  - path/to/referenced-types.md (referenced by phase-3.md)
  - ...
```

The resolved file list is the **audit scope** for subsequent cycles. Reading a
referenced file to verify a claim does not authorize editing that file.
