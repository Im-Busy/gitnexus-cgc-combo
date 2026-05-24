# Agent Handover State

> Auto-updated each session. Read this first when resuming.

## Project Vision

**Code Intelligence Bootstrap Kit** — an agent-native provisioning system that teaches any AI coding agent to self-install, configure, and operate GitNexus + CodeGraphContext. The agent enforces impact-analysis-before-edit discipline forever after.

This repo ships:
1. A **protocol document** (AGENTS.md) — 8-phase bootstrap sequence for the agent
2. A **platform matrix** (platforms/matrix.json) — declarative registry of all supported AI coding platforms
3. A **config generator** (src/config_gen.py) — generates correct MCP JSON for any platform, merges with existing, plus CLI orchestrator
4. **8 operational skills** — GitNexus (6) + CGC (1) + combo workflow (1)
5. **3 slash commands** — `/combo-setup` (provision), `/combo-diagnose` (health check), `/combo-uninstall` (cleanup)

## Key Insight

**The end user never runs any commands.** The AI agent reads this repo's instructions and provisions everything. This repo is a knowledge injection for AI coding agents.

**The product is the protocol, not the executables.** GitNexus fetches via `npx`, CGC installs via `uv pip install`. The combo repo provides the bootstrap logic, platform mapping, config merging, and behavioral rules.

## Architecture

```
gitnexus_CGC_combo/
├── AGENTS.md                 # MAIN FILE — full 8-phase bootstrap protocol (the program)
├── README.md                 # Human-facing overview
├── MEMORY.md                 # This file — project state
├── pyproject.toml            # Single entry point: combo-setup
├── platforms/
│   └── matrix.json           # Platform registry — single source of truth
├── src/
│   └── config_gen.py         # MCP config engine + CLI orchestrator (~300 LOC)
├── tests/
│   └── test_config_gen.py    # Config generation tests
├── .kilo/                    # Kilo-native configs
│   ├── kilo.json             # MCP config template (this project's own setup)
│   ├── global-rules.md       # Universal agent behavioral rules
│   ├── project-rules.md      # Combo-specific rules
│   ├── agent/                # Slash command agent definitions
│   ├── command/              # Slash command manifests
│   └── skills/               # 8 skills (gitnexus + cgc + combo)
├── docs/
│   ├── DESIGN_RATIONALE.md   # Design decisions & scope philosophy
│   ├── SETUP_GUIDE.md
│   ├── TOOL_REFERENCE.md
│   └── MCP_CONFIGS.md
└── progress_docs/            # Progress tracking system
    ├── README.md              # Conventions + plan type catalog
    ├── current.md             # Session log (most recent first)
    ├── plans/
    │   ├── full.md            # Master plan
    │   ├── 10-simplification.md
    │   └── archived/
    ├── handovers/
    └── logs/
```

**Core insight:** The agent is the runtime, AGENTS.md is the program. Scripts exist only where agents are weak (JSON manipulation). Everything else — environment detection, file injection, skill copying, watcher management — the agent does natively.

## Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Agent as runtime** | AGENTS.md is the program, agent is the execution engine. Scripts exist only where agents are weak. |
| **Merge, don't replace** | MCP configs are merged into existing files. User's other servers are preserved. |
| **Detect, don't assume** | Platform auto-detection via filesystem markers. No guessing. |
| **Idempotent** | `<!-- gitnexus:start -->` markers prevent duplicate injection. `skipped` status from config_gen. |
| **Least intrusive** | Only write configs for detected platforms. Meta-directives in platform files are 1-3 lines. |
| **Cross-platform** | Python `pathlib` handles Windows/Unix paths. Agent writes files, not shell scripts. |

## Progress Tracking

> See `progress_docs/plans/full.md` for the master implementation plan.
> See `progress_docs/current.md` for session log.
> See `progress_docs/handovers/` for detailed session handovers.

**Phase Status:** 01 ✅ | 02 ✅ | 03 ✅ | 04 ✅ | 05 ✅ | 06 ✅ | 07 ✅ | 08 ✅ | 09 ⏪ | 10 ✅

> Phases 02-09 artifacts reversed in Phase 10. See `docs/DESIGN_RATIONALE.md` for rationale.

## Current Objectives

