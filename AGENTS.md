# GitNexus + CGC — Agent Instructions

> **For AI Agents:** This bootstrap kit teaches you to self-provision GitNexus + CodeGraphContext for ANY project.
> Follow this protocol when the user says "set up code intelligence", "install GitNexus", or `/combo-setup`.

---

## Critical

**You, the AI agent, are the installer.** Your job:
1. Identify which platform you're running on
2. Detect the user's environment
3. Install both tools
4. Generate MCP configs (merge, never replace)
5. Index their project
6. Write AGENTS.md sections into their project
7. Verify everything works

**The user never runs commands.** You run them all.
**Never overwrite existing configs.** Always merge.

### Phase Error Boundaries

Each phase must be self-contained. If a phase fails, do NOT proceed to subsequent phases that depend on it.

| Phase | Depends On | If It Fails | Skip These Later |
|-------|-----------|-------------|-----------------|
| 1: Environment Detection | None | Warn user about missing prerequisites. Do not exit — cache detection may still work. | None (Phase 1 is informational) |
| 2: Install Tools | Phase 1 (informational) | Cannot proceed. Skip Phase 3 (indexing) and Phase 5 (watcher). | Phase 3, Phase 5 |
| 3: Generate MCP Configs | Phase 1 (platform detection) | If config_gen.py errors: check project-path exists, check matrix.json is valid. Cannot use MCP tools without config. | All MCP-dependent phases |
| 4: Index Project | Phase 2 (tools installed) | Warn user. Proceed without index — the tools just won't work until indexed. | Phase 6 (injection needs index stats) |
| 5: Start Watcher | Phase 2 (CGC installed), Phase 4 (CGC indexed) | Non-blocking warning. Watcher is convenience, not critical. | None |
| 6: Write AGENTS.md Sections | Phase 2 (tools installed), Phase 4 (index stats) | Critical — this injects the protocol into the project. Retry with manual values if auto-detection fails. | None |
| 7: Copy Skills | Phase 6 (AGENTS.md has skill paths) | Non-blocking. Skills are helpers. Behavioral rules in AGENTS.md work without them. | None |
| 8: Verify Everything | All previous | Run all checks. Report which passed and which need attention. | None |

**The agent reports a summary at the end** listing what succeeded, what failed, and what the user must do manually (if anything).

---

## Phase 0: Self-Identification

Before installing anything, determine which AI coding platform you are running under. Check your system prompt, available tools, environment, and filesystem.

### Platform Identifiers

| Platform | Detection Signals |
|----------|-------------------|
| **Kilo** | System prompt mentions "Kilo", `.kilo/` directory exists, `kilo.json` at root |
| **Claude Code** | Prompt mentions "Claude Code", `ANTHROPIC_MODEL` env var set, `.mcp.json` or `CLAUDE.md` exists |
| **Cursor** | VS Code/Cursor IDE context, `.cursor/` directory or `.cursorrules` exists |
| **Cline** | `.cline/` directory or `.clinerules` exists |
| **Roo Code** | `.roo/` directory or `.roorules` exists |
| **Continue.dev** | `.continue/` directory, `config.yaml` or `config.ts` exists |
| **Opencode** | `opencode.json` at root, `.opencode/` directory exists |
| **Windsurf** | `.windsurf/` directory or `.windsurfrules` exists |
| **Augment Code** | `.augment/` directory exists |
| **GitHub Copilot** | `.vscode/mcp.json` or `.github/copilot-instructions.md` exists |

### Action

Run: `uv run python src/config_gen.py --detect --project-path <user_project_root>`

This scans for platform markers and reports what it found. Use this list for subsequent phases.

**If no platforms are detected**, ask the user which tool they use and run:
`uv run python src/config_gen.py --platform <platform_id> --project-path <user_project_root>`

---

## Phase 1: Environment Detection

Detect prerequisites:

