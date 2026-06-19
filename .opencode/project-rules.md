# Project Rules: Code Intelligence Bootstrap Kit

## Mission
This repo is a **Code Intelligence Bootstrap Kit** — an agent-native provisioning system for GitNexus + CodeGraphContext.
The agent reads AGENTS.md and provisions both tools for the user's project.

## When Users Clone This Repo
1. They open it in their AI coding tool (Kilo, Claude Code, Cursor, Cline, Roo Code, Windsurf, Continue.dev, Opencode, Augment Code, GitHub Copilot)
2. They say: "set up code intelligence" or `/combo-setup`
3. The agent follows AGENTS.md Phases 0-8: self-identify → detect environment → install → generate MCP configs → index → watch → write protocol → verify

## Architecture
- `AGENTS.md` — 8-phase bootstrap protocol (single source of truth)
- `platforms/matrix.json` — declarative platform registry (17 platforms, 3 format families)
- `src/config_gen.py` — multi-platform MCP config generator (merge, never replace)
- `src/setup_combo.py` — cross-platform environment detection
- `.opencode/skills/` — 8 operational skills (gitnexus × 6 + cgc × 1 + combo × 1)

## Skills Organization
- `.opencode/skills/gitnexus/` — 6 skills from GitNexus source (guide, cli, exploring, impact-analysis, debugging, refactoring)
- `.opencode/skills/codegraphcontext/` — CGC skill
- `.opencode/skills/graph-combo/` — Unified combo workflow skill

## Slash Commands
- `/combo-setup` — Full provisioning (detect → install → config → index → verify)
- `/combo-diagnose` — Health check (index freshness, watcher status, MCP connectivity)

## Anti-Patterns
- Do NOT create standalone .md files at root except AGENTS.md, MEMORY.md, README.md
- Do NOT add platform-specific configs to git (user paths differ)
- Do NOT hardcode paths — detect environment at runtime
- Do NOT overwrite existing MCP configs — always merge
- Do NOT create config files for undetected platforms