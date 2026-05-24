---
project: Code Intelligence Bootstrap Kit
last_updated: 2026-05-24
phases_total: 10
phases_complete: 9
phases_reversed: 6
enhancement_tracks:
  - multi-platform
  - tests
  - resilience
  - distribution
---

# Full Implementation Plan

## Phase Status

| # | Phase | Status | P0 Done | P1 Done | P2 Done |
|---|-------|--------|---------|---------|---------|
| 01 | Foundation — Platform Matrix + Config Generator | ✅ Complete | 5/5 | — | — |
| 02 | Portable Skills — Multi-Platform Distribution | ✅ Complete | 3/3 | 3/3 | 0/2 |
| 03 | Tests & Validation | ✅ Complete | 5/5 | 1/3 | 0/2 |
| 04 | Watcher Hardening — Survivable Background Process | ✅ Complete | 3/3 | 2/2 | 0/1 |
| 05 | Offline & Resilience — Error Recovery + No-Network | ✅ Complete | 4/4 | 3/3 | 0/2 |
| 06 | Agent-Executed Injection — AGENTS.md Auto-Writer | ✅ Complete | 2/2 | 2/2 | 0/1 |
| 07 | Uninstall & Cleanup Protocol | ✅ Complete | 3/3 | 2/2 | 1/1 |
| 08 | Distribution & Packaging | ✅ Complete | 2/2 | 3/3 | 2/2 |
| 09 | Non-Docker Distribution Channels | ⏪ Reversed (Phase 10) | 1/1 | 1/1 | 2/2 |
| 10 | Architecture Simplification | ✅ Complete | 8/8 | 3/4 | 0/3 |

---

## Reversal Notes: Phases 02-09

Per the design rationale in `docs/DESIGN_RATIONALE.md`, the scripts, tests, and infrastructure produced by Phases 02-09 are being removed as part of Phase 10. The core insight: **the agent is the runtime — building Python scripts for tasks the agent does natively is redundant.** The work was not wasted — it validated what was and wasn't needed:

- **Phases 02 (Skills), 03 (Tests), 04 (Watcher), 05 (Offline), 06 (Injection), 07 (Uninstall)** — Scripts produced by these phases are being cut. The agent performs these functions natively via AGENTS.md protocol.
- **Phase 08 (Distribution)** — Dockerfile, CI, pre-commit hooks removed. PyPI packaging kept (simplified to single `combo-setup` entry point).
- **Phase 09 (Distribution Channels)** — VS Code extension, npx starter, standalone binary, Codespaces config removed. Deferred until core product is stable.

**What survives from all prior phases:** `config_gen.py` (Phase 01), `platforms/matrix.json` (Phase 01), `AGENTS.md` (Phase 01/06), `.kilo/skills/` (Phase 02), `docs/DESIGN_RATIONALE.md` (new).

---

## Phase 01: Foundation ✅ COMPLETE

> Platform matrix, config generator, environment detector, protocol rewrite, rebranding.

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 01-1 | Platform matrix | `platforms/matrix.json` | 200 | Declarative registry: 11 platforms, 3 MCP format families, detection markers, merge strategies |
| P0 | 01-2 | Config generator | `src/config_gen.py` | 240 | Multi-platform MCP config generator: merge/create/print modes, idempotent, handles all format families |
| P0 | 01-3 | Fix env detector | `src/setup_combo.py` | 130 | Fix shell detection (pwsh), Python detection (filter stubs, try uv), stderr version capture |
| P0 | 01-4 | Rewrite AGENTS.md | `AGENTS.md` | 480 | Add Phase 0 self-identification, 8-phase multi-platform protocol, merge strategy, meta-directive pattern |
| P0 | 01-5 | Rebrand + docs | `README.md`, `docs/*.md` | 350 | Rebrand to "Bootstrap Kit," rewrite SETUP_GUIDE, MCP_CONFIGS, TOOL_REFERENCE for 10 platforms |

