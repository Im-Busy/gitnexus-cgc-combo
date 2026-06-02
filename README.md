# Code Intelligence Bootstrap Kit

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **One sentence, give your AI coding agent superpowers.** Drop this kit into any project, say "/combo-setup", and your agent self-provisions GitNexus + CodeGraphContext — dual knowledge graphs that give it impact analysis, concept search, dead code detection, safe rename, execution tracing, and visual graphs. The agent enforces impact-analysis-before-edit discipline forever after.

## What It Does

Gives your AI coding agent a **dual knowledge graph** of your codebase — two complementary code intelligence engines working together. Instead of grepping blindly through files, your agent can:

- Run impact analysis before every edit ("if I change this function, what breaks?")
- Find code by meaning, not by keyword matching
- Detect dead code automatically
- Safely rename symbols across the entire codebase (understands the call graph, so it never misses a reference)
- Trace full execution flows step-by-step for debugging
- Check change scope before commits (maps git diffs back to affected symbols)
- Query the codebase with Cypher (same graph query language used by Neo4j)
- Visualize module dependencies as an interactive graph

Supports **17 AI coding platforms** out of the box: Kilo, Claude Code, Codex, Cursor, Cline, Roo Code, Continue.dev, Opencode, GitHub Copilot (VS Code + CLI), Windsurf, Augment Code, FactoryAI, Gemini CLI, Hermes, Kiro, Mastra Code, and Pi Agent.

## Quick Start

**You never run a command yourself.** Just open this project in your AI coding tool and ask:

> **`/combo-setup`** *or* **"Set up code intelligence"**

The agent detects your platform, checks your environment, installs both tools, generates platform-correct MCP configs, indexes your codebase, and writes permanent behavioral rules that make it use these tools forever after.

### Option A: GitHub Template

1. Click **"Use this template"** → **"Create a new repository"**
2. Open your new repo in your AI coding tool
3. Say: **`/combo-setup`**

### Option B: Manual Clone

```bash
git clone https://github.com/Im-Busy/gitnexus-cgc-combo.git
cd gitnexus-cgc-combo
rm -rf .git && git init && git add -A && git commit -m "Initial: Code Intelligence Bootstrap Kit"
```

Open in your AI coding tool and say **`/combo-setup`**.

## What Gets Provisioned

| Layer | What | How |
|-------|------|-----|
| **GitNexus** | Impact analysis, safe rename, execution flows, change detection, semantic search (BM25+vectors), Cypher queries, 7 MCP tools | `npx gitnexus@latest` (auto-fetched from npm, no install) |
| **CodeGraphContext** | Code search (name/content/regex), dead code detection, class hierarchy analysis, import analysis, complexity analysis, visual graph, Cypher queries, 21 MCP tools | `uv pip install codegraphcontext` |
| **MCP Configs** | Both tools registered as MCP servers in the correct format for your platform | Auto-generated, merged into existing configs (never overwrites) |
| **Agent Protocol** | AGENTS.md with Always/Never rules — impact-analysis-before-edit, change-check-before-commit, concept-search-instead-of-grep | Injected idempotently into your project |
| **Skills** | 8 operational skills (6 GitNexus + 1 CGC + 1 combo workflow) | Copied to `.kilo/skills/` or `.claude/skills/` |
| **File Watcher** | CGC live watcher auto-updates the graph on file changes | Background process (systemd / launchd / PowerShell) |

## What Each Tool Can Do — Individual Strengths & Limits

### GitNexus — Strengths

| Capability | How |
|------------|-----|
| **Impact analysis** | Given a function/class/method, reports every caller, every execution flow it participates in, and a risk level (LOW/MEDIUM/HIGH/CRITICAL). Answers "what will break if I change this?" |
| **Safe rename** | Graph-assisted multi-file rename — finds all references through the call graph, not text matching. Dry-run mode shows you what will change before anything happens. |
| **Change detection** | Maps `git diff` output to affected symbols. Before committing, tells you exactly which functions and execution flows your changes touched. |
| **Concept search** | Hybrid BM25 + vector embedding search. Ask "how does auth middleware work?" and get ranked results grouped by execution flow, not just file matches. |
| **Symbol context** | 360-degree view of any symbol — all callers, all callees, all execution flows it participates in. |
| **Execution flows** | Maps your entire codebase as business-process flows. Follow a request from entry point through every function call to the response. |

