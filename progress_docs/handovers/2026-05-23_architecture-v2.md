# Handover — 2026-05-23: Architecture v2

## Session Summary

Rebuilt the project from a single-platform "one-click install" prototype into a multi-platform **Code Intelligence Bootstrap Kit** with a declarative platform matrix, config generator, and self-identifying 8-phase protocol.

## Verified Working

- [x] `platforms/matrix.json` — 11 platforms, 3 MCP format families, all detection markers correct
- [x] `src/config_gen.py` — `--detect`, `--platform`, `--cgc-path`, `--print`, `--force`, `--list-platforms` all tested
- [x] Merge logic — existing server preserved, gitnexus+cgc added, idempotent re-run skipped
- [x] All 3 format families — mcpServers (Claude/Cursor/Cline/Roo/Continue/Windsurf/Augment), mcp (Kilo/Opencode), servers (Copilot VS Code) produce correct JSON
- [x] `src/setup_combo.py` — shell="pwsh", Python="3.13.12 (via uv)", gitnexus="1.6.4", CGC="0.4.11" all correct
- [x] ruff lint — zero errors
- [x] Zero "one-click" references in entire project

## File Inventory

New files (7):
- `platforms/matrix.json`
- `src/config_gen.py`
- `progress_docs/README.md`
- `progress_docs/current.md`
- `progress_docs/plans/full.md`
- `progress_docs/plans/01-foundation.md`
- `progress_docs/plans/02-skills.md`

Modified files (10):
- `src/setup_combo.py`
- `AGENTS.md`
- `README.md`
- `MEMORY.md`
- `pyproject.toml`
- `docs/SETUP_GUIDE.md`
- `docs/MCP_CONFIGS.md`
- `docs/TOOL_REFERENCE.md`
- `.kilo/kilo.json`
- `.kilo/project-rules.md`

Modified Kilo files (5):
- `.kilo/agent/combo-setup.md`
- `.kilo/agent/combo-diagnose.md`
- `.kilo/command/combo-setup.md`
- (`.kilo/command/combo-diagnose.md` — unchanged, no "one-click" references)
- (`.kilo/global-rules.md` — unchanged, still correct)

Created directories (3):
- `platforms/`
- `progress_docs/`
- `progress_docs/plans/`, `progress_docs/handovers/`, `progress_docs/logs/`, `progress_docs/plans/archived/`

## Design Principles Enforced

| Principle | How |
|-----------|-----|
| Merge, don't replace | `config_gen.py` merges into existing JSON, preserves user servers |
| Detect, don't assume | Platform auto-detection via filesystem markers in matrix.json |
| Idempotent | Re-running `config_gen.py` returns `[SKIP]` if already configured |
| Least intrusive | Only write configs for detected platforms. Meta-directives are 1-3 lines. |
| Cross-platform | Python `pathlib` handles Windows/Unix paths. No shell-specific scripts. |
| No "one-click" language | Rebranded to "Code Intelligence Bootstrap Kit" — agent-provisioned, not user-installed |

## NEXT: Phase 03 — Tests & Validation

1. **P0-03-1**: Write `tests/test_config_gen.py` — merge test (existing server + gitnexus+cgc → preserved)
2. **P0-03-2**: Create test, skip test (idempotent), manual print test
3. **P0-03-3**: Edge cases — invalid JSON backup, missing platform, empty project detection
4. **P0-03-4**: Write `tests/test_setup_combo.py` — shell detection, Python detection, stub filtering
5. **P0-03-5**: Full bootstrap integration test on temp project

Test framework: pytest (already in pyproject.toml dev deps). Create `tests/` directory at project root.

Also:
- Write `progress_docs/plans/03-tests.md` with detailed task breakdown
- Create `.github/workflows/ci.yml` for automated lint+test on push (Phase 08 P0-1, can do early)