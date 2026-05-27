---
description: Remove GitNexus + CodeGraphContext — MCP entries, AGENTS.md sections, skills, indexes, directives
agent: combo-uninstall
subtask: true
---

Remove all traces of the GitNexus + CGC combo from this project:

- MCP config entries from all platform config files
- Combo protocol sections from AGENTS.md
- Skill files (.kilo/skills/gitnexus/, .claude/skills/, etc.)
- Index directories (.gitnexus/, .cgc/)
- Platform instruction file directives (CLAUDE.md, .cursorrules, etc.)

Use `--dry-run` to preview without making changes. Use `--stop-watcher` to also kill the CGC background watcher process. Use `--remove mcp` / `--remove agents-md` / `--remove skills` / `--remove indexes` / `--remove directives` for targeted removal.
