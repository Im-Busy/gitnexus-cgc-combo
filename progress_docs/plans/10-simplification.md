# Phase 10: Architecture Simplification

> **Date:** 2026-05-23  
> **Rationale document:** `docs/DESIGN_RATIONALE.md`  
> **Summary:** Reduce codebase from 10 Python scripts (~2,450 LOC) + 8 test files (~2,000 LOC) down to 1 core script (~300 LOC) + 1 test file. Remove incorrect abstractions (Docker, unified CLI, offline mode) and premature infrastructure (CI, devcontainer, packages). Align with principle: **the agent is the runtime, AGENTS.md is the program, scripts exist only where agents are weak.**

---

## Current State (Before)

```
src/
├── combo.py             187 lines   Unified CLI dispatcher
├── config_gen.py         242 lines   MCP config engine ← KEEP
├── setup_combo.py        210 lines   Environment detection
├── inject_agents_md.py   440 lines   AGENTS.md template injection
├── uninstall.py          463 lines   Cleanup protocol
├── skill_gen.py          212 lines   Skill file generation
├── offline.py            193 lines   Offline mode
├── bootstrap_state.py    145 lines   Phase state tracking
├── watcher_health.py     195 lines   Watcher health check
└── rule_extractor.py     399 lines   Rule extraction + directives
                           ---- 
                        ~2,686 lines
```

Plus: `tests/` (8 files, ~2,000 lines), `Dockerfile`, `templates/` (2 files), `.devcontainer/`, `.github/workflows/`, `packages/` (3 stubs), `.pre-commit-config.yaml`.

`pyproject.toml` registers 9 CLI entry points:
```
combo, combo-setup, combo-uninstall, combo-config, combo-skills,
combo-health, combo-offline, combo-inject, combo-state
```

## Target State (After)

```
src/
└── config_gen.py         ~300 lines   MCP config engine + CLI orchestrator
```

Plus: `tests/test_config_gen.py` (kept, ~200 lines).

`pyproject.toml` registers 1 CLI entry point:
```
combo-setup
```

---

## What the Single Script Must Do

`combo-setup setup <project-path>` orchestrates the full manual install path:

1. **Detect platform(s)** — scan project dir for platform markers (existing `detect_platforms()` in config_gen.py)
2. **Generate MCP configs** — for each detected platform (existing `write_mcp_config()`)
3. **Index with GitNexus** — `npx gitnexus analyze --embeddings --skills`
4. **Index with CGC** — `uv run cgc index <project-path>`
5. **Print summary** — platforms configured, index stats, watcher status

The `--detect` and `--platform` flags from current `config_gen.py` remain for advanced users who only want MCP config generation.

---

## Phase Status

| # | Phase | Status |
|---|-------|--------|
| 10 | Architecture Simplification | ⏳ In Progress |

---

## Task Breakdown

### P0: Core Reduction (remove incorrect abstractions)

| Priority | Task# | Task | Description |
|----------|-------|------|-------------|
| P0 | 10-1 | Delete 9 Python scripts | Remove `combo.py`, `setup_combo.py`, `inject_agents_md.py`, `uninstall.py`, `skill_gen.py`, `offline.py`, `bootstrap_state.py`, `watcher_health.py`, `rule_extractor.py` from `src/`. |
| P0 | 10-2 | Delete test files | Remove `test_bootstrap.py`, `test_inject_agents_md.py`, `test_phase02.py`, `test_phase04_05.py`, `test_setup_combo.py`, `test_skill_gen.py`, `test_uninstall.py`. Keep `test_config_gen.py` only. |
| P0 | 10-3 | Delete infrastructure files | Remove `Dockerfile`, `.devcontainer/`, `.github/`, `.pre-commit-config.yaml`, `templates/`, `packages/`. |
| P0 | 10-4 | Clean `pyproject.toml` | Replace 9 `[project.scripts]` entries with 1: `combo-setup = "src.config_gen:main"`. Remove `dev` dependency group (ruff, pytest). Remove `[tool.ruff]` and `[tool.pytest.ini_options]` sections. |
| P0 | 10-5 | Expand `config_gen.py` with `setup` mode | Add a `setup` subcommand to the existing argparse that: (1) runs `detect_platforms()` if `--detect`, (2) runs `write_mcp_config()` for each platform, (3) runs `subprocess.call(["npx", "gitnexus", "analyze", "--embeddings"])` and `subprocess.call(["uv", "run", "cgc", "index", str(project_path)])`, (4) prints summary. The existing `--detect`, `--platform`, `--print`, `--force`, `--list-platforms` flags remain for config-only usage. |
| P0 | 10-6 | Update `AGENTS.md` Phase 3 | Phase 3 currently says "Run: `uv run python src/config_gen.py --detect --project-path <user_project_root>`". This is still correct. Verify no references to removed scripts. Remove Phase 5 watcher template references (templates directory being removed — AGENTS.md already documents the commands inline). |
| P0 | 10-7 | Update `README.md` architecture section | Replace the tree diagram and file descriptions to reflect the simplified layout. Update section "Architecture & Technical Implementation" to explain the two-path design (agent reads AGENTS.md, manual users run `combo-setup`). |
| P0 | 10-8 | Update `MEMORY.md` | Update "Architecture" tree diagram. Update "Phase Status" to mark Phase 10 as in-progress. Add Phase 10 to "Current Objectives". Update "Design Principles" to add the agent-as-runtime principle. Add session log entry. |

