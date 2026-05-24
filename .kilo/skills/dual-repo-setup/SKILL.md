---
name: dual-repo-setup
description: Guides the agent to provision a dual-remote Git architecture for any project — private development repo (master/main) + curated public-facing mirror (public branch). Detects project structure, identifies private vs public files, creates whitelist, repo-syncer infrastructure, and .gitignore exclusions. Use when user wants to publish a subset of a private repo without leaking secrets, IDE configs, progress docs, or agent memory.
license: MIT
metadata:
    skill-author: project
---

# Dual-Repo Setup — Provision Private→Public Architecture

You are setting up a dual-remote Git architecture for the current project. Follow this protocol exactly.

## Architecture Pattern

```
Private Repo (remote: private)        Public Repo (remote: public)
  master/main branch                    public branch
  [all files, full history]             [curated subset only]

  git push private master               git push public public
       │                                      │
       │  git checkout public                 │
       │  git merge master                    │
       │  [safety check + strip leaks]        │
       │  git push public public              │
       └──────────────────────────────────────┘
```

## Reference Implementations

Two projects use this pattern with different private/public scopes:

### gitnexus-cgc-combo (bootstrap kit)

| Private only (never public) | Public (curated) |
|---|---|
| `progress_docs/` — project plans | `src/` — config generator |
| `MEMORY.md` — agent memory | `tests/` — test suite |
| `.vscode/`, `.claude/` — IDE configs | `platforms/` — registry |
| `CLAUDE.md` — platform instructions | `docs/` — documentation |
| `.code-workspace` — leaks paths | `.kilo/agent/`, `.kilo/command/`, `.kilo/skills/` — infra |
| `.python-version` — local pin | `.kilo/global-rules.md`, `.kilo/project-rules.md`, `.kilo/kilo.json` |
| `.gitnexus/`, `.cgc/` — indexes | `README.md`, `AGENTS.md` |
| | `pyproject.toml`, `uv.lock`, `whitelist.txt`, `.cgcignore` |

### investment_trying (quant trading)

| Private only | Public |
|---|---|
| `data/` — 105 CSVs, 45 MB | `src/` — 536 source files |
| `models/` — 167 .pkl, 34 MB | `tests/` — 119 files |
| `outputs/` — 739 files, 443 MB | `scripts/` — CLI tools |
| `experiments/`, `reports/` — results | `docs/` — documentation |
| `notebooks/`, `logs/` — runtime | `AGENTS.md`, `README.md`, `BESTS.md` |
| `useful_resources/` — papers/repos | `pyproject.toml`, `uv.lock` |

## Step-by-Step Setup

### Step 1: Detect current project state

```bash
git remote -v
git branch -a
git ls-tree -r --name-only HEAD
```

Identify:
- Current branch name (master or main)
- Existing remotes
- What files exist at root
- What directories are present (src/, tests/, docs/, data/, .github/, etc.)

### Step 2: Classify files into public vs private

Walk the root directory and classify EVERY file/directory:

| Category | Public if... | Private if... |
|----------|-------------|---------------|
| Source code | `src/`, `lib/`, `.py`, `.js`, `.ts`, `.rs` | Generated build artifacts |
| Tests | `tests/`, `test/`, `spec/` | Benchmarks with proprietary data |
| Documentation | `docs/`, `README.md` | Internal planning docs, handover notes |
| Configs | `pyproject.toml`, `package.json`, `uv.lock`, `.gitignore` | `.env`, credentials, local overrides |
| IDE | — | `.vscode/`, `.idea/`, `.claude/`, `.roo/`, `.cursor/` |
| AI tooling | `.kilo/agent/`, `.kilo/command/`, `.kilo/skills/` | `.kilo/worktrees/`, `.kilo/kilo.json` (if has secrets), `MEMORY.md` |
| Data | — | `data/`, `*.csv`, `*.parquet`, `*.db`, `*.sqlite` |
| Models/artifacts | — | `models/`, `*.pkl`, `*.pt`, `*.onnx`, `outputs/` |
| Generated | — | `dist/`, `build/`, `*.egg-info/`, `__pycache__/` |
| Memory/plans | — | `progress_docs/`, `plans/`, `MEMORY.md`, `*.code-workspace` |

### Step 3: Create whitelist.txt

Create a `whitelist.txt` at the project root listing only public paths:

```
# Whitelist for public repo sync
# Lines starting with # are ignored. Directories must end with /.

# === Source Code ===
src/

# === Tests ===
tests/

# === Documentation ===
docs/
README.md
AGENTS.md

# ... (add project-specific entries)
```

### Step 4: Update .gitignore with public exclusions

Append to `.gitignore`:

```
# ===== PUBLIC REPO EXCLUSIONS (both branches) =====
# IDE configs (platform-specific, never tracked)
/.vscode/
/.claude/
/.roo/
/.cursor/
/CLAUDE.md

# Indexes (regenerable)
/.gitnexus/
/.cgc/
```

**Important:** Do NOT add files tracked on the private branch (like `MEMORY.md`, `progress_docs/`) to `.gitignore` — the repo-syncer agent strips them during merge. `.gitignore` only excludes files that should never be tracked on ANY branch.

### Step 5: Configure git remotes

```bash
# If remotes don't exist yet, add them:
git remote add private <private_repo_url>
git remote add public <public_repo_url>
```

### Step 6: Create public branch

```bash
git checkout -b public
```

The public branch starts identical to master. The first curation commit will strip private files.

### Step 7: Make the initial curation commit

On the public branch, remove private files from tracking:

```bash
git checkout public
git rm --cached -r progress_docs/ .vscode/ .claude/ 2>$null
git rm --cached MEMORY.md CLAUDE.md .python-version *.code-workspace 2>$null
git commit -m "curate: remove private files for public mirror"
```

### Step 8: Create repo-syncer infrastructure

Create three files (adapt paths from gitnexus-cgc-combo reference):

1. **`.kilo/agent/repo-syncer.md`** — Agent definition with safety checks, merge workflow, private file stripping
2. **`.kilo/command/repo-sync.md`** — `/repo-sync` slash command (supports `check` and `status` sub-commands)
3. **`.kilo/skills/dual-repo-sync/SKILL.md`** — Full workflow documentation with leak prevention rules

Customize the private files list in each based on Step 2 classification.

### Step 9: Push public branch

```bash
git push public public
```

### Step 10: Return to development

```bash
git checkout master
```

### Step 11: Update AGENTS.md

Add a Repository Architecture section at the top of `AGENTS.md` with remotes, branches, and sync command reference.

### Step 12: Verify

```bash
git remote -v                    # Must show private + public
git branch -a                    # Must show master + public
git ls-remote --heads public     # Must show ONLY refs/heads/public
```

## After Setup: Ongoing Sync

Use `/repo-sync` to merge private changes to public:

```
/repo-sync         # Full sync: merge master → strip leaks → push public
/repo-sync check   # Verify no private files on public branch
/repo-sync status  # Show current state
```

## Leak Prevention Rules

1. Never push master/main to the public remote — only the `public` branch
2. Always run safety check after `git merge` before pushing
3. Always verify remotes before pushing
4. If new private directories are created on master, update the repo-syncer agent
5. If private files ever appear on the public repo, immediately delete: `git push public --delete master`
