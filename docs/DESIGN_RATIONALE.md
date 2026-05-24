# Design Rationale

> Architectural decisions and scope philosophy for the GitNexus + CGC combo bootstrap kit.
> Written 2026-05-23 following a project scope review session, expanded thereafter.

---

## Table of Contents

1. [Core Insight: The Agent IS the Runtime](#core-insight-the-agent-is-the-runtime)
2. [Architecture: Three-Part Design](#architecture-three-part-design)
3. [The Platform Matrix: Data, Not Code](#the-platform-matrix-data-not-code)
4. [The Config Generator: The One Script That Survives](#the-config-generator-the-one-script-that-survives)
5. [The Skills System: Defense-in-Depth Agent Memory](#the-skills-system-defense-in-depth-agent-memory)
6. [What We Cut (and Why)](#what-we-cut-and-why)
7. [What We Keep (and Why)](#what-we-keep-and-why)
8. [Two Paths, One Engine](#two-paths-one-engine)
9. [Testing Philosophy](#testing-philosophy)
10. [Distribution Recommendations](#distribution-recommendations)
11. [Post-Scope-Review: Deferred Channels (Phase 09)](#post-scope-review-deferred-channels-phase-09)
12. [Scope Boundaries](#scope-boundaries)
13. [Key Technical Decisions](#key-technical-decisions)
14. [The Design Principle](#the-design-principle)

---

## Core Insight: The Agent IS the Runtime

This project exists to solve one problem: **an AI coding agent should self-provision GitNexus + CodeGraphContext for any project.** The agent already has tools for running commands, reading/writing files, and following instructions. Building Python scripts that duplicate these capabilities is redundant.

**The product is the protocol, not the executables.** AGENTS.md encodes a complete 8-phase bootstrap sequence. The agent reads it, follows it, and provisions everything. No user action required.

This leads to a simple architecture:

```
AGENTS.md              ← The program. Agent follows this.
platforms/matrix.json  ← Data. Declarative registry of all supported platforms.
config_gen.py          ← The one script agents need. MCP JSON generation + merging.
skills/                ← Reference cards. Agent loads on demand.
```

---

## Architecture: Three-Part Design

The bootstrap kit has three layers with distinct responsibilities:

```
┌─────────────────────────────────────────────────────────────┐
│  AGENTS.md (544 LOC)                                        │
│  The protocol. Agent reads → executes → provisions.        │
│  Never edited by code. Human-readable + machine-actionable. │
├─────────────────────────────────────────────────────────────┤
│  config_gen.py (242 LOC) + platforms/matrix.json (208 LOC) │
│  The data engine. Structured JSON generation across 3       │
│  MCP format families × 10 platforms. Agents are bad at     │
│  structured JSON; Python is not.                            │
├─────────────────────────────────────────────────────────────┤
│  .kilo/skills/ (8 skill files)                              │
│  Agent reference cards. Loaded on demand for specific       │
│  tasks. Separate from protocol — opinionated workflows.     │
└─────────────────────────────────────────────────────────────┘
```

The separation ensures each layer can evolve independently. Changing a platform's MCP format does not touch AGENTS.md. Adding a new skill does not touch `config_gen.py`. Rewriting the protocol does not touch the skills.

---

## The Platform Matrix: Data, Not Code

`platforms/matrix.json` is a declarative registry of all supported AI coding platforms. Adding a new platform requires only a JSON entry — no Python changes.

### Design Tradeoffs Evaluated

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Hardcode in Python | Fast to write | Requires code change per platform. No non-developer contributions. | ❌ |
| YAML registry | More readable than JSON | Same as JSON but with schema complexity and YAML's whitespace sensitivity. | ❌ |
| **JSON registry** | Universal parsing. No dependency. Validates trivially. | Verbose. | ✅ Chosen |
| TOML registry | Python-native (`pyproject.toml` style). | Less familiar to non-Python devs. Poor nesting support. | ❌ |

### Three Format Families

The registry documents three distinct MCP JSON formats:

| Family | Wrapper Key | Used By | Format |
|--------|-------------|---------|--------|
| `mcpServers` | `"mcpServers"` | Claude Code, Cursor, Cline, Roo Code, Continue, Windsurf, Augment | `command` + `args` + `env` (flat) |
| `mcp` | `"mcp"` | Kilo, Opencode | `type: "local"` + `command` array + `workdir` |
| `servers` | `"servers"` | Copilot (VS Code) | `type: "stdio"` + `command` + `args` + `env` |

These 3 families cover 10 platforms. If a new platform uses any of these formats, its entry is purely additive data. If a new format emerges (e.g., `mcpServers` with `url` instead of `command`), `config_gen.py` extends with a new family handler.

### Merge Strategies

Not all platforms support automatic config writing:

| Strategy | Platforms | Behavior |
|----------|-----------|----------|
| `merge-into-existing-json` | Kilo, Claude Code, Cursor, Cline, Roo Code, Opencode, Copilot | Parses existing config, adds entries, preserves all user content |
| `create-standalone-file` | Continue.dev | Creates a new file in a directory that expects individual server files |
| `print-for-manual-paste` | Windsurf, Augment Code | Prints JSON to stdout. User must paste into global settings. |

This distinction is critical because Windsurf and Augment do not support project-level MCP configs — they require global config paste. The registry captures this limitation explicitly.

### Platform Detection

Each platform has detection markers (`detection_markers`) — files or directories that indicate the platform is in use. For example:

- Kilo: `.kilo/` directory exists
- Claude Code: `.mcp.json` or `CLAUDE.md` exists
- Cursor: `.cursor/` directory exists

Detection is a pure filesystem scan — no configuration is written based on detection alone. The user (or agent) must explicitly request MCP config generation.

---

## The Config Generator: The One Script That Survives

`config_gen.py` is the sole Python script preserved in the architecture. Every other script was cut because the agent can perform its function with existing tools. This one survives because agents are fundamentally bad at structured, multi-format JSON generation.

### Why Agents Struggle With MCP Configs

AI agents operate on text. When told to "add a gitnexus server to my .mcp.json", they:
1. Read the existing file (may have complex JSON with user's other servers)
2. Parse JSON by reading tokens (error-prone with nested structures)
3. Generate the correct new JSON (must match the platform's format family)
4. Write back (risk: corrupting the entire file if JSON is malformed)

Each of these steps is fragile for 10 platforms across 3 format families. One missing comma, one wrong key name, and the agent's MCP tools stop working entirely — silently breaking the session.

### Design: Parsed, Not Generated

`config_gen.py` does not generate JSON by string concatenation. It:
1. `json.load()` — parses existing config into a Python dict
2. Adds entries with `dict[key] = {...}` — structured mutation
3. `json.dump(indent=2)` — writes back with guaranteed valid JSON

This guarantees the output is always valid JSON. The existing structure is preserved byte-for-byte except for the new entries.

### Idempotency by Design

If gitnexus or codegraphcontext entries already exist in the config, `config_gen.py` returns `[SKIP]`. This means:
- The agent can always call it — no pre-checking needed
- Re-running setup never duplicates entries
- The `--force` flag backs up corrupted configs as `.bak` and writes fresh

### The `--detect` Mode

The agent does not need to know which platforms are in use. It calls:

```bash
uv run python src/config_gen.py --detect --project-path /path/to/project
```

`config_gen.py` scans the project directory for platform markers, resolves the format family from the matrix, and generates configs only for detected platforms. Zero platform knowledge required from the agent.

---

## The Skills System: Defense-in-Depth Agent Memory

The 8 operational skills serve a different purpose than AGENTS.md. AGENTS.md encodes the bootstrap protocol ("how to set up"). Skills encode the operational protocols ("how to use the tools once set up").

### Two Categories of Skills

| Category | Skills | Purpose |
|----------|--------|---------|
| **GitNexus** (6 skills) | guide, cli, exploring, impact-analysis, debugging, refactoring | How to use GitNexus for specific engineering tasks |
| **CGC** (1 skill) | cgc-guide | How to use CodeGraphContext for graph queries |
| **Combo** (1 skill) | combo-workflow | When to use GitNexus vs CGC for a given task |

### When Skills Load

Skills are not always loaded — that would bloat the agent's context window. They are loaded **on demand** when a task matches the skill's description:

| User says | Skill Loaded |
|-----------|-------------|
| "What breaks if I change foo()?" | `gitnexus-impact-analysis` |
| "How does the auth system work?" | `gitnexus-exploring` |
| "Why is the payment flow failing?" | `gitnexus-debugging` |
| "Rename getCwd to getCurrentWorkingDirectory" | `gitnexus-refactoring` |
| "Find all functions matching pattern X" | `cgc-guide` |
| Complex refactor with both tools | `combo-workflow` |

### Skill Portability

Skills are written in a platform-agnostic format. The same 8 files work for Kilo (`.kilo/skills/`) and Claude Code (`.claude/skills/`). Phase 7 of AGENTS.md documents the copy path — the agent copies the directory during bootstrap.

For platforms without native skill systems (Cursor, Roo Code, Continue.dev, etc.), the behavioral rules are embedded inline in AGENTS.md Phase 6 as "Always Do / Never Do" tables and "When to Use Each" tables. These inline rules provide equivalent behavioral guidance without a skill file loading mechanism.

### Why Embedded Rules Instead of Skill Files for All Platforms

The skills encode **workflows** (do this, then that, then check this). Platforms without skill systems cannot load workflows — they can only read static text. The inline rules in AGENTS.md convert the dynamic workflow guidance into static behavioral mandates that the agent follows regardless of platform.

---

## What We Cut (and Why)

### Cut: `setup_combo.py` (210 lines — environment detection)

**What it did:** Ran `node --version`, `python --version`, `uv --version`, `git --version`. Printed a report.

**Why cut:** The agent has `bash`. It runs these commands natively. AGENTS.md Phase 1 already lists every check with exact commands. A script that runs `node --version` and prints output is 210 lines of indirection over `bash: node --version`.

### Cut: `inject_agents_md.py` (440 lines — AGENTS.md injection)

**What it did:** Parsed AGENTS.md, substituted variables, injected sections between `<!-- gitnexus:start -->` markers. Handled nested code block fence balancing, multi-section splitting, dry-run mode, removal support.

**Why cut:** The agent has `read` and `edit` tools. It can read the target AGENTS.md, find or insert markers, and write the behavioral protocol sections directly. Template variable substitution is string manipulation — the agent is good at this. 440 lines of Python for what is effectively a find-and-replace operation.

### Cut: `skill_gen.py` (212 lines — skill file copying)

**What it did:** Copied 8 skill files from the combo repo to the user's project.

**Why cut:** The agent has `glob` and file copying capabilities. AGENTS.md Phase 7 already specifies exact source → destination mappings. The agent can enumerate files and copy them.

### Cut: `uninstall.py` (463 lines — cleanup)

**What it did:** Removed MCP config entries (with deduplication for shared config files), AGENTS.md sections (with whitespace cleanup), skill files (with empty parent cleanup), indexes, platform directives, and the watcher process. Supported `--dry-run`, targeted `--remove` flags, and `--stop-watcher`.

**Why cut:** Every removal operation is the inverse of a setup operation the agent already knows how to do. Remove a JSON key. Delete an AGENTS.md section. Delete directories. Stop a process. The agent can undo what it did. 463 lines of Python for actions the agent performs with `edit` and `bash`.

### Cut: `watcher_health.py` (195 lines — watcher status check)

**What it did:** Checked if `cgc watch` process was running across platforms (Windows/Unix/systemd/launchd).

**Why cut:** `pgrep -f "cgc watch"` (Unix) or `Get-Process` (Windows). One command. The agent has `bash`. 195 lines of Python for a single shell command.

### Cut: `rule_extractor.py` (399 lines — rule extraction)

**What it did:** Extracted "Always Do / Never Do" rules from AGENTS.md, detected existing platform instruction files, wrote meta-directives and behavioral rules for non-skill platforms (Cursor, Cline, Roo Code, Windsurf, Augment, Copilot).

**Why cut:** The agent can read AGENTS.md and summarize. Or better: AGENTS.md Phase 6 already includes the full behavioral protocol inline — no extraction needed.

### Cut: `bootstrap_state.py` (145 lines — state tracking)

**What it did:** Wrote `.gitnexus-cgc-bootstrap.json` after each phase for resume-on-failure. Tracked phase completion, failure markers, and allowed resumption from last checkpoint.

**Why cut:** Premature optimization. The agent can re-run idempotent phases. The protocol is designed for idempotency (`<!-- gitnexus:start -->` markers, config merge skip). State tracking is complexity that doesn't earn its keep.

### Cut: `offline.py` (193 lines — offline resilience)

**What it did:** Checked network connectivity (TCP sockets to npmjs.org, pypi.org, github.com), detected cached tools in `~/.npm/` and `~/.cache/uv/`, offered pre-bundled config templates for air-gapped environments.

**Why cut:** The agent can `ping` or `curl` a URL and decide what to do. Cached tool detection is a `which gitnexus` away. Offline bootstrap is an edge case for an internet-dependent setup tool.

### Cut: `combo.py` (187 lines — unified CLI prototype)

**What it did:** Wrapped multiple scripts into a single `combo` command with 9 subcommands (setup, uninstall, diagnose, config, skills, health, offline, inject, state).

**Why cut:** The architecture doesn't need a unified CLI. An agent follows AGENTS.md. A human runs one command. There is no suite of subcommands to orchestrate.

### Cut: `Dockerfile` (20 lines)

**What it did:** Containerized `setup_combo.py` — python:3.12-slim + Node.js 20 + uv pre-installed.

**Why cut:** Docker is the wrong abstraction for a bootstrap harness. The tool installs software and writes config files onto the user's real machine. A container is isolated by design — it cannot reach out and modify the host filesystem without fragile volume mounts, permission juggling, and platform misdetection.

### Cut: `templates/` (2 files — systemd service, launchd plist)

**What it did:** Templates for running `cgc watch` as a persistent OS service with security hardening (`NoNewPrivileges`, `ProtectSystem=strict`, specific `ReadWritePaths`) and auto-restart (`Restart=on-failure`, `KeepAlive=true`).

**Why cut:** AGENTS.md Phase 5 already documents the exact commands. Most users will never set up an OS-level watcher service. For those who do, the documented commands suffice. Maintaining OS-specific service templates is administrative overhead, not user value.

### Cut: `tests/` (232 tests, ~2,800 LOC across 7 test files)

**What it did:** Unit and integration tests for config_gen, setup_combo, inject_agents_md, bootstrap, uninstall, rule extraction, watcher hardiness, and offline resilience.

**Why cut:** Tests protect against regression in code that changes. When the code is removed, the tests go with it. The "tests" for the simplified architecture are: `bash` one-liners verifying the agent protocol works end-to-end.

### Cut: `.github/workflows/`, `.pre-commit-config.yaml`, `.devcontainer/`

**Why cut:** CI, pre-commit hooks, and devcontainers are contributor infrastructure — premature for a project still clarifying its scope. Defer until a stable, published package exists.

### Cut: `packages/` (VS Code extension stubs, npx starter stubs, standalone binary stubs)

**Why cut:** Three alternative distribution channels explored before the core product is stable. Each represents a separate maintenance burden. The `create-code-intelligence` scaffolding tool, `vscode-code-intelligence` extension, and standalone binary wrapper are premature.

---

## What We Keep (and Why)

### AGENTS.md (544 lines — agent protocol)

The single source of truth. An 8-phase bootstrap sequence written as executable instructions for an AI coding agent. The agent reads it, follows it, and provisions everything. No user action required.

### `config_gen.py` (242 lines — MCP config generation)

The one script agents genuinely need. MCP config JSON varies across 10 platforms in 3 format families. Structured JSON manipulation — parsing existing configs, adding entries, preserving user's other servers, handling merge-vs-standalone-vs-print strategies — is error-prone for an agent writing raw text. A Python script with proper JSON parsing (`json.load`/`json.dump`) is the right tool for this job.

`config_gen.py` reads `platforms/matrix.json` (declarative registry of all 10 platforms) and generates the correct MCP server JSON for any detected platform. It merges into existing configs (never overwrites), handles 3 format families (`mcpServers`, `mcp`, `servers`), and is idempotent (re-running returns `[SKIP]`).

### `platforms/matrix.json` (208 lines — platform registry)

Data, not code. Adding a new platform requires only a new JSON entry — no Python changes. This is the right decoupling. The registry encodes: platform name, detection markers, MCP format family, config file path, merge strategy, instruction files, skill support, and auto-MCP capability.

### `.kilo/` (commands, agents, skills, rules)

Kilo-native config that makes the combo usable as slash commands. Lightweight wrappers — each `command/*.md` is a manifest, each `agent/*.md` is a task prompt that invokes AGENTS.md phases. The 8 skill files are agent reference cards for specific tasks (impact analysis, debugging, refactoring, etc.).

### CLI entry point (`pyproject.toml` scripts)

A lightweight `combo-setup` command for users who don't use AI coding tools:
- Calls `config_gen.py` for MCP configs
- Runs `npx gitnexus analyze` and `cgc index` for indexing
- Optionally writes AGENTS.md sections
- Prints a summary

This serves the manual-install path without duplicating agent capabilities. `uvx gitnexus-cgc-combo setup my-project/` is the user-facing distribution path.

---

## Two Paths, One Engine

```
                    ┌──────────────────────┐
                    │   config_gen.py      │
                    │  (MCP config engine) │
                    └─────────┬────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
    ┌─────────┴──────────┐         ┌──────────┴────────┐
    │   Agent Path        │         │   Manual Path      │
    │                     │         │                    │
    │ AI agent follows    │         │ User runs:         │
    │ AGENTS.md protocol  │         │ combo-setup ./     │
    │                     │         │                    │
    │ Agent handles:      │         │ CLI handles:       │
    │ - Skills            │         │ - MCP configs      │
    │ - AGENTS.md inject  │         │ - Indexing         │
    │ - Verification      │         │ - AGENTS.md (opt)  │
    │                     │         │ - Summary          │
    │                     │         │                    │
    │ Agent uses:         │         │                    │
    │ - bash (commands)   │         │ (No skill files —  │
    │ - read (files)      │         │  manual user has   │
    │ - edit (injection)  │         │  no skill system)  │
    │ - glob (file copy)  │         │                    │
    └─────────────────────┘         └────────────────────┘
```

Shared core: `config_gen.py` + `platforms/matrix.json`. Everything else is path-specific.

---

## Testing Philosophy

The scope review cut 232 tests along with the code they tested. This is not a rejection of testing — it's a recognition that the architecture changed. Post-cut, testing takes a different form.

### What to Test vs What Not to Test

| Test? | Rationale |
|--------|-----------|
| ✅ `config_gen.py` output is valid JSON for all 3 format families | The one surviving script. Test its core function. |
| ✅ `config_gen.py` merge preserves user's existing servers | The merge guarantee is the product's key safety promise. |
| ✅ `config_gen.py` is idempotent (re-run = `[SKIP]`) | Idempotency is essential for agent execution. |
| ✅ `platforms/matrix.json` is valid JSON with all required fields | Data integrity. A malformed matrix breaks all platforms. |
| ✅ End-to-end: agent follows AGENTS.md on a clean project | The "smoke test" — does the whole protocol work? |
| ❌ `setup_combo.py` correctly detects shell | Cut script. Agent uses `echo $0` instead. |
| ❌ `inject_agents_md.py` template extraction | Cut script. Agent uses `edit` tool instead. |
| ❌ `uninstall.py` correctly removes MCP entries | Cut script. Agent performs inverse operations. |
| ❌ `bootstrap_state.py` resumes from checkpoint | Cut script. Protocol is idempotent. |

### Test Strategy Post-Cut

```
1. Unit tests for config_gen.py (~100 tests)
   - Merge into existing configs (all 3 families)
   - Create new config on empty project
   - Idempotency (SKIP on re-run)
   - Force mode (backup + write fresh on invalid JSON)
   - Detection on all 10 platforms
   - Error handling (missing matrix, invalid platform, etc.)

2. Data validation for matrix.json (~10 tests)
   - All required fields present
   - No duplicate platform IDs
   - Valid merge strategy values
   - Format family consistency

3. Integration test: full agent protocol (~5 tests)
   - Agent provisions on clean project
   - Agent provisions on project with existing MCP servers
   - Agent provision is idempotent
   - Cross-platform detection writes only for detected platforms
```

The integration tests verify the architecture's central claim: **an agent following AGENTS.md can self-provision GitNexus + CGC without human intervention.** If this fails, the entire project fails.

### What "Testing" Means for AGENTS.md

AGENTS.md is a prose document, not code. "Testing" it means:
1. **Execution verification**: Have 3 different AI coding platforms follow it end-to-end
2. **Phase boundary verification**: If Phase 2 fails, do Phases 3+5 correctly skip?
3. **Edge case verification**: Empty project, heavily populated project, project with custom MCP servers
4. **Freshness verification**: Does the stale-index detection logic trigger correctly?

These cannot be unit-tested. They require live agent execution against real projects.

---

## Post-Scope-Review: Deferred Channels (Phase 09)

The scope review cut `packages/` (VS Code extension stubs, npx starter stubs, PyInstaller build spec) as premature. However, these channels address a real problem: **Docker is unfamiliar to non-technical users.** Phase 09 plans four incremental distribution channels that require zero Docker knowledge, ranked by impact-to-effort ratio.

### P0: GitHub Codespaces (30 min)

A `.devcontainer/devcontainer.json` so users can click "Open with Codespaces" on GitHub and get a fully provisioned cloud environment. Zero local installs — just a browser and GitHub account. The `postCreateCommand` runs `uv sync`, the `postStartCommand` prints "Tell your AI agent: set up code intelligence."

**Why P0 (highest priority):** No prerequisites. Works for every GitHub user. 30 minutes to implement.

### P1: `npx` Starter (3 hours)

```bash
npx create-code-intelligence /path/to/my-project
```

Scaffolds the bootstrap kit into any project directory. Pure Node.js, zero npm dependencies. Follows the `create-react-app` → `create-next-app` → `create-astro` pattern familiar to JavaScript developers. Bundles all template files (AGENTS.md, platforms/matrix.json, config_gen.py, skills) into the npm package.

**Why P1:** Familiar UX pattern for frontend developers. Visibility via npm ecosystem. Edits nothing outside the target directory.

### P2: VS Code Extension (1 day)

A lightweight VS Code/Cursor extension with:
- **Status bar indicator:** Shows GitNexus + CGC index freshness (green/yellow/gray)
- **One-click scaffolding:** "Code Intelligence: Setup" from command palette
- **Diagnose command:** Equivalent to `/combo-diagnose`
- **Reindex command:** Force re-indexes both tools

The extension does NOT manage MCP configs — that's the agent's job. It scaffolds files and shows status, nothing more.

**Why P2:** Taps the largest AI coding tool user base (VS Code + Cursor). Medium maintenance burden (VS Code API changes).

### P3: Standalone Binary (4 hours)

A single executable built with PyInstaller. Multi-platform (Windows/Mac/Linux). No Python, Node.js, or uv required — the binary bundles everything. Distributed via GitHub Releases, Homebrew, Chocolatey, and Scoop.

**Why P3:** Complete zero-dependency story. But highest maintenance burden (per-platform builds, signing, notarizing on macOS).

### Why These Are Deferred, Not Rejected

The scope review was right to cut these as premature. Building distribution channels before the core product is stable risks:

1. **Fragmentation:** Fixing a bug in AGENTS.md requires updating 4 distribution channels
2. **False confidence:** A working Codespaces setup that silently misses a config format
3. **Maintenance treadmill:** VS Code API deprecations, npm security patches, PyInstaller build breaks — without the user base to justify it

Each channel is independent — building Codespaces does not require the npx starter. The rollout order prioritizes the highest impact with the lowest effort first. Each channel can be implemented in isolation.

---

## Key Technical Decisions

### Decision 1: Python over Node.js for the bootstrap kit

| Factor | Python | Node.js |
|--------|--------|---------|
| Dependency | `codegraphcontext` is a Python package | Would need child_process to invoke Python |
| `uv` integration | Native (`uvx`, `uv sync`, `uv pip install`) | Would need `execSync('uv', ...)` |
| Cross-platform | `pathlib` handles Windows/Unix paths | `path` with separator normalization |
| User prerequisite | `uv` auto-fetches Python if missing | Node.js must be pre-installed |

**Verdict:** Python. CGC is a Python package. Wrapping Python in Node.js adds a prerequisite (Node) for a tool whose primary dependency is Python. The `uvx` distribution path (see Distribution) eliminates the Python prerequisite entirely.

### Decision 2: JSON over YAML/TOML for the platform registry

JSON was chosen for `platforms/matrix.json` because:
- **Zero dependencies:** `json.load()` is in the standard library. YAML requires `PyYAML`.
- **Universal parsing:** Every language has a JSON parser. The registry is readable by VS Code extensions (TypeScript), npx starters (JavaScript), and config generators (Python) without conversion.
- **Trivial validation:** `python -m json.tool platforms/matrix.json` validates in one command.
- **Editability:** Every AI agent can write valid JSON. YAML has whitespace sensitivity that agents frequently get wrong.

The verbosity of JSON (lots of `{}` and `[]`) is a minor tradeoff for universal compatibility.

### Decision 3: Markdown over HTML/PDF/YAML for AGENTS.md

AGENTS.md is a Markdown file because:
1. AI agents natively read and write Markdown
2. Human readability and editability (viewable on GitHub without rendering)
3. No toolchain dependency (no SSG, no PDF generator)
4. Code blocks are first-class (critical for bash commands and JSON examples)

The `<!-- gitnexus:start -->` / `<!-- gitnexus:end -->` HTML comment markers are invisible to Markdown renderers but parseable by both agents and scripts.

### Decision 4: `uv` over `pip` for package management

| Factor | `uv` | `pip` |
|--------|------|-------|
| Python auto-fetch | `uv python install 3.13` installs Python if missing | Requires pre-installed Python |
| No-install run | `uvx tool command` (like `npx`) | Not supported |
| Lock file | `uv.lock` (cross-platform, deterministic) | `pip freeze` (snapshot, non-deterministic) |
| Speed | 10-100x faster than pip | — |
| Windows support | First-class, tested | Long-standing issues |

**Verdict:** `uv`. The `uvx` distribution path means users never install Python. They run one command. `uv` auto-fetches what it needs. This eliminates the "I don't have Python installed" barrier.

### Decision 5: Idempotent merge over replace

Every MCP config operation is a merge, never a replace. This means:
- If the user has a `filesystem` MCP server configured, it stays
- If the user has custom `env` variables, they stay
- Running setup twice produces the same result as running it once

The alternative (replace) would destroy user configuration — an unacceptable risk for a bootstrap tool.

### Decision 6: Protocol over CLI

The project deliberately does not build a unified CLI with subcommands. Instead:
- **For agents:** AGENTS.md is the CLI. Each phase is a numbered step.
- **For humans:** `uvx gitnexus-cgc-combo setup <project>` is the CLI. One command.

This avoids the "CLI treadmill" — every new phase requires a new subcommand, its help text, its error handling, its tests. The protocol document scales linearly (add a phase section) without code changes. The human CLI wraps the same engine (`config_gen.py`) and runs steps sequentially.

### Decision 7: Platform detection by filesystem markers, not user prompts

The agent never asks "What AI tool do you use?" Instead, `config_gen.py --detect` scans the filesystem. This matters because:
- The user may not know what their AI tool is called (many IDEs label it "AI Assistant")
- The user may use multiple tools (VS Code + Cursor + Claude Code on the same project)
- Asking is an interruption that breaks the agent's autonomy

The detection is a prefix of the full matrix — if only Kilo markers are found, only Kilo config is generated. If multiple platforms are detected, all are configured.

---

## Distribution Recommendations

The target user downloads a bootstrap kit and runs one command. The user may not write Python. The tool should impose minimal prerequisites.

### Recommended: `uvx` (top choice)

```bash
uvx gitnexus-cgc-combo setup my-project/
```

`uvx` is Python's equivalent of `npx` — fetch, run, discard. No install step. No Python required (uv auto-fetches Python if needed). No lock-in. Nothing to uninstall. Works for Python and non-Python users alike.

**Why this over other options:**

| Option | Install required? | Requires Python? | Requires Node? | Good for non-Python users? |
|--------|:--:|:--:|:--:|:--:|
| **uvx** | No | No (auto) | No | Yes |
| pip install | Yes | Yes | No | No |
| pipx install | Yes | Yes | No | No |
| npx | No | Yes (script is Python) | Yes | No |
| npm install -g | Yes | Yes | No | No |
| conda install | Yes | Yes | No | No (data science only) |
| pixi | Yes | Yes | No | No (very niche) |
| brew install | Yes | No | No | Yes (macOS only) |
| scoop install | Yes | No | No | Yes (Windows only) |
| Standalone binary | No | No | No | Yes (all platforms) |

### Secondary: Standalone binary (GitHub Releases)

```bash
# Download from GitHub Releases, then:
./combo-setup setup my-project/
```

A single executable built with PyInstaller. No runtime dependencies — no Python, no Node, no uv. Download, run, delete. The tradeoff: larger file size (bundled Python interpreter) and a build step for each release.

Best for users who want zero prerequisites and are uncomfortable with terminal package managers.

### Not recommended:

- **npm/npx:** The tool is Python. Wrapping a Python tool in npm adds a Node.js prerequisite for non-Node users. The `npx` "no install" benefit is already covered by `uvx` without the Node requirement.
- **conda/pixi:** Too heavyweight. conda is for data science environments, pixi is a conda alternative with ~zero adoption. The tool's dependency tree is trivial (codegraphcontext + standard library).
- **brew/scoop:** OS-specific package managers add maintenance burden (formula submissions, tap repos, version bumps) for a bootstrap tool that runs once per project. Not worth it.
- **Docker:** Wrong abstraction for a tool that modifies the host filesystem. Docker adds isolation where you need access, and complexity where you need simplicity.

### Deferred (see Post-Scope-Review above):

- **GitHub Codespaces:** Zero prerequisite cloud environment. Planned as P0 for Phase 09.
- **npx Starter** (`create-code-intelligence`): Familiar JS ecosystem pattern. Planned as P1.
- **VS Code Extension:** Status bar + one-click scaffolding for the largest user base. Planned as P2.
- **Standalone Binary (PyInstaller):** Zero-dependency single executable. Planned as P3.

### Recommendation summary:

Publish the package to PyPI. Primary install path is `uvx gitnexus-cgc-combo setup <project>`. Also offer standalone binaries on GitHub Releases for users who prefer a downloadable executable. If demand emerges, add `brew` and `scoop` later.

---

## Scope Boundaries

**In scope:**
- Install GitNexus and CodeGraphContext
- Generate MCP configs for the user's AI coding platform
- Index the user's project with both tools
- Write behavioral protocol into the user's AGENTS.md
- Start the CGC file watcher

**Out of scope:**
- A unified CLI with subcommands (diagnose, uninstall, status, etc.)
- A VS Code extension
- A Docker image
- A scaffolding tool (`create-code-intelligence`)
- Offline/air-gapped installation
- Bootstrap state persistence across sessions
- OS-level watcher service management (systemd, launchd)
- Rule extraction for non-skill platforms

**Deferred — revisit if demand materializes (Phase 09 planned):**
- GitHub Codespaces pre-configuration
- `npx` starter scaffolding tool
- VS Code / Cursor extension with status bar
- Standalone PyInstaller binary with Homebrew/Chocolatey/Scoop distribution

**Deferred — revisit if users ask:**
- Uninstall command (`--remove` flags for partial cleanup)
- Health/diagnose command

---

## The Design Principle

> **The agent is the runtime. AGENTS.md is the program. Scripts exist only where agents are weak.**

An AI agent can run commands, read files, edit files, copy directories, and follow multi-step protocols. Building Python scripts for these tasks is redundant — it's writing an interpreter for a language the agent already speaks. The one exception is structured JSON generation across 10 inconsistent platform formats. That's `config_gen.py`. Everything else is the agent's job.