1. **[COMPLETE]** Phase 10: Architecture Simplification — reduced codebase from 10 scripts to 1 (config_gen.py, ~300 LOC), 7 test files to 1. Aligned with agent-as-runtime design principle. Plan at `progress_docs/plans/10-simplification.md`. Rationale at `docs/DESIGN_RATIONALE.md`.
2. **[COMPLETE]** Phase 09: Non-Docker Distribution Channels — Codespaces, npx starter, VS Code extension, standalone binary ✅ (reversed in Phase 10)
3. **[COMPLETE]** Phase 08: Distribution & Packaging — CI pipeline, PyPI config, pre-commit hooks, Docker, badges ✅ (reversed in Phase 10)
4. **[COMPLETE]** Phase 07: Uninstall & Cleanup — MCP/AGENTS.md/skills/indexes/directives removal, watcher stop, dry-run ✅ (reversed in Phase 10)
5. **[COMPLETE]** Phase 06: Agent-Executed Injection — template extraction, variable substitution, idempotent AGENTS.md injection ✅ (reversed in Phase 10)
6. **[COMPLETE]** Phases 04+05: Watcher hardening + offline resilience ✅ (reversed in Phase 10)
7. **[COMPLETE]** Phase 03: Tests & Validation ✅ (reversed in Phase 10)
8. **[COMPLETE]** Phase 02: Portable Skills ✅ (skills kept, scripts reversed in Phase 10)
9. **[COMPLETE]** Phase 01: Foundation — Platform matrix, config_gen.py, AGENTS.md rewrite ✅ (core survives)

## Platform Support

| Platform | MCP Family | Config Generation | Skills | Tested |
|----------|-----------|:--:|:--:|:--:|
| Kilo | mcp | Auto (merge) | `.kilo/skills/` | ✅ |
| Claude Code | mcpServers | Auto (merge) | `.claude/skills/` | ✅ |
| Cursor | mcpServers | Auto (merge) | — | — |
| Cline | mcpServers | Auto (merge) | — | — |
| Roo Code | mcpServers | Auto (merge) | — | — |
| Continue.dev | mcpServers | Auto (standalone) | — | — |
| Opencode | mcp | Auto (merge) | — | — |
| Copilot | servers | Auto (merge) | — | — |
| Windsurf | mcpServers | Manual (print) | — | — |
| Augment Code | mcpServers | Manual (print) | — | — |

## Session Log

- **2026-05-24** — Phase 10 COMPLETE — Architecture Simplification executed. P0 tasks: deleted 10 Python scripts from src/ (config_gen.py is the sole survivor), 7 test files from tests/, 6 infrastructure dirs/files (Dockerfile, .devcontainer/, .github/, .pre-commit-config.yaml, templates/, packages/). Cleaned pyproject.toml: 9→1 entry point (`combo-setup`), removed dev dependency group and ruff/pytest tool configs. Expanded config_gen.py (~340 LOC) with `setup` subcommand that orchestrates platform detection, MCP config generation, GitNexus indexing, and CGC indexing with a summary. Updated AGENTS.md: removed setup_combo.py reference, removed template file references from Phase 5 (now documents inline commands), updated systemd/launchd instructions to use direct file creation. Updated README.md: removed CI badge, simplified architecture tree (1 script, 1 test), replaced script-specific sections with two-path architecture explanation, updated design principles. Updated MEMORY.md (this file): completed Phase 10, added session log entry. | P0-1 through P0-8 complete, P1-9 through P1-10 partial. | NEXT: P1-11 update full.md, P1-12 end-to-end verification.

