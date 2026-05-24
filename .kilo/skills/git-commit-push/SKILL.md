---
name: git-commit-push
description: Safely commits and pushes current changes with dual-repo awareness. Auto-detects branch, runs pre-commit checks (gitnexus_detect_changes), stages files, commits with conventional message, and pushes to the correct remote. Never pushes private branches to public remotes.
license: MIT
metadata:
    skill-author: project
---

# Git Commit & Push — Dual-Repo Aware

Commit and push current working tree changes, respecting the dual-repo architecture.

## Pre-Flight Checks

### 1. Determine repo architecture

```bash
git remote -v
git branch --show-current
```

Results tell you:
- Which remotes exist (`private` + `public` = dual-repo, or just `origin` = single)
- Which branch you're on (determines push target)

### 2. Check index freshness (if GitNexus is active)

```bash
npx gitnexus status
```

If stale, warn the user before committing. The AGENTS.md protocol requires fresh indexes.

### 3. Run change detection (if GitNexus is active)

```bash
npx gitnexus detect_changes
```

Verify changes only affect expected symbols. If unexpected symbols are affected, warn the user.

### 4. Review what will be committed

```bash
git status
git diff --stat
git diff --cached --stat
```

## Staging

### What to stage

```
git add <files>
```

**Rules:**
- Stage source files, tests, docs, configs
- Stage new infrastructure files (agents, commands, skills)
- **Never** stage IDE configs (`.vscode/`, `.claude/`, `.cursor/`)
- **Never** stage index files (`.gitnexus/`, `.cgc/`)
- **Never** stage secrets (`.env`, credentials)
- **Never** stage agent memory (`MEMORY.md`) unless user explicitly asks
- If uncertain about a file, ask the user before staging it

### Verify staged changes

```bash
git diff --cached --stat
```

## Commit

### Message format

Use conventional commit style, adapted for the project:

```
<type>: <description>

<optional body>
```

**Types:**
| Type | When to use |
|------|------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `infra` | Infrastructure, tooling, CI, skills, agents |
| `docs` | Documentation only |
| `chore` | Maintenance, cleanup, curation |
| `test` | Tests only |
| `refactor` | Code restructuring (no behavior change) |

**Examples:**
```
infra: add dual-repo sync infrastructure (whitelist, repo-syncer agent, command, skill)
feat: add platform auto-detection for Kilo MCP configs
fix: handle empty .gitignore in config_gen merge
chore: curate public branch - strip IDE configs and progress docs
```

### Execute commit

```bash
git commit -m "<type>: <description>" -m "<optional body>"
```

## Push

### Dual-repo (private + public remotes)

```
On master/main → git push private master
On public      → git push public public
```

**CRITICAL: NEVER push master to public remote. NEVER push public to private remote.**

Verify before pushing:
```bash
git branch --show-current          # Confirm branch
git remote get-url public           # Confirm public remote URL
git remote get-url private          # Confirm private remote URL
```

### Single-repo (only origin)

```
git push origin <current-branch>
```

## Post-Push Verification

```bash
git status                         # Working tree clean
git log --oneline -3               # Confirm commit is latest
```

For dual-repo, verify public only has public branch:
```bash
git ls-remote --heads public       # Must show ONLY refs/heads/public
```

## Anti-Patterns (NEVER DO)

- NEVER `git push --force` on shared branches without explicit user request
- NEVER push `master` to `public` remote in dual-repo setup
- NEVER skip hooks (`--no-verify`, `--no-gpg-sign`) unless user explicitly requests
- NEVER amend commits that were already pushed to a remote
- NEVER commit files that contain secrets or credentials
- NEVER commit binary artifacts (`.pkl`, `.parquet`, `.zip`, `.tar`)
- NEVER commit without checking `gitnexus_detect_changes` first (if GitNexus available)

## Full Workflow (copy-paste sequence)

```
git status
git diff --stat
npx gitnexus status                          # if GitNexus available
npx gitnexus detect_changes                  # if GitNexus available
git add <files>
git diff --cached --stat                     # verify staging
git commit -m "<type>: <description>"
git branch --show-current                    # confirm target
git push <remote> <branch>                   # push to correct remote
git status                                   # verify clean
```