### P1: Documentation & Cleanup

| Priority | Task# | Task | Description |
|----------|-------|------|-------------|
| P1 | 10-9 | Review and update `docs/` | Check `SETUP_GUIDE.md`, `TOOL_REFERENCE.md`, `MCP_CONFIGS.md` for references to removed scripts or features. Update where needed. |
| P1 | 10-10 | Update `.gitignore` | Remove entries for files/directories being deleted. Add entry for `.gitnexus-cgc-bootstrap.json` if the state file is cut. |
| P1 | 10-11 | Update `progress_docs/plans/full.md` | Add Phase 10 to phase status table, execution order, and add deferred items for features being cut. |
| P1 | 10-12 | Verify `uv run combo-setup` works end-to-end | Create a temporary test project, run `uv run combo-setup setup <test-project>`, verify MCP configs are generated, indexes are created, summary is printed. Run `uv run combo-setup --detect --project-path <test-project>` to verify config-only mode still works. |

### P2: Future Considerations (deferred)

| Priority | Task# | Task | Description |
|----------|-------|------|-------------|
| P2 | 10-13 | `uvx` distribution | Publish to PyPI. Verify `uvx gitnexus-cgc-combo setup .` works as zero-install distribution path. |
| P2 | 10-14 | Standalone binary | PyInstaller build for users without Python/uv. Deferred until core is stable and published. |
| P2 | 10-15 | Re-add watcher management | If users ask for OS-level watcher lifecycle management (systemd/launchd/Start-Process), add back as inline documentation in AGENTS.md, not as code. |

---

## What Gets Cut (Detailed Rationale)

> Full design reasoning in `docs/DESIGN_RATIONALE.md`. Summary below.