**Total:** 5 P0 tasks, 5 files created, 12 files modified, ~15,000 LOC.

---

## Phase 02: Portable Skills ✅ COMPLETE

> Multi-platform skill distribution, platform-specific instruction files, skill system awareness.

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 02-1 | Skills for Kilo | `.kilo/skills/*` | — | 8 skills already structured for Kilo. Copy path documented in AGENTS.md Phase 7. ✅ |
| P0 | 02-2 | Skills for Claude Code | Copy `.kilo/skills/` → | — | Documented copy path in AGENTS.md Phase 7. Agent copies during bootstrap. ✅ |
| P0 | 02-3 | Meta-directives | AGENTS.md Phase 6 | — | Documented meta-directive pattern for CLAUDE.md, .cursorrules, .clinerules, .roorules, .windsurfrules, .github/copilot-instructions.md. ✅ |
| P1 | 02-4 | Skill path normalization | `src/inject_agents_md.py`, `src/rule_extractor.py` | 30 | --skills-platform flag normalizes `.claude/skills/` → `.kilo/skills/` for Kilo. For non-skill platforms, replaces CLI table with inline "Key Behaviors" section containing extracted rules. |
| P1 | 02-5 | Platform instruction file detection | `src/rule_extractor.py` | 50 | detect_existing_instruction_files() + get_platform_instruction_files() use matrix.json instructions_files. detect() returns {pid: [existing_paths]}. |
| P1 | 02-6 | Rule extraction for non-skill platforms | `src/rule_extractor.py` | 290 | extract_always_do(), extract_never_do(), extract_behavioral_rules(), write_meta_directive(), write_rules_to_instruction_file(), write_platform_directives(). Added .cursorrules to matrix.json cursor instructions_files. |
| P2 | 02-7 | Skill generation from AGENTS.md | New: `src/skill_gen.py` | 100 | Auto-generate skill files from AGENTS.md sections for platforms that support skills |
| P2 | 02-8 | Cross-skill validation | New: tests | 60 | Verify skill file references are consistent across Kilo and Claude Code paths |

**Status:** P0 items complete. P1 items document the skill landscape for non-native-skill platforms. P2 items are nice-to-have automation.

---

## Phase 03: Tests & Validation ⏳ PENDING

> Test coverage for config generator, environment detector, and end-to-end bootstrap flow.

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 03-1 | config_gen unit tests — merge | `tests/test_config_gen.py` | 120 | Test merge-into-existing: preserves user's MCP servers, adds only gitnexus+cgc, handles all 3 families |
| P0 | 03-2 | config_gen unit tests — create/skip | `tests/test_config_gen.py` | 80 | Test create-new (empty project), skip (already configured → idempotent), manual print mode |
| P0 | 03-3 | config_gen unit tests — edge cases | `tests/test_config_gen.py` | 100 | Test invalid JSON backup + --force, missing platform, detection on empty project, unknown platform error |
| P0 | 03-4 | setup_combo unit tests | `tests/test_setup_combo.py` | 80 | Test shell detection (bash/zsh/pwsh/cmd), Python detection (python3/python/uv fallback), stub filtering |
| P0 | 03-5 | Full bootstrap integration test | `tests/test_bootstrap.py` | 120 | Simulate full bootstrap on temp project: detect platform, generate config, verify merge, verify idempotent re-run |
| P1 | 03-6 | Test on Windows | — | — | Run full test suite on Windows with PowerShell. Verify backslash paths in JSON. |
| P1 | 03-7 | Test on macOS | — | — | Run full test suite on macOS. Verify Unix paths and launchd watcher template. |
| P1 | 03-8 | Test on Linux | — | — | Run full test suite on Linux. Verify systemd user service template. |
| P2 | 03-9 | Coverage report | `pyproject.toml` | 10 | Add pytest-cov config, set minimum coverage threshold (80%) |
| P2 | 03-10 | CI pipeline | `.github/workflows/test.yml` | 40 | GitHub Actions: ruff lint + pytest on ubuntu/macos/windows matrix |