### GitNexus — Limitations

- **Class hierarchy analysis** — Not its strength. Use CGC's `analyze inheritance` instead.
- **Import analysis** — "Who imports this module?" is better answered by CGC.
- **Dead code detection** — CGC has a dedicated `find_dead_code` tool. GitNexus can infer unused code from impact analysis but it's not a first-class feature.
- **Fuzzy code search** — GitNexus excels at semantic/concept search, but exact name or regex matching is CGC's territory.
- **Visual graph** — GitNexus has a web UI graph explorer, but CGC's 2D/3D force graph visualization is richer for module-dependency views.

### CodeGraphContext (CGC) — Strengths

| Capability | How |
|------------|-----|
| **Code search** | Three modes: search by exact name, by regex pattern, or by fuzzy content. Finds functions, classes, variables across 20+ languages. |
| **Dead code detection** | Dedicated tool that finds unreferenced functions, classes, and variables. |
| **Class hierarchy** | Analyzes inheritance chains. "What inherits from BaseModel?" — CGC answers directly. |
| **Import analysis** | "Who imports this module?" and "What does this module import?" — both directions. |
| **Complexity analysis** | Identifies complexity hotspots — functions with high cyclomatic complexity, deep nesting, or large parameter counts. |
| **Visual graph** | Built-in viz server with 2D/3D force graphs. See your module dependency structure as an interactive graph. |
| **Cypher queries** | Read-only Cypher execution. Write arbitrary graph queries if the built-in tools don't cover your exact need. |
| **Registry bundles** | Search and load shared code-intelligence bundles. |

### CGC — Limitations

- **Impact analysis** — CGC's `analyze_code_relationships` can show callers/callees, but it does not report risk levels, execution-flow grouping, or business-process impact. Use GitNexus `impact` for "what breaks?"
- **Safe rename** — CGC has no rename tool. You'd need to manually Cypher-query + find. Use GitNexus `rename` instead.
- **Change detection** — CGC has no git-diff-to-symbol mapping. Use GitNexus `detect_changes` before committing.
- **Semantic/concept search** — CGC's fuzzy search is keyword-based. GitNexus's hybrid BM25+vector search is better for "find me the auth logic" type queries.
- **Execution flows** — CGC builds a structural graph (files, classes, functions, calls). GitNexus additionally maps business-process execution flows through those structures.

## Combined Power — What They Do Together

The two tools are intentionally complementary — one covers the other's gaps. Together they form defense-in-depth code intelligence:

| Situation | Use |
|-----------|-----|
| "What breaks if I change this function?" | **GitNexus** `impact` — blast radius + risk level |
| "What files changed and which symbols are affected?" | **GitNexus** `detect_changes` |
| "Rename `foo()` to `bar()` everywhere" | **GitNexus** `rename` (with `dry_run` first) |
| "Find everywhere authentication logic lives" | **GitNexus** `query` — semantic concept search |
| "Show me everything about `handleRequest`" | **GitNexus** `context` — 360-degree symbol view |
| "What inherits from `BaseController`?" | **CGC** `analyze inheritance` |
| "Who imports the `utils` module?" | **CGC** `analyze imports` |
| "Find all functions named `validate*`" | **CGC** `find name` or `find pattern` |
| "Are there any unused functions?" | **CGC** `analyze dead-code` |
| "Show me a visual graph of module dependencies" | **CGC** `visualize` |
| "Write a custom Cypher query" | Either — both support Cypher |
| "Trace how a login request flows through the system" | **GitNexus** process resources — step-by-step execution flow |
| "Show all callers of `processPayment`" | Either — GitNexus `context` or CGC `analyze_code_relationships` |

Mindset shift: you stop grepping and start querying. Instead of `rg "auth" --include="*.py"`, you ask `gitnexus_query({query: "authentication middleware"})` and get results grouped by execution flow with relevance ranking.

## How It Works — Step by Step

When you say `/combo-setup`, the agent runs 8 phases automatically. Here is what happens under the hood:

### Phase 0: Platform Self-Identification
The agent checks its own system prompt, environment variables, and filesystem markers to determine which AI coding platform it is running under. It supports 17 platforms with a declarative detection system — each platform has a set of filesystem markers (e.g., `.kilo/` + `kilo.json` for Kilo, `.mcp.json` + `CLAUDE.md` for Claude Code).

