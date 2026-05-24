---
name: combo-uninstall
description: "Remove GitNexus + CodeGraphContext from your project — MCP entries, AGENTS.md sections, skills, indexes"
agent: combo-uninstall
---

Usage: `/combo-uninstall`

Removes all traces of the GitNexus + CGC combo from your project:
- MCP config entries from all platform config files
- Combo protocol sections from AGENTS.md
- Skill files (`.kilo/skills/gitnexus/`, `.claude/skills/`, etc.)
- Index directories (`.gitnexus/`, `.cgc/`)
- Platform instruction file directives (CLAUDE.md, .cursorrules, etc.)

Use `--dry-run` to preview without making changes.
Use `--stop-watcher` to also kill the CGC background watcher process.
Use `--remove mcp` / `agents-md` / `skills` / `indexes` / `directives` for targeted removal.