- **2026-05-23** — Phase 10 PLANNED — Architecture simplification. Full audit of current codebase vs. `docs/DESIGN_RATIONALE.md`. Identified 9 Python scripts (~2,450 LOC) + 7 test files (~1,800 LOC) + 10 config/infra files to cut. Target: 1 script (config_gen.py, ~300 LOC), 1 test file. Two-path design: agent reads AGENTS.md, manual users run `combo-setup`. Phase plan written at `progress_docs/plans/10-simplification.md`. Updated `progress_docs/plans/full.md` with Phase 10 + reversal of 02-09. Updated `MEMORY.md` architecture, design principles, phase status, objectives. Distribution recommendation: primary = `uvx`, secondary = standalone binary. Created `docs/DESIGN_RATIONALE.md` with full rationale.
- **2026-05-23** — Phase 09 COMPLETE — ALL 4 channels done. P2 Standalone Binary: standalone_entry.py (180 LOC), build.spec (12 data bundles), Homebrew/Chocolatey/Scoop distribution manifests, release.yml (4-OS matrix). ALL 9 PHASES COMPLETE. Project is feature-complete. (reversed in Phase 10)
- **2026-05-23** — Phase 09 P2 VS Code Extension COMPLETE. Split `extension.ts` into 5 modular TS files (detector, scaffolder, statusBar, commands, extension). Created sync script, synced 10 template files, created README, updated package.json and .vscodeignore. 3/4 Phase 09 channels complete.
- **2026-05-23** — Phase 09 P0+P1 COMPLETE. P0: Verified `.devcontainer/devcontainer.json`. P1: Verified `bin/create-code-intelligence.js` (209 LOC), created `bin/sync-templates.js` (75 LOC) and `README.md`, synced 18 template files into `packages/create-code-intelligence/templates/`. Updated progress docs and MEMORY.md. 2/4 Phase 09 channels complete.
- **2026-05-23** — Phase 02 COMPLETE — Portable Skills P1 items. Added `--skills-platform` flag to `inject_agents_md.py` (normalizes `.claude/skills/` → `.kilo/skills/` for Kilo, replaces CLI table with inline "Key Behaviors" for non-skill platforms). Created `src/rule_extractor.py` (290 LOC) with behavioral rule extraction (Always Do/Never Do), meta-directive writing, platform instruction file detection via matrix.json. Added `.cursorrules` to cursor instructions_files in matrix.json. 36 new tests in `tests/test_phase02.py`. Total: 232 tests passing, ruff clean.
- **2026-05-23** — Phase 09: Non-Docker Distribution Channels planned. Four channels specified: Codespaces (P0), npx starter (P1), VS Code extension (P2), standalone binary (P2). Full technical specs with file structures, implementation details, multi-platform build matrix, and verification steps.
- **2026-05-23** — Phase 08: Distribution & Packaging complete. CI workflow (3 OS × 3 Python), PyPI packaging config, pre-commit hooks, Dockerfile, badges, template clone instructions.
- **2026-05-23** — Phase 07: Uninstall & Cleanup complete. Created `src/uninstall.py` (290 LOC), 36 tests, slash command + agent for `/combo-uninstall`.
- **2026-05-23** — Phase 06: Agent-Executed Injection. Created `src/inject_agents_md.py` (210 LOC), 22 tests, fence-balancing fix.
- **2026-05-23** — Phases 04+05: Watcher hardening + offline resilience. 33 tests, bootstrap state tracker.
- **2026-05-23** — Phase 03: Tests & Validation. 105 tests, ~780 LOC test code, 2 bug fixes.
- **2026-05-22** — Architecture v2: Platform matrix, config_gen.py with merge logic, AGENTS.md Phase 0 self-identification.
- **2026-05-22** — Initial project creation. All infrastructure files created.

## Version Tagging Strategy

| Component | Version Policy |
|-----------|---------------|
| **Semantic versioning** | `MAJOR.MINOR.PATCH` — MAJOR: breaking protocol changes, MINOR: new phases/skills/tools, PATCH: bug fixes/typos |
| **Python package** | `pyproject.toml:version` is the canonical source. Tag with `git tag v{version}`. |
| **GitNexus** | Fetched via `npx gitnexus@latest` — clients always get latest. No version pinning. |
| **CGC** | Pinned in `pyproject.toml:dependencies` via `codegraphcontext>=X.Y`. Bump manually. |

## Release Checklist

```markdown
## Release v0.2.0

### Pre-release
- [ ] Verify `uv run python src/config_gen.py --list-platforms` shows all 10 platforms
- [ ] Verify `uv run combo-setup` help text displays correctly
- [ ] `progress_docs/current.md` updated with session log
- [ ] `progress_docs/plans/full.md` phase status updated
- [ ] `MEMORY.md` Phase Status and Session Log updated

### Release
- [ ] Bump version in `pyproject.toml` (`project.version`)
- [ ] `git tag v0.2.0` with annotation: `git tag -a v0.2.0 -m "v0.2.0: <summary>"`
- [ ] `git push origin main --tags`
- [ ] Create GitHub Release from tag with changelog notes

### Post-release (PyPI — optional)
- [ ] `uv build` — builds dist/
- [ ] `uv publish --token $PYPI_TOKEN` — publish to PyPI
- [ ] Verify: `uvx gitnexus-cgc-combo setup .` works
```

### Changelog Format

Entries in reverse chronological order:

```markdown
## v0.1.0 (2026-05-24)

### Added
- 8-phase bootstrap protocol (AGENTS.md)
- Platform matrix with 10 AI coding platforms (platforms/matrix.json)
- MCP config generator + setup orchestrator (src/config_gen.py)
- 8 operational skills (.kilo/skills/)

### Removed (Phase 10 simplification)
- 10 Python scripts (replaced by agent-native operations)
- 7 test files (tests for removed scripts)
- Dockerfile, .devcontainer/, .github/, .pre-commit-config.yaml, templates/, packages/
```