### Phase 1: Environment Detection
Checks your OS, shell, Node.js version, Python version, uv, and git. Reports any missing prerequisites and guides installation. If Python is missing, `uv python install 3.13` auto-handles it.

### Phase 2: Install Tools
- **GitNexus** — No install. `npx gitnexus@latest` auto-fetches from npm. Run `npx gitnexus --version` to verify.
- **CodeGraphContext** — `uv sync` installs from `pyproject.toml` dependencies, or `uv pip install codegraphcontext` for global install.

### Phase 3: Generate MCP Configs
Runs `config_gen.py` which reads `platforms/matrix.json` — a declarative registry of all 17 supported platforms — and generates the correct MCP server JSON for each detected platform. Three format families are handled automatically: `mcpServers` (14 platforms like Cursor, Windsurf, Codex, Factory), `mcp` (Kilo, Opencode, Kiro), and `servers` (GitHub Copilot VS Code). Generated configs are **merged** into existing config files — your other MCP servers are preserved untouched. Idempotent: re-running returns `[SKIP]`.

### Phase 4: Index Your Project
- `npx gitnexus analyze --embeddings --skills` builds the GitNexus knowledge graph with embeddings for semantic search and skill files for agent guidance.
- `uv run cgc index <your_project>` builds the CGC structural graph database (files, functions, classes, calls, imports, inheritance).

### Phase 5: Start CGC Live Watcher
Starts a background process that monitors `src/` for file changes and auto-updates the CGC graph. Platform-specific: systemd user service on Linux, launchd plist on macOS, PowerShell background process on Windows. Survives terminal close and auto-restarts on failure.

### Phase 6: Write Agent Protocol Sections
Extracts the GitNexus + CGC behavioral protocol template from this repo's AGENTS.md, substitutes actual index stats (symbol count, relationship count, execution flow count), and idempotently injects it into your project's AGENTS.md using `<!-- gitnexus:start -->` / `<!-- gitnexus:end -->` markers. Writes short meta-directives into platform-specific instruction files (`CLAUDE.md`, `.cursorrules`, `.clinerules`, etc.) pointing the agent to AGENTS.md.

### Phase 7: Copy Operational Skills
Copies 8 skill files to your project. For Kilo: `.kilo/skills/`; for Claude Code: `.claude/skills/`; for Codex: `.codex/skills/`; for OpenCode: `.opencode/skills/`; similarly for FactoryAI, Gemini, Hermes, Kiro, Mastra, and Pi. Skills cover: exploring architecture, impact analysis, debugging, refactoring, CLI operations, tool reference (GitNexus), CGC graph queries, and unified combo workflow. Other platforms get behavioral rules embedded in AGENTS.md instead.

### Phase 8: Verification
Runs a full health check: GitNexus index freshness, CGC index stats, watcher process status, tool versions, and MCP connectivity. Reports a summary of what passed and what needs attention.

## Multi-Platform Support

The bootstrap kit auto-detects your AI coding platform and generates the correct MCP config format. Each platform has a different config schema, file location, and merge strategy — all handled automatically:

| Platform | MCP Family | Config File | Skills | Detection Markers |
|----------|-----------|-------------|:--:|-------------------|
| **Kilo** | `mcp` | `.kilo/kilo.json` | Yes | `.kilo/`, `kilo.json` |
| **Claude Code** | `mcpServers` | `.mcp.json` | Yes | `.mcp.json`, `CLAUDE.md` |
| **Codex** | `mcpServers` | `.mcp.json` | Yes | `.codex/` |
| **Cursor** | `mcpServers` | `.cursor/mcp.json` | — | `.cursor/`, `.cursorrules` |
| **Cline** | `mcpServers` | `.cline/mcp.json` | — | `.cline/`, `.clinerules` |
| **Roo Code** | `mcpServers` | `.roo/mcp.json` | — | `.roo/`, `.roorules` |
| **Continue.dev** | `mcpServers` | `.continue/mcpServers/gitnexus-cgc.json` | — | `.continue/`, `config.yaml` |
| **Opencode** | `mcp` | `opencode.json` | Yes | `opencode.json`, `.opencode/` |
| **Copilot (VS Code)** | `servers` | `.vscode/mcp.json` | — | `.vscode/mcp.json` |
| **Copilot (CLI)** | `mcpServers` | `.mcp.json` | — | `.mcp.json` (shared detection) |
| **Windsurf** | `mcpServers` | Manual paste (global) | — | `.windsurf/`, `.windsurfrules` |
| **Augment Code** | `mcpServers` | Manual paste (global) | — | `.augment/` |
| **FactoryAI** | `mcpServers` | `.mcp.json` | Yes | `.factory/` |
| **Gemini CLI** | `mcpServers` | `.mcp.json` | Yes | `.gemini/` |
| **Hermes** | `mcpServers` | `.mcp.json` | Yes | `.hermes/` |
| **Kiro** | `mcp` | `kiro.json` | Yes | `.kiro/`, `kiro.json` |
| **Mastra Code** | `mcpServers` | `.mcp.json` | Yes | `.mastracode/` |
| **Pi Agent** | `mcpServers` | `.mcp.json` | Yes | `.pi/` |

