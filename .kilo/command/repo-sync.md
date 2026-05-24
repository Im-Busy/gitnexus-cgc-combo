---
description: Sync curated files from the private development repo to the public-facing repo. Merges master→public, runs safety checks, strips private data, and pushes only the clean public branch.
---

# Repo Sync — Private → Public Curation

Syncs the `public` branch with the latest `master` changes, automatically stripping private data (progress docs, agent memory, IDE configs, workspace files).

## Usage

```
/repo-sync              # Full sync: merge master → public → push
/repo-sync check        # Safety check only: verify no private files on public branch
/repo-sync status       # Show current branch state and remote config
```

## What It Does

| Step | Action |
|------|--------|
| 1. Verify | Confirm `private`→private, `public`→public remotes |
| 2. Pull | Fetch latest `master` from private remote |
| 3. Merge | Merge `master` into `public` branch |
| 4. Safety check | Scan for leaked private files |
| 5. Clean | If leak detected: `git rm --cached` private files |
| 6. Push | Push clean `public` branch to public repo |
| 7. Return | Switch back to `master` |

## Safety Guarantees

- Only pushes the `public` branch — never `master`
- Detects and strips: `progress_docs/`, `MEMORY.md`, `.vscode/`, `.claude/`, `CLAUDE.md`, `.python-version`, `.code-workspace`
- Verifies no `master` branch exists on the public remote after push
- All operations are revertible (no destructive commands)

## Emergency

If private files ever appear on the public repo:
```bash
git push public --delete master 2>$null   # Delete master if it exists
git push public --force public             # Force-push clean public branch
```