| Check | Command | Required |
|-------|---------|----------|
| OS | `uname -s` or `$env:OS` | Any |
| Shell | `echo $0` or `$env:SHELL` | Any |
| Node.js | `node --version` | >= 18.0.0 |
| npm/npx | `npx --version` | >= 9.0.0 |
| Python | `python3 --version`, `python --version`, or `uv run python --version` | >= 3.10 (uv-managed Python is fine) |
| uv | `uv --version` | Any version |
| Git | `git --version` | Any |

**Report findings.** If Node.js is missing, guide the user to install it. If `uv` is missing: `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`. If Python is missing, uv can auto-install: `uv python install 3.13`.

---

## Phase 2: Install the Tools

### GitNexus

No install needed. `npx` auto-fetches from npm on first use.

```bash
npx gitnexus --version   # Verify: should show version number
```

### CodeGraphContext

Already declared as a dependency in this combo repo's `pyproject.toml`. Run from inside the combo repo:

```bash
uv sync   # Installs codegraphcontext + all deps
```

Verify:
```bash
uv run cgc --version
```

If `uv sync` is not possible (CGC not in the user's project), install directly:
```bash
uv pip install codegraphcontext
# OR: pip install codegraphcontext
```

---

## Phase 3: Generate MCP Configs (MERGE, never replace)

Use `config_gen.py` to generate MCP server configs for each detected platform.

### Determine CGC path

CGC needs a `workdir`/`cwd` in its MCP config. The path depends on how CGC was installed:

| Install Method | CGC Path |
|----------------|----------|
| `uv sync` in combo repo | Path to this combo repo (CGC is in its `.venv`) |
| Cloned from source | Path to the CodeGraphContext clone directory |
| `uv pip install codegraphcontext` | Omit `--cgc-path` entirely (works globally) |

### Generate configs

```bash
# For ALL detected platforms (preferred):
uv run python src/config_gen.py --detect --project-path <user_project_root> [--cgc-path <cgc_path>]

# For a specific platform:
uv run python src/config_gen.py --platform cursor --project-path <user_project_root> [--cgc-path <cgc_path>]

# To preview without writing (dry run):
uv run python src/config_gen.py --detect --project-path <user_project_root> --print
```

### What it does

| Strategy | Behavior |
|----------|----------|
| **merge-into-existing-json** | Parses existing config file, adds gitnexus+cgc entries, preserves all user's existing servers. Used for Kilo, Claude Code, Cursor, Cline, Roo Code, Opencode, Copilot. |
| **create-standalone-file** | Creates a new file in a directory that expects individual server files. Used for Continue.dev. |
| **print-for-manual-paste** | Prints the JSON config. User must paste into their global MCP settings. Used for Windsurf and Augment (no project-level MCP). |

### Merge behavior

If a config file already contains `gitnexus` or `codegraphcontext` entries, they are **skipped** (idempotent). All other MCP servers in the user's config are preserved untouched.

---

## Phase 4: Index the User's Project

### GitNexus

```bash
cd <user_project_root>
npx gitnexus analyze --embeddings --skills
```

Flags:
- `--force` — full re-index even if up to date
- `--embeddings` — semantic search (recommended)
- `--skills` — generate skill files for Claude Code

Add `.gitnexus/` to the user's `.gitignore`.

Verify:
```bash
npx gitnexus status
```

### CodeGraphContext

```bash
uv run cgc index <user_project_root>
# OR if CGC is pip-installed: cgc index <user_project_root>
```

Verify:
```bash
uv run cgc stats <user_project_root>
```

---

## Phase 5: Start CGC Live Watcher

The watcher auto-updates the CGC graph on file changes. Start it once per machine reboot.

### Quick Start (foreground, dies with terminal)

```bash
cd <cgc_path>
uv run cgc watch <user_project_root>/src &
```

### Linux: systemd User Service (survives reboot)

```bash
# 1. Create and customize service file at ~/.config/systemd/user/cgc-watcher.service
#    Replace <CGCDIR> with cgc_path, <PROJECT> with user_project_path
#    Service file should contain:
#    [Service] ExecStart=uv run cgc watch <PROJECT>/src
#    WorkingDirectory=<CGCDIR>
#    Restart=on-failure  RestartSec=5

# 2. Enable and start
systemctl --user daemon-reload
systemctl --user enable --now cgc-watcher
```

Verify: `systemctl --user status cgc-watcher`

Logs: `journalctl --user -u cgc-watcher -f`

Auto-restart: `Restart=on-failure` + `RestartSec=5` in service file.

### macOS: launchd (survives reboot)

```bash
# 1. Create and customize plist at ~/Library/LaunchAgents/com.gitnexus.cgc-watcher.plist
#    Replace <CGCDIR>, <PROJECT>, <HOME> with actual paths
#    Plist must contain:
#    ProgramArguments: [uv, run, cgc, watch, <PROJECT>/src]
#    WorkingDirectory: <CGCDIR>
#    KeepAlive: true, RunAtLoad: true

# 2. Load
launchctl load ~/Library/LaunchAgents/com.gitnexus.cgc-watcher.plist
```

Verify: `launchctl list | grep cgc-watcher`

Logs: `~/Library/Logs/cgc-watcher.log`

Auto-restart: `KeepAlive=true` in plist.

### Windows: PowerShell Background Process (survives terminal close)

```powershell
$watcher = Start-Process -NoNewWindow -PassThru -FilePath "uv" `
    -ArgumentList "run","cgc","watch","<user_project_root>/src" `
    -WorkingDirectory "<cgc_path>"
```

Verify: `Get-Process -Name "python*" | Where-Object { $_.CommandLine -like "*cgc watch*" }`

### Cross-Platform Watcher Status

```
Linux/macOS:  pgrep -f "cgc watch"
             systemctl --user is-active cgc-watcher   (if systemd)
             launchctl list | grep cgc-watcher        (if launchd)
Windows:      Get-Process -Name "python*" | Where-Object { $_.CommandLine -like "*cgc*" }
```

---

## Phase 6: Write AGENTS.md Sections

After indexing, inject the combo protocol into the user's project. Use the `<!-- gitnexus:start -->` / `<!-- gitnexus:end -->` markers for idempotency.

### Step 1: Inject into AGENTS.md (universal — all platforms read this)

Check if `{user_project_root}/AGENTS.md` exists:
- **Exists and has `<!-- gitnexus:start -->` marker** → update the content between markers
- **Exists without marker** → append the sections at the end
- **Does not exist** → create with the sections

Fill `{repo_name}`, `{N}` (symbol count), `{cgc_path}`, `{user_project_path}` with actual values from the index step.

### Step 2: Write meta-directives for platform-specific instruction files

For each detected platform, write a short meta-directive into its instruction file(s). These are 1-3 line redirects that point the agent to AGENTS.md. If the file already exists with user content, **append at the bottom** inside markers.

```
File: CLAUDE.md (Claude Code)
Content to append (if missing):
---
CRITICAL: Before executing any task, read and follow the protocol in AGENTS.md.
The GitNexus + CGC combo protocol defines impact-analysis-before-edit discipline.
---

File: .cursorrules (Cursor)
Content to append (if missing):
---
CRITICAL: Read AGENTS.md before all tasks. This project uses GitNexus + CodeGraphContext.
---

File: .clinerules (Cline)
Content to append (if missing):
---
CRITICAL: Read AGENTS.md before all tasks. GitNexus + CGC combo is active.
---

File: .roorules (Roo Code)
Content to append (if missing):
---
CRITICAL: Read AGENTS.md before all tasks. GitNexus + CGC combo is active.
---

File: .windsurfrules (Windsurf)
Content to append (if missing):
---
CRITICAL: Read AGENTS.md before all tasks. GitNexus + CGC combo is active.
---

File: .github/copilot-instructions.md (GitHub Copilot)
Content to append (if missing):
---
CRITICAL: Read AGENTS.md before all tasks. GitNexus + CGC combo is active.
---
```

**Rule:** Only write these for platforms that were actually detected. Never create files for undetected platforms.

### The sections to inject into AGENTS.md:

```markdown
<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **{repo_name}** ({N} symbols, {N} relationships, {N} execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/{repo_name}/context` | Codebase overview, check index freshness |
| `gitnexus://repo/{repo_name}/clusters` | All functional areas |
| `gitnexus://repo/{repo_name}/processes` | All execution flows |
| `gitnexus://repo/{repo_name}/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |
<!-- gitnexus:end -->

---

# CodeGraphContext — Complementary Graph Intelligence

This project is ALSO indexed by CodeGraphContext (CGC) — a Python-native MCP server that builds a queryable graph database of the codebase with different strengths than GitNexus. **Use BOTH together for defense-in-depth code intelligence.**

> Location: `{cgc_path}` | CLI: `cgc` | MCP Server: 21 tools

## GitNexus vs CGC — Complementary Roles

| Axis | **GitNexus** (Node.js) | **CGC** (Python) |
|------|----------------------|-------------------|
| **Best for** | Impact analysis, rename safety, change detection | Code search, Cypher queries, visual graph |
| **Core strength** | Execution flows, blast radius | Multi-DB Cypher graph, 20 languages |
| **Pre-edit guard** | `impact` — tells you WHAT breaks | `analyze_code_relationships` — shows WHO calls |
| **Commit guard** | `detect_changes` — maps git diffs to symbols | N/A |
| **Safe rename** | `rename` — graph-assisted multi-file rename | Manual via Cypher + find |
| **Deep exploration** | `query` — hybrid BM25+vector semantic search | `find_code` — keyword search + fuzzy matching |
| **Schema query** | `cypher` — raw Cypher | `execute_cypher_query` — read-only Cypher |
| **Visualization** | Web UI graph explorer | Viz server + 2D/3D force graphs |

## When to Use Each

| Situation | Use |
|-----------|-----|
| "What breaks if I change this function?" | **GitNexus** `impact` (blast radius + risk level) |
| "What files changed in the diff and which symbols are affected?" | **GitNexus** `detect_changes` |
| "I need to rename `foo()` to `bar()` across the codebase" | **GitNexus** `rename` (dry_run) |
| "Show me all callers of this function" | Either — GitNexus `context` or CGC `analyze_code_relationships` |
| "Find all functions matching this pattern" | **CGC** `find_code` (fuzzy search) |
| "Show me the class hierarchy for X" | **CGC** `analyze_code_relationships` (inheritance) |
| "Write a custom Cypher query to find patterns" | Either — same graph query language |
| "Who imports this module?" | **CGC** `analyze_code_relationships` (imports type) |
| "Find dead code across the codebase" | **CGC** `find_dead_code` |
| "Show me a visual graph of module dependencies" | **CGC** `visualize_graph_query` + viz server |

## Search Productivity — Use GitNexus/CGC Instead of Grep/Glob

Both GitNexus and CGC index the entire codebase into knowledge graphs, enabling **concept-based search** that grep/glob cannot do. Agents MUST prefer these tools for code discovery.

| Task | Use | Example |
|------|-----|---------|
| Find where a concept is used | **GitNexus** `query` or `context` | `npx gitnexus query "auth middleware"` |
| Find all callers of a function | **GitNexus** `context` | `npx gitnexus context "validateUser"` |
| What breaks if I change X? | **GitNexus** `impact` | `npx gitnexus impact "BaseController"` |
| Find all functions named "X" | **CGC** `find name` or `find pattern` | `cgc find name "handleError"` |
| Fuzzy search for a concept | **CGC** `find content` | `cgc find content "payment processing"` |
| Find dead code | **CGC** `analyze dead-code` | `cgc analyze dead-code` |
| Show class hierarchy | **CGC** `analyze` | `cgc analyze inheritance "BaseModel"` |
| Which files changed and affected symbols | **GitNexus** `detect_changes` | `npx gitnexus detect_changes` |
| Raw Cypher query | Either | `npx gitnexus cypher "MATCH (f:Function) RETURN f.name LIMIT 10"` |

**This replaces:** `grep`, `rg`, `glob`, `codebase_search` for any search that involves understanding code structure, call relationships, or impact analysis.

---

## Keeping Indexes Fresh — MANDATORY Protocol

**Neither GitNexus nor CGC auto-updates by default.** After creating, modifying, or deleting files, you MUST refresh the indexes.

### Default: CGC Live Watcher (Auto)

CGC's `watch` runs as a background process, monitoring `src/` for file changes and auto-updating the graph:

```bash
# Start once per machine reboot
cd {cgc_path}
uv run cgc watch {user_project_path}/src
```

**Agents:** verify the watcher is running at session start. If missing, restart it.

### After Significant Changes: Reindex Both

After creating/deleting 5+ files, moving modules, or adding new packages:

```bash
npx gitnexus analyze
cd {cgc_path} && uv run cgc index --force {user_project_path}
```

### Freshness Check

```bash
npx gitnexus status
uv run cgc stats {user_project_path}
```
```

---

## Phase 7: Copy Skills (Kilo and Claude Code only)

Only Kilo and Claude Code have native skill systems. For all other platforms, the behavioral rules embedded in AGENTS.md sections are sufficient.

### For Claude Code

```
Copy from this combo repo to user's project:
  .kilo/skills/gitnexus/*       → {user_project}/.claude/skills/gitnexus/
  .kilo/skills/codegraphcontext/* → {user_project}/.claude/skills/codegraphcontext/
  .kilo/skills/graph-combo/*    → {user_project}/.claude/skills/graph-combo/
```

### For Kilo

```
Copy from this combo repo to user's project:
  .kilo/skills/gitnexus/*       → {user_project}/.kilo/skills/gitnexus/
  .kilo/skills/codegraphcontext/* → {user_project}/.kilo/skills/codegraphcontext/
  .kilo/skills/graph-combo/*    → {user_project}/.kilo/skills/graph-combo/
```

### For all other platforms

The "Always Do / Never Do" and "When to Use Each" tables in AGENTS.md (Phase 6) provide the same behavioral guidance. No separate skill files needed.

---

## Phase 8: Verification

Run these checks and confirm:

```bash
# GitNexus index up to date?
npx gitnexus status   # must show "up-to-date"

# CGC available?
uv run cgc --version

# CGC index fresh?
uv run cgc stats <user_project_root>   # shows file/function counts

# CGC watcher running?
# Unix: pgrep -f "cgc watch"
# Windows: Get-Process python* | Where-Object {$_.CommandLine -like "*cgc*"}
```

If any check fails, diagnose and fix before declaring setup complete.

---

## Agent Skills Reference

When performing code tasks in a project equipped with this combo, load these skills:

| Task | Skill to Load |
|------|--------------|
| Understanding code architecture | `gitnexus-exploring` |
| Before editing ANY code | `gitnexus-impact-analysis` |
| Debugging issues | `gitnexus-debugging` |
| Renaming/refactoring | `gitnexus-refactoring` |
| CLI/index operations | `gitnexus-cli` |
| Tool reference | `gitnexus-guide` |
| CGC graph queries | `cgc-guide` |
| Combined workflow | `combo-workflow` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `npx gitnexus` not found | Node.js >= 18 required. `npx` auto-downloads the package. |
| GitNexus index stale after analyze | Restart agent (MCP server caches old index). |
| CGC `command not found` | `uv pip install codegraphcontext` or run `uv sync` in combo repo. |
| CGC index doesn't update | Watcher may not be running. Restart it. |
| MCP tools don't appear | Check MCP config syntax. Restart agent. |
| `config_gen.py` fails | Ensure `uv sync` was run first in this combo repo. |
| Windsurf/Augment MCP not working | These require manual paste into global settings. Run `uv run python src/config_gen.py --platform <id> --print` to see the exact JSON. |
| Multiple platforms detected, wrong one used | Re-run with `--platform <specific_id>` to target a single platform. |
| Existing config corrupted | `config_gen.py --force` backs up the corrupted file as `.bak` and writes fresh. |