MCP configs use **merge-into-existing** strategy (15 platforms), **create-standalone-file** (Continue.dev), or **print-for-manual-paste** (Windsurf, Augment — both lack project-level MCP support). Existing MCP servers are never touched.

## Architecture & Technical Implementation

### How the Bootstrap System Works

This project is an **agent-native provisioning system** — the product is the protocol, not the executables. The AI agent reads AGENTS.md as its instruction manual and executes all 8 phases autonomously. The user never runs a command.

```
gitnexus_CGC_combo/
├── AGENTS.md                 # The program — 8-phase bootstrap protocol for the agent
├── README.md                 # Human-facing overview (this file)
├── pyproject.toml            # Single entry point: combo-setup
├── platforms/
│   └── matrix.json           # Declarative platform registry (17 platforms, 3 MCP families)
├── src/
│   └── config_gen.py         # MCP config engine + setup orchestrator (~300 LOC)
├── tests/
│   └── test_config_gen.py    # Config generation tests
├── .kilo/
│   ├── kilo.json             # This project's own MCP config
│   ├── global-rules.md       # Agent behavioral standards
│   ├── project-rules.md      # Combo-specific rules
│   ├── agent/                # 3 agent definitions (combo-setup, combo-diagnose, combo-uninstall)
│   ├── command/              # 3 slash command manifests
│   └── skills/               # 8 operational skills (6 GitNexus + 1 CGC + 1 combo workflow)
└── docs/
    ├── DESIGN_RATIONALE.md   # Design decisions and rationale
    ├── SETUP_GUIDE.md        # User-facing setup walkthrough
    ├── TOOL_REFERENCE.md     # Complete tool-by-tool reference
    └── MCP_CONFIGS.md        # MCP config format reference (all 3 families)
```

### Core Design: Platform Matrix

At the heart of the config generation system is `platforms/matrix.json` — a declarative JSON registry that maps each AI coding platform to its MCP config format, file path, detection markers, and capabilities. Instead of hardcoding platform-specific logic, `config_gen.py` reads this matrix and generates the correct JSON for any platform. Adding a new platform requires only a new entry in the matrix — no code changes needed.

Three MCP format families are supported:

| Family | Top-Level Key | Server Type | Platforms |
|--------|--------------|-------------|-----------|
| `mcpServers` | `"mcpServers"` | `command` + `args` + `cwd` | 14 (Claude Code, Codex, Cursor, Cline, Roo Code, Continue, Windsurf, Augment, Copilot CLI, Factory, Gemini, Hermes, Mastra, Pi) |
| `mcp` | `"mcp"` | `"type": "local"`, `command` array + `workdir` | 3 (Kilo, Opencode, Kiro) |
| `servers` | `"servers"` | `"type": "stdio"`, `command` + `args` + `cwd` | 1 (GitHub Copilot VS Code) |

Each family has subtly different JSON structure, key names, and semantics. The matrix handles all three.

### Merge Strategy

Config generation never overwrites. When a config file already exists:
1. Parses existing JSON
2. Adds only `gitnexus` and `codegraphcontext` entries
3. Preserves all user's other MCP servers untouched
4. Re-running returns `[SKIP]` — fully idempotent

If the existing JSON is corrupted, `--force` backs it up as `.bak` and writes fresh.

### Two-Path Architecture

The single engine (`config_gen.py` + `platforms/matrix.json`) serves two paths:

