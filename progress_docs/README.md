# Progress Documentation

**Project:** Code Intelligence Bootstrap Kit — GitNexus + CodeGraphContext
**Last Updated:** 2026-05-23

---

## Quick Start for Agents

1. **Read `current.md`** — know what was happening when the last session ended
2. **Read `plans/full.md`** — see all phases, deferred items, and pending work
3. **Resume** from the first incomplete P0 task in the phase status table

---

## Phase Map

| # | Phase | Plan | Log | Status |
|---|-------|------|-----|--------|
| 01 | Foundation — Platform Matrix + Config Generator | [plan](plans/01-foundation.md) | [log](logs/01-foundation.md) | ✅ Complete |
| 02 | Portable Skills — Multi-Platform Distribution | [plan](plans/02-skills.md) | [log](logs/02-skills.md) | 🔄 Partially Done |
| 03 | Tests & Validation | [plan](plans/03-tests.md) | [log](logs/03-tests.md) | ⏳ Pending |
| 04 | Watcher Hardening — Survivable Background Process | [plan](plans/04-watcher.md) | [log](logs/04-watcher.md) | ⏳ Pending |
| 05 | Offline & Resilience — Error Recovery + No-Network Mode | [plan](plans/05-offline.md) | [log](logs/05-offline.md) | ⏳ Pending |
| 06 | Agent-Executed Injection — AGENTS.md Section Auto-Writer | [plan](plans/06-injection.md) | [log](logs/06-injection.md) | ⏳ Pending |
| 07 | Uninstall & Cleanup Protocol | [plan](plans/07-uninstall.md) | [log](logs/07-uninstall.md) | ⏳ Pending |
| 08 | Distribution & Packaging | [plan](plans/08-distribution.md) | [log](logs/08-distribution.md) | ⏳ Pending |

## Setups

| Name | Plan | Log | Status |
|------|------|-----|--------|
| Project Bootstrap — Initial File Structure | [plan](plans/setup-bootstrap.md) | [log](logs/setup-bootstrap.md) | ✅ Done |
| Rebrand — One-Click → Bootstrap Kit | [plan](plans/setup-rebrand.md) | [log](logs/setup-rebrand.md) | ✅ Done |

## Evaluations

| Name | Plan | Log | Status | Decision |
|------|------|-----|--------|----------|
| Bundle vs Fetch Distribution Model | [plan](plans/eval-distribution.md) | [log](logs/eval-distribution.md) | ✅ Done | FETCH: npx + uv pip install |

---

## Known Plan Types

| Type | Prefix | Frontmatter Required | When To Use |
|------|--------|---------------------|-------------|
| `phase` | `NN-` | phase, name, status, depends_on, blocks | Multi-step implementation with deliverables and checkpoints |
| `setup` | `setup-` | name, status | Environment, tooling, infrastructure changes |
| `eval` | `eval-` | name, status, criteria, decision | Comparing approaches, making a go/no-go choice |

**Agent Self-Extension:** When encountering a new activity type not in the catalog above:
1. Determine a short `type` name (lowercase, no spaces)
2. Create the plan file with `{type}-{descriptor}.md` naming
3. Add the new type to this catalog table
4. Add a new section in `plans/full.md` for the type

---

## File Conventions

| Convention | Rule |
|------------|------|
| **Folder** | `progress_docs/` — single entry point for all progress tracking |
| **Naming** | Phases: `NN-short-name.md`. Non-phases: `{type}-{descriptor}.md`. All kebab-case. |
| **Plan format** | Markdown + YAML frontmatter for metadata + Markdown tables for tasks |
| **Log format** | Markdown tables — append-only, chronological |
| **Session recovery** | `current.md` — read first, most recent entry at top |
| **Completion marker** | YAML `status: complete` — never rename files |
| **Deferral marker** | YAML `status: deferred` + `deferred_reason` + `revisit_when` |
| **Aggregation** | `plans/full.md` has all phases, deferred items, and pending work |

## Related Files

- `AGENTS.md` — bootstrap protocol (agent instruction source of truth)
- `MEMORY.md` — persistent agent handover state
- `README.md` — human-facing project overview
- `platforms/matrix.json` — platform registry
- `src/config_gen.py` — MCP config generator
- `.kilo/global-rules.md` — universal agent rules
- `.kilo/project-rules.md` — project-specific rules