**Total:** 5 P0, 3 P1, 2 P2. Estimated ~600 LOC tests + CI config.

---

## Phase 04: Watcher Hardening ⏳ PENDING

> Survivable CGC watcher that persists across terminal closes and machine reboots.

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 04-1 | Windows: Start-Process replacement | AGENTS.md Phase 5 | 15 | Replace PowerShell `Start-Job` (dies with terminal) with `Start-Process -NoNewWindow -PassThru` (survives terminal close) |
| P0 | 04-2 | Linux: systemd user service | New: `templates/cgc-watcher.service` | 20 | systemd user service template with auto-restart on failure, logging to journald |
| P0 | 04-3 | macOS: launchd plist | New: `templates/com.gitnexus.cgc-watcher.plist` | 25 | launchd plist template with KeepAlive, RunAtLoad, StandardOutPath |
| P1 | 04-4 | Cross-platform watcher status | AGENTS.md Phase 5 | 10 | Unified status check: `pgrep -f "cgc watch"` (Unix), `Get-Process python* \| Where CommandLine -like "*cgc*"` (Windows) |
| P1 | 04-5 | Auto-restart on crash | templates/* | 30 | systemd: Restart=on-failure. launchd: KeepAlive. Windows: wrapper script with retry loop. |
| P2 | 04-6 | Watcher health metric | New: `src/watcher_health.py` | 60 | CLI to check watcher status, CPU/memory usage, last index update time. Used by combo-diagnose. |

**Total:** 3 P0, 2 P1, 1 P2. Estimated ~160 LOC + 3 template files.

---

## Phase 05: Offline & Resilience ⏳ PENDING

> Graceful degradation when network is unavailable, error recovery per phase, verify-only mode.

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 05-1 | Network connectivity pre-check | `src/setup_combo.py` | 30 | Check npmjs.org + pypi.org reachable. Warn early if offline. Suggest cached alternatives. |
| P0 | 05-2 | Phase error boundaries | AGENTS.md Phase 1-8 | 20 | Each phase returns success/failure. If Phase 2 (CGC install) fails, Phase 3 (index) should not proceed. |
| P0 | 05-3 | Verify-only mode | `.kilo/agent/combo-diagnose.md` | 40 | Combo-diagnose already checks index freshness + watcher + versions. Add: MCP connectivity test, config validity, targeted fix suggestions per failing check. |
| P0 | 05-4 | Cache detection | `src/setup_combo.py` | 40 | Check if gitnexus + cgc are already installed. Skip install phases if found. Offer reinstall if versions mismatch. |
| P1 | 05-5 | Partial bootstrap recovery | New: `src/bootstrap_state.py` | 80 | Write `.gitnexus-cgc-bootstrap.json` state file after each phase. On re-run, resume from last completed phase. |
| P1 | 05-6 | Stale index detection | AGENTS.md | 10 | Before operations, check git status. If HEAD differs from last-indexed commit, flag indexes as potentially stale. |
| P1 | 05-7 | Config backup on corruption | `src/config_gen.py` | 20 | Already implemented via --force (backs up as .bak). Add automatic detection: if JSON parse fails, offer --force. |
| P2 | 05-8 | Offline-first mode | New: `src/offline.py` | 60 | Bundle minimal config templates (static JSON strings). If network unreachable, use bundled configs instead of fetching tools. |
| P2 | 05-9 | Watcher self-healing | Phase 04-5 | — | Covered by watcher auto-restart in Phase 04. |

**Total:** 4 P0, 3 P1, 2 P2. Estimated ~300 LOC.

---

## Phase 06: Agent-Executed Injection ✅ COMPLETE

> Template extraction, variable substitution, idempotent injection, removal.

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 06-1 | Template extraction + variable substitution + idempotent injection | `src/inject_agents_md.py` | 210 | Extract template from AGENTS.md with fence-balancing for nested code blocks, substitute {repo_name}/{symbols}/{cgc_path} etc., create/update/append/noop injection modes |
| P0 | 06-2 | Injection tests | `tests/test_inject_agents_md.py` | 200 | 6 classes, 22 tests: template extraction, variable substitution, idempotent injection, dry-run, removal, edge cases |
| P1 | 06-3 | Dry-run + multi-section | `src/inject_agents_md.py` | built-in | --dry-run flag, _split_sections for gitnexus/CGC separation, removal support |
| P2 | 06-4 | Unified CLI | deferred | — | Combine MCP config + AGENTS.md injection into single command |

**Total:** 2 P0, 1 P1, 0 P2. 2 files created, ~410 LOC.

---

## Phase 07: Uninstall & Cleanup ✅ COMPLETE

> Safe removal of all combo traces: MCP entries, AGENTS.md sections, skills, indexes, watcher.

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 07-1 | MCP config entry removal | `src/uninstall.py` | 60 | Remove gitnexus + codegraphcontext from all auto-MCP platform configs. Preserves other servers. Deduplicates shared files. |
| P0 | 07-2 | AGENTS.md section removal | `src/uninstall.py` | 50 | Remove gitnexus markers + trailing CGC section. Clean up whitespace. |
| P0 | 07-3 | Skill file removal | `src/uninstall.py` | 30 | Remove .kilo/skills/ + .claude/skills/ dirs. Clean up empty parents. |
| P1 | 07-4 | Index cleanup + watcher stop | `src/uninstall.py` | 40 | Remove .gitnexus/ and .cgc/ dirs. Stop watcher via --stop-watcher. |
| P1 | 07-5 | Dry-run + targeted removal | `src/uninstall.py` | 20 | --dry-run preview. --remove mcp/agents-md/skills/indexes/directives/all. |
| P1 | 07-6 | Slash command + agent | `.kilo/command/combo-uninstall.md`, `.kilo/agent/combo-uninstall.md` | 50 | /combo-uninstall command + agent workflow. |
| Bonus | — | Platform directive cleanup | `src/uninstall.py` | 40 | Remove combo lines from CLAUDE.md, .cursorrules, .clinerules, etc. |

**Total:** 6 tasks (3 P0, 2 P1, 1 bonus). 3 files created, ~290 LOC uninstall + 36 tests.

---

## Phase 08: Distribution & Packaging ✅ COMPLETE

> Make the project easily distributable, installable, and discoverable.

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 08-1 | GitHub Actions CI | `.github/workflows/ci.yml` | 50 | On push: ruff lint + pytest on ubuntu/macos/windows matrix. Block merge if tests fail. |
| P0 | 08-2 | Template-ready clone | `README.md`, `.gitignore` | 10 | Add instructions for using this repo as a GitHub template. Add git-clean script to remove .git and re-init. |
| P1 | 08-3 | Version tagging | `pyproject.toml` | 5 | Semantic versioning strategy. Changelog format. Release checklist in MEMORY.md. |
| P1 | 08-4 | PyPI package | `pyproject.toml` | 20 | Set `tool.uv.package = true`, add `[build-system]`, publish to PyPI. `pip install gitnexus-cgc-combo` → `combo-setup` command. |
| P1 | 08-5 | Pre-commit hooks | `.pre-commit-config.yaml` | 20 | ruff + pytest on commit. Blocks commit if tests fail. |
| P2 | 08-6 | Badge suite | `README.md` | 5 | CI passing, Python version, license badges. |
| P2 | 08-7 | Docker image | `Dockerfile` | 30 | All-in-one image with Node.js + Python + uv + gitnexus + cgc pre-installed. For environments where installing dependencies is painful. |

**Total:** 2 P0, 3 P1, 2 P2. Estimated ~140 LOC + CI configs.

---

## Phase 09: Non-Docker Distribution Channels ✅ COMPLETE

> Docker is unfamiliar to non-technical users. Add four incremental distribution channels
> that require zero container knowledge: Codespaces, npx starter, VS Code extension, standalone binary.

| Priority | Task# | Task | File(s) | LOC | Status |
|----------|-------|------|---------|-----|--------|
| P0 | 09-1 | GitHub Codespaces pre-config | `.devcontainer/devcontainer.json` | 30 | ✅ Complete |
| P1 | 09-2 | `npx` starter | `packages/create-code-intelligence/` | ~450 | ✅ Complete |
| P2 | 09-3 | VS Code / Cursor extension | `packages/vscode-code-intelligence/` | 300 | ✅ Complete |
| P2 | 09-4 | Standalone binary | `packages/standalone/`, `.github/workflows/release.yml` | 300 | ✅ Complete |

**Total:** 1 P0, 1 P1, 2 P2. Estimated ~680 LOC + package configs. 4/4 complete.

### Rollout Order
1. ~~09-1 Codespaces (30 min)~~ ✅ Done
2. ~~09-2 npx Starter (~1 hour)~~ ✅ Done — `bin/create-code-intelligence.js` (209 LOC) + `bin/sync-templates.js` (75 LOC) + README + templates
3. ~~09-3 VS Code Extension (~1 hour)~~ ✅ Done — 5 TS source files (detector/scaffolder/statusBar/commands/extension), sync script, 10 template files, README
4. ~~09-4 Standalone Binary (4 hours)~~ ✅ Done — standalone_entry.py (180 LOC, direct template extraction, env detection, dry-run/overwrite), build.spec (12 bundled src/*.py files, .kilo/skills, platforms, templates, AGENTS.md), release.yml (4-OS build matrix, auto-GH-release on tag), Homebrew formula (25 LOC Ruby), Chocolatey (nuspec + installer.ps1, 30 LOC), Scoop manifest (12 LOC JSON)

Each channel is independent — no channel blocks any other.

---

## Phase 10: Architecture Simplification ✅ COMPLETE

> Full plan: `progress_docs/plans/10-simplification.md`  
> Rationale: `docs/DESIGN_RATIONALE.md`

Reduced codebase from 10 Python scripts (~2,450 LOC) + 8 test files (~2,000 LOC) down to 1 core script (~340 LOC) + 1 test file. Removed Docker, unified CLI, offline mode, watcher health, state tracking, rule extraction, skill generation, AGENTS.md injection, environment detection, uninstall. Aligned with principle: **the agent is the runtime, AGENTS.md is the program, scripts exist only where agents are weak.**

| Priority | Task# | Task | Status |
|----------|-------|------|--------|
| P0 | 10-1 | Delete 10 Python scripts | ✅ Done |
| P0 | 10-2 | Delete 7 test files | ✅ Done |
| P0 | 10-3 | Delete infrastructure files | ✅ Done (Dockerfile, .devcontainer/, .github/, .pre-commit-config.yaml, templates/, packages/) |
| P0 | 10-4 | Clean pyproject.toml | ✅ Done (9→1 entry point, removed dev deps, removed ruff/pytest config) |
| P0 | 10-5 | Expand config_gen.py with setup mode | ✅ Done (~340 LOC, subcommand: detect + config + index + summary) |
| P0 | 10-6 | Update AGENTS.md | ✅ Done (removed setup_combo.py reference, removed template file references, updated watcher instructions) |
| P0 | 10-7 | Update README.md | ✅ Done (simplified architecture tree, two-path explanation, updated design principles) |
| P0 | 10-8 | Update MEMORY.md | ✅ Done (simplified architecture, Phase 10 complete, session log) |
| P1 | 10-9 | Review and update docs/ | ✅ Done (no stale references found in SETUP_GUIDE.md, TOOL_REFERENCE.md, MCP_CONFIGS.md) |
| P1 | 10-10 | Update .gitignore | ✅ Minimal (no stale entries found) |
| P1 | 10-11 | Update progress_docs/plans/full.md | ✅ Done (this file) |
| P1 | 10-12 | End-to-end verification | ⏳ Pending |
| P2 | 10-13 | uvx distribution | Deferred |
| P2 | 10-14 | Standalone binary | Deferred |
| P2 | 10-15 | Re-add watcher management | Deferred |

---

## Deferred Items

| Item | Reason | Revisit When |
|------|--------|-------------|
| Skill generation for non-skill platforms (P2-02-7) | AGENTS.md inline rules are sufficient for behavioral guidance | If demand for Continue.dev/Cursor/Roo Code skills emerges |
| Offline-first mode with bundled configs (P2-05-8) | Network is usually available; offline is edge case | If users in air-gapped environments request it |
| Docker image (P2-08-7) | Adds maintenance burden; most devs have Node+Python | If CI runners or containerized workflows become common |
| Unified CLI (combo.py) + 9 subcommands | Design says one command is enough — config_gen is the engine | If users demand diagnose/uninstall subcommands |
| AGENTS.md injection (inject_agents_md.py) | Agent handles via read+edit; manual users don't need AGENTS.md | If manual users want AGENTS.md written automatically |
| Skill generation (skill_gen.py) | Skills exist as files; agent copies them directly | If skill templates change frequently |
| Rule extraction (rule_extractor.py) | Agent reads AGENTS.md natively | If non-skill platforms need automated behavior injection |
| Bootstrap state tracking (bootstrap_state.py) | Protocol is idempotent; re-running phases is safe | If phase failure recovery becomes a real problem |
| Watcher health CLI (watcher_health.py) | Agent checks with one bash command | If watcher diagnostics need structured JSON output |
| VS Code extension, npx starter, standalone binary, Codespaces | Three products before core is stable | After core is published and demand data exists |
| Environment detection CLI (setup_combo.py) | Agent runs `node --version` etc. natively | If CLI needs structured pre-flight checks |
| Uninstall CLI (uninstall.py) | Agent undoes what it did; manual users delete files | If cleanup becomes a common request |

---

## Execution Order

```
Phase 10 P0 (Simplification) ✅ COMPLETE
    │
    ├── P0-1: Delete 10 scripts ✅
    ├── P0-2: Delete 7 test files ✅
    ├── P0-3: Delete infrastructure files ✅
    ├── P0-4: Clean pyproject.toml ✅
    ├── P0-5: Expand config_gen.py with setup mode ✅
    ├── P0-6: Update AGENTS.md references ✅
    ├── P0-7: Update README.md ✅
    └── P0-8: Update MEMORY.md ✅
    │
    ▼
Phase 10 P1 (Docs & Verify) ✅ PARTIAL
    ├── P1-9: Update docs/ ✅
    ├── P1-10: Update .gitignore ✅
    ├── P1-11: Update progress_docs/plans/full.md ✅
    └── P1-12: End-to-end verification ⏳
    │
    ▼
Phase 10 P2 (Distribution) — deferred
```

**Blockers: None.**

## Immediate Next Actions

**Phase 10 98% COMPLETE.** Architecture simplified to 1 script + 1 test file:
- ~~**P0 — 10-1:** Delete 10 Python scripts from `src/`~~ ✅ Done
- ~~**P0 — 10-2:** Delete 7 test files from `tests/` (keep `test_config_gen.py`)~~ ✅ Done
- ~~**P0 — 10-3:** Delete infrastructure files~~ ✅ Done
- ~~**P0 — 10-4:** Clean `pyproject.toml`~~ ✅ Done
- ~~**P0 — 10-5:** Expand `config_gen.py` with `setup` subcommand~~ ✅ Done
- ~~**P0 — 10-6:** Update `AGENTS.md` references~~ ✅ Done
- ~~**P0 — 10-7:** Update `README.md` architecture section~~ ✅ Done
- ~~**P0 — 10-8:** Update `MEMORY.md` architecture and phase status~~ ✅ Done
- **P1 — 10-12:** End-to-end verification with `uv run combo-setup setup <test-project>`