- **Agent Path:** The AI agent reads AGENTS.md and executes phases directly — runs `bash` for commands, uses `read`/`edit` for file operations, uses `glob` for file copying. No scripts needed.
- **Manual Path:** Users who don't use AI coding tools run `uvx gitnexus-cgc-combo setup ./` — a single command that generates MCP configs, indexes both tools, and prints a summary.

### Agent-Executed Operations

All non-config phases are performed by the agent directly — no scripts:
- **Environment detection** — `node --version`, `python --version`, etc. via `bash`
- **Template injection** — Agent reads AGENTS.md template, substitutes variables, uses `edit` to inject into target project
- **Skill copying** — Agent enumerates `.kilo/skills/` directories and copies to target
- **Verification** — Agent runs `npx gitnexus status`, `uv run cgc stats`, and `pgrep`/`Get-Process` for watcher checks
- **Uninstall** — Agent performs inverse of setup operations (delete JSON keys, delete file sections, stop processes)
- **Watcher management** — Agent starts `uv run cgc watch` as background process (systemd/launchd/PowerShell documented in AGENTS.md Phase 5)

## Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Agent-native** | The protocol IS the product. The agent reads AGENTS.md and provisions everything autonomously. Scripts exist only where agents are weak (structured JSON generation). |
| **Merge, don't replace** | MCP configs are merged into existing files. User's other servers are preserved. AGENTS.md sections use marker fences for safe injection. |
| **Detect, don't assume** | Platform auto-detection via filesystem markers. Environment auto-detection via command probing. No guessing. |
| **Idempotent everywhere** | `<!-- gitnexus:start -->` markers prevent duplicate injection. `config_gen.py` returns `[SKIP]` on re-run. All phases are safe to re-run. |
| **Least intrusive** | Only writes configs for detected platforms. Meta-directives in platform files are 1-3 lines. Skill files go in dedicated directories. |
| **Cross-platform from the ground up** | Python `pathlib` handles Windows/Unix paths. Matrix handles 3 MCP format families. Watcher instructions cover systemd, launchd, and PowerShell. |
| **Two paths, one engine** | Agent reads AGENTS.md (the protocol). Manual users run `uvx combo-setup setup .` (the CLI). Both use `config_gen.py` for MCP config generation. |

## Prerequisites

| Prerequisite | Required | Auto-Installed |
|-------------|:--:|:--:|
| Node.js >= 18 | Yes | No (agent guides you) |
| Python >= 3.10 | Yes | Yes — `uv python install 3.13` |
| uv | Yes | Yes — `pip install uv` or curl installer |
| Git | Yes | No (agent guides you) |
| Internet (first run) | Yes | — |

The setup agent auto-detects missing prerequisites and guides installation step-by-step. uv-managed Python is fully supported — no system Python needed.

## After Setup — What Your Agent Does Forever

Once provisioned, your AI agent follows these rules permanently (enforced by the protocol injected into AGENTS.md):

| When | What Happens |
|------|-------------|
| **Before editing any function/class/method** | Runs `gitnexus_impact()` — shows blast radius (direct callers, affected processes) and risk level. Warns you if HIGH or CRITICAL risk. |
| **Before committing** | Runs `gitnexus_detect_changes()` — maps `git diff` to affected symbols and execution flows. Verifies changes only affect expected scope. |
| **Exploring unfamiliar code** | Uses `gitnexus_query()` or `cgc find` instead of grep. Concept-based search returns results grouped by execution flow, ranked by relevance. |
| **Renaming a symbol** | Uses `gitnexus_rename()` instead of find-and-replace. Graph-assisted — finds all references through the call graph, not text matching. |
| **Tracing a bug** | Uses `gitnexus` process resources to follow execution flows step-by-step. |
| **Finding dead code** | Uses `cgc analyze dead-code` to find unreferenced symbols. |
| **Understanding class hierarchy** | Uses `cgc analyze inheritance` to map inheritance chains. |
| **Custom graph queries** | Uses `cypher` (either tool) for arbitrary graph pattern matching. |

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/combo-setup` | Full provisioning: platform detection → environment check → install → MCP config → index → watcher → AGENTS.md injection → verification |
| `/combo-diagnose` | Health check: index freshness, watcher process status, MCP tool connectivity, tool versions |
| `/combo-uninstall` | Remove everything: MCP entries, AGENTS.md sections, skill files, indexes, platform directives, stop watcher. Dry-run supported. |

## License

MIT
