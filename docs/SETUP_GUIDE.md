# Setup Guide

## What This Is

The **Code Intelligence Bootstrap Kit** gives your AI coding agent a dual knowledge graph of your codebase — GitNexus (impact analysis, safe rename, execution flows) + CodeGraphContext (code search, dead code detection, Cypher queries, visual graph).

| Tool | Language | Best For |
|------|----------|----------|
| **GitNexus** | Node.js (npm) | Impact analysis, safe rename, execution flow tracing |
| **CodeGraphContext** | Python (pip) | Code search, Cypher queries, dead code detection, visual graph |

Together they provide **defense-in-depth code intelligence** — each has strengths the other lacks. The agent enforces impact-analysis-before-edit discipline permanently.

## How to Use

1. **Clone this repo** into your project or alongside it
2. **Open it** in your AI coding tool (Kilo, Claude Code, Cursor, Cline, Roo Code, Windsurf, Continue.dev, Opencode, Augment Code, or GitHub Copilot)
3. **Say:** "/combo-setup" or "set up code intelligence"
4. **The AI agent provisions everything** — installs both tools, generates MCP configs for your platform(s), indexes your project, writes AGENTS.md protocol sections

**You never run any commands manually.** The agent handles everything.

## Prerequisites

The agent checks for these. If any are missing, it guides you:

- **Node.js** >= 18 (for GitNexus)
- **Python** >= 3.10 (uv-managed Python is fine — for CodeGraphContext)
- **uv** (Python package manager — agent can install this)
- **Git** (your project must be a git repo)

## Multi-Platform Support

The kit auto-detects your AI coding platform and generates the correct MCP config format:

| Platform | MCP Config | Skills | Setup |
|----------|:--:|:--:|:--:|
| **Kilo** | Auto (`.kilo/kilo.json`) | Yes | Merges with existing |
| **Claude Code** | Auto (`.mcp.json`) | Yes | Merges with existing |
| **Cursor** | Auto (`.cursor/mcp.json`) | — | Merges with existing |
| **Cline** | Auto (`.cline/mcp.json`) | — | Merges with existing |
| **Roo Code** | Auto (`.roo/mcp.json`) | — | Merges with existing |
| **Continue.dev** | Auto (`.continue/mcpServers/`) | — | Standalone file |
| **Opencode** | Auto (`opencode.json`) | — | Merges with existing |
| **Copilot** | Auto (`.vscode/mcp.json`) | — | Merges with existing |
| **Windsurf** | Manual paste (global) | — | Agent prints config |
| **Augment Code** | Manual paste (global) | — | Agent prints config |

**Principle:** Configs are merged — your existing MCP servers are never touched.

## What the Agent Does (8 Phases)

### Phase 0: Self-Identification
The agent identifies which AI platform it's running under by checking its system prompt, environment, and filesystem markers.

### Phase 1: Environment Detection
Checks your OS, shell, Node.js version, Python version, uv, and git status.

### Phase 2: Install Tools
- GitNexus: verified via `npx gitnexus` (auto-fetches from npm)
- CodeGraphContext: installed via `uv sync` or `uv pip install codegraphcontext`

### Phase 3: Generate MCP Configs
Runs `config_gen.py` which generates the correct JSON for every detected platform. Existing configs are merged — your other MCP servers are preserved.

### Phase 4: Index Your Project
- `npx gitnexus analyze --embeddings --skills` — builds the GitNexus knowledge graph
- `uv run cgc index <your_project>` — builds the CGC graph database

### Phase 5: Start File Watcher
Starts CGC's live watcher so the index auto-updates as you code (cross-platform — Unix background process or PowerShell).

### Phase 6: Write Protocol Sections
Injects the GitNexus + CGC protocol into your project's AGENTS.md (the one file every platform reads). Writes short meta-directives into platform-specific files (CLAUDE.md, .cursorrules, .clinerules, etc.) pointing to AGENTS.md.

### Phase 7: Copy Skills
Copies operational skill files for Kilo (`.kilo/skills/`) or Claude Code (`.claude/skills/`). For all other platforms, the behavioral rules in AGENTS.md are sufficient.

### Phase 8: Verification
Checks index freshness, watcher status, MCP connectivity, and tool versions. Reports any issues.

## After Setup

Your AI agent will:
- Run impact analysis before every edit (`gitnexus_impact`)
- Check change scope before commits (`gitnexus_detect_changes`)
- Use concept search instead of grep (`gitnexus_query` / `cgc find`)
- Find dead code automatically (`cgc analyze dead-code`)
- Use safe rename instead of find-and-replace (`gitnexus_rename`)

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/combo-setup` | Full provisioning: detect → install → config → index → verify |
| `/combo-diagnose` | Health check: index freshness, watcher status, MCP connectivity |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| GitNexus index stale | `npx gitnexus analyze` |
| CGC watcher died | Restart with `uv run cgc watch <project>/src` |
| MCP tools not showing | Check config syntax, restart agent |
| CGC install fails on Windows | `uv pip install codegraphcontext` handles platform deps |
| Windsurf/Augment MCP not working | Must paste config into global MCP settings. Run `uv run python src/config_gen.py --platform <id> --print` |
| Existing config corrupted | `config_gen.py --force` backs up as `.bak` and writes fresh |