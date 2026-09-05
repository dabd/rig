## Personal workspace

Clone disposable repositories under `~/projects/mystuff/agents/<repo>`. The
Git configuration there selects the personal identity; `/tmp` does not, and
macOS cleanup can delete idle temporary checkouts.

The `agents/` janitor recognizes disposable build caches by a `-cache` suffix.
After a review or freeze milestone, back up the branch to
`~/projects/mystuff/agents/.backups/<repo>.git`, creating the bare repository
if needed. Unpushed commits should not exist in only one `.git` directory.
