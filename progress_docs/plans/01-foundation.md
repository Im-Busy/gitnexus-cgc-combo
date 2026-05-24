---
phase: 01
name: Foundation — Platform Matrix + Config Generator
status: complete
depends_on: []
blocks: [02, 03, 04, 05, 06, 07, 08]
completed: 2026-05-23
---

# Phase 01: Foundation

## Goal

Build the architectural core of the Bootstrap Kit: a declarative platform registry and a multi-format MCP config generator that merges into existing configs. Replace the hand-coded single-platform AGENTS.md with a self-identifying multi-platform protocol.

## Tasks

| Priority | Task# | Task | Status | Notes |
|----------|-------|------|--------|-------|
| P0 | 01-1 | `platforms/matrix.json` | ✅ Done | 11 platforms, 3 MCP format families. Detection markers, merge strategies, skills support, auto/manual flags |
| P0 | 01-2 | `src/config_gen.py` | ✅ Done | `--detect`, `--platform`, `--cgc-path`, `--print`, `--force`, `--list-platforms`. Merge/create/skip/manual modes. |
| P0 | 01-3 | Fix `src/setup_combo.py` | ✅ Done | 3 bugs: shell detection (now pwsh on Windows via PSModulePath), Python detection (filters Windows App Alias stubs, tries uv fallback), stderr version capture |
| P0 | 01-4 | Rewrite `AGENTS.md` | ✅ Done | Phase 0 self-identification table, 8 phases, config_gen.py integration, merge strategy, meta-directive pattern |
| P0 | 01-5 | Rebrand + docs rewrite | ✅ Done | README: "Code Intelligence Bootstrap Kit." SETUP_GUIDE: 10 platforms + 8 phases. MCP_CONFIGS: 3 families + merge behavior. TOOL_REFERENCE: unified. |

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| 3 MCP format families, not 10 individual formats | 8 platforms share `mcpServers`, 2 share `mcp`, 1 uses `servers`. Only need 3 generators. |
| `config_gen.py` as Python script, not inline in AGENTS.md | Testable, maintainable, handles edge cases (invalid JSON backup, merge idempotency). Agent calls it via `uv run python src/config_gen.py`. |
| Merge strategy: never overwrite | Parses existing JSON, adds only gitnexus+cgc entries. Idempotent re-run returns `[SKIP]`. |
| Meta-directives in platform files (CLAUDE.md, .cursorrules, etc.) | 1-3 line redirect to AGENTS.md. Appended at bottom if file exists. Only created for detected platforms. |
| Skills only for Kilo and Claude Code | Only two platforms with native skill systems. Others get behavioral rules inline in AGENTS.md sections. |
| `<PATH_TO_CODEGRAPHCONTEXT_CLONE>` replaced with `"."` | CGC installed via `uv sync` in this repo's `.venv`. Workdir `.` resolves to project root where `uv run cgc` works. |
| No `tool.uv.package = true` | Entry points don't work without packaging. `uv run python src/<script>.py` is cross-platform and always works. |

## Files Modified

```
NEW:
  platforms/matrix.json          (200 LOC)
  src/config_gen.py              (240 LOC)
  progress_docs/                 (directory tree)

MODIFIED:
  src/setup_combo.py             (3 bugs fixed, 130 LOC)
  AGENTS.md                      (full rewrite, 480 LOC)
  README.md                      (rebrand, 90 LOC)
  MEMORY.md                      (architecture update, 120 LOC)
  docs/SETUP_GUIDE.md            (rewrite, 150 LOC)
  docs/MCP_CONFIGS.md            (rewrite, 140 LOC)
  docs/TOOL_REFERENCE.md         (update, 120 LOC)
  pyproject.toml                 (description, removed entry points)
  .kilo/kilo.json                (workdir "." instead of placeholder)
  .kilo/agent/combo-setup.md     (8-phase summary)
  .kilo/agent/combo-diagnose.md  (standardized checks)
  .kilo/command/combo-setup.md   (rebranded)
  .kilo/project-rules.md         (removed "one-click")
```

## Verification

- [x] ruff lint passes on all Python files
- [x] `config_gen.py --list-platforms` shows all 11 platforms
- [x] `config_gen.py --detect` correctly identifies kilo in this project
- [x] `config_gen.py --platform cursor --print` generates correct mcpServers format
- [x] `config_gen.py --platform copilot-vscode --print` generates correct servers format
- [x] `config_gen.py --platform claude-code --cgc-path <path>` substitutes CGC path correctly
- [x] Merge into existing .cursor/mcp.json preserves existing-server, adds gitnexus+cgc
- [x] Idempotent re-run returns `[SKIP]`
- [x] `setup_combo.py` correctly detects pwsh, Python 3.13.12 via uv
- [x] Zero "one-click" references in entire project (grep confirmed)
- [x] All 3 format families produce structurally correct JSON