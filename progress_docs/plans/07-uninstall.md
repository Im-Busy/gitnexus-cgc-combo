# Phase 07: Uninstall & Cleanup Protocol

## Status: ✅ COMPLETE

### P0 Items

| # | Task | Status | File | LOC |
|---|------|--------|------|-----|
| 07-1 | MCP config entry removal | ✅ | `src/uninstall.py` | 60 | Remove gitnexus + codegraphcontext from all platform MCP configs. Preserves other servers. Handles all 3 format families (mcpServers, mcp, servers). Deduplicates shared config files (`.mcp.json` used by multiple platforms). Skips invalid JSON gracefully. |
| 07-2 | AGENTS.md section removal | ✅ | `src/uninstall.py` | 50 | Remove `<!-- gitnexus:start -->` ... `<!-- gitnexus:end -->` section AND the trailing CGC section (`# CodeGraphContext` through `## Keeping Indexes Fresh`). Cleans up excess whitespace. |
| 07-3 | Skill file removal | ✅ | `src/uninstall.py` | 30 | Removes `.kilo/skills/gitnexus/`, `.kilo/skills/codegraphcontext/`, `.kilo/skills/graph-combo/` and `.claude/skills/` equivalents. Cleans up empty parent directories (`.kilo/skills/`, `.claude/skills/`). |

### P1 Items

| # | Task | Status | File | LOC |
|---|------|--------|------|-----|
| 07-4 | Index cleanup | ✅ | `src/uninstall.py` | 20 | Remove `.gitnexus/` and `.cgc/` directories. Stop watcher process via `--stop-watcher` flag (pgrep/pkill on Unix, Get-Process/taskkill on Windows). |
| 07-5 | Dry-run mode | ✅ | `src/uninstall.py` | 20 | `--dry-run` flag across all removal functions. Previews actions without writing. Per-component `--remove` flag (mcp, agents-md, skills, indexes, directives, all). |
| 07-6 | Slash command + agent | ✅ | `.kilo/command/combo-uninstall.md`, `.kilo/agent/combo-uninstall.md` | 50 | `/combo-uninstall` command. Agent workflow: dry-run → confirm → execute → summary. |

### Platform Directive Removal (Bonus)

Also implemented `remove_platform_directives()` which cleans combo-related lines from:
- `CLAUDE.md`, `.cursorrules`, `.clinerules`, `.roorules`, `.windsurfrules`, `.github/copilot-instructions.md`

If a file becomes empty after removal, it is deleted.

### Tests

`tests/test_uninstall.py` — 36 tests in 7 classes:

| Class | Tests | Covers |
|-------|-------|--------|
| TestRemoveMcpEntries | 7 | Kilo, Claude Code, empty wrapper key, invalid JSON, dry-run, missing files, no combo entries |
| TestRemoveAgentsMdSections | 5 | Full removal with CGC section, no markers, missing file, dry-run, preserves other sections |
| TestRemoveSkillFiles | 8 | gitnexus/cgc/combo skills for Kilo + Claude Code, empty parent dirs, no skill dirs, dry-run, preserves unrelated skills |
| TestRemoveIndexes | 5 | .gitnexus, .cgc, both, no indexes, dry-run |
| TestRemovePlatformDirectives | 6 | .cursorrules, .clinerules, CLAUDE.md, empty file deletion, no directives, dry-run |
| TestStopWatcher | 2 | Dry-run does not crash, returns status |
| TestEdgeCases | 3 | Multiple platforms sharing config, agents.md without CGC section, full dry-run all components |

### Verification

```
ruff check src/uninstall.py tests/test_uninstall.py  → All checks passed
pytest tests/ (full suite)                            → 196 passed
```