| File | Lines | Why Cut |
|------|------:|---------|
| `combo.py` | 187 | Unified CLI dispatcher wrapping 9 subcommands. Design says a unified CLI is too much — one command is enough. |
| `setup_combo.py` | 210 | Runs `node --version`, `python --version`, etc. Agent does this with `bash`. For the manual CLI path, env checks are inline in `config_gen.py`'s setup mode. |
| `inject_agents_md.py` | 440 | Template extraction (150 lines), fence-balancing algorithm, variable substitution, section splitting, diff detection, platform directive writing. Agent does all of this with `read` + `edit`. Manual users don't need AGENTS.md injection (they're not using AI tools). |
| `uninstall.py` | 463 | 10 functions, 5 removal categories, cross-module imports from `inject_agents_md`. Agent undoes what it did. Manual users can delete config files manually or just not use the tool. |
| `skill_gen.py` | 212 | Generates SKILL.md from Python dicts that duplicate what's already in `.kilo/skills/`. Agent copies files directly. Manual users have no skill system. |
| `offline.py` | 193 | Hardcodes MCP configs already generated by `config_gen.py`. Duplicates platform→family mapping from `matrix.json`. Offline bootstrap is an edge case for an internet-dependent tool. |
| `bootstrap_state.py` | 145 | Phase state tracking for resume-on-failure. Protocol is idempotent — re-running phases is safe. State file is solving a problem that doesn't exist. |
| `watcher_health.py` | 195 | 195 lines to wrap `pgrep -f "cgc watch"` (Unix) and `Get-Process` (Windows). Agent does this in one `bash` call. |
| `rule_extractor.py` | 399 | Extracts "Always Do" / "Never Do" bullet points from markdown, normalizes skill paths, writes meta-directives. Imports from `inject_agents_md` (circular dependency). All operations the agent does natively. |
| `Dockerfile` | 20 | Wrong abstraction — bootstrap tool installs software on the host. Docker isolates from the host. |
| `tests/` (7 of 8 files) | ~1,800 | Tests for scripts being cut. Only `test_config_gen.py` survives. |
| `templates/` (2 files) | — | systemd service + launchd plist. Commands are already in AGENTS.md Phase 5. |
| `.devcontainer/` | — | Contributor infrastructure. Premature for a project still clarifying scope. |
| `.github/` | — | CI pipeline. Premature. Defer until published package exists. |
| `.pre-commit-config.yaml` | — | Admin overhead. Defer until published. |
| `packages/` (3 stubs) | — | VS Code extension, npx starter, standalone binary. Three products before the core product is stable. |

**Total removed:** ~2,450 lines Python + ~1,800 lines tests + ~10 config/infra files.

---

## What Survives

| File | Lines | Why Keep |
|------|------:|----------|
| `AGENTS.md` | ~540 | The program. Single source of truth. Agent follows this. |
| `src/config_gen.py` | ~300 | The one script agents genuinely need. Structured JSON manipulation across 10 platforms × 3 format families. Expanded with `setup` subcommand for manual CLI path. |
| `platforms/matrix.json` | ~200 | Data, not code. Adding a platform requires only a JSON entry. |
| `.kilo/` directory | — | Agent commands, agents, skills, rules. Lightweight wrappers. |
| `docs/DESIGN_RATIONALE.md` | ~350 | Design decisions captured. |
| `tests/test_config_gen.py` | ~200 | Verify config generation and merge logic. |

**Total kept:** 1 Python script (~300 lines), 1 test file (~200 lines), 1 JSON data file, 1 protocol document.

---

## Post-Cut Architecture

```
gitnexus_CGC_combo/
├── AGENTS.md                  # Agent protocol (the program)
├── README.md                  # Human-facing overview
├── MEMORY.md                  # Project state
├── pyproject.toml             # Single entry point: combo-setup
├── platforms/
│   └── matrix.json            # Platform registry (data)
├── src/
│   └── config_gen.py          # MCP config engine + setup CLI
├── tests/
│   └── test_config_gen.py     # Config generation tests
├── .kilo/                     # Kilo-native configs
│   ├── kilo.json              # This project's own MCP config
│   ├── global-rules.md        # Agent behavioral rules
│   ├── project-rules.md       # Combo-specific rules
│   ├── agent/                 # 3 agent definitions
│   ├── command/               # 3 slash command manifests
│   └── skills/                # 8 skill files
└── docs/
    ├── DESIGN_RATIONALE.md    # Design decisions
    ├── SETUP_GUIDE.md
    ├── TOOL_REFERENCE.md
    └── MCP_CONFIGS.md
```

---

## Execution Order

```
Phase 10 (Simplification)
    │
    ├── P0-1: Delete 9 scripts
    ├── P0-2: Delete 7 test files
    ├── P0-3: Delete infrastructure (Docker, CI, packages, etc.)
    ├── P0-4: Clean pyproject.toml (9→1 entry points)
    ├── P0-5: Expand config_gen.py with setup mode
    ├── P0-6: Update AGENTS.md references
    ├── P0-7: Update README.md
    ├── P0-8: Update MEMORY.md
    ├── P1-9: Update docs/
    ├── P1-10: Update .gitignore
    ├── P1-11: Update progress_docs/plans/full.md
    └── P1-12: End-to-end verification
```

**Estimated effort:** P0: 1 session (~3 hours). P1: 1 session (~1 hour). P2: deferred.
