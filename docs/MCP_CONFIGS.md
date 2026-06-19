# MCP Configuration Reference

The Code Intelligence Bootstrap Kit generates MCP server configs for **all 17 supported platforms** using `config_gen.py`. Configs are **merged** into existing files — your other MCP servers are never touched.

## How Configs Are Generated

```bash
# Auto-detect all platforms in your project and generate configs:
uv run python src/config_gen.py --detect --project-path <your_project>

# Target a specific platform:
uv run python src/config_gen.py --platform cursor --project-path <your_project>

# Preview configs without writing (dry run):
uv run python src/config_gen.py --detect --project-path <your_project> --print

# With CGC clone path:
uv run python src/config_gen.py --detect --project-path <your_project> --cgc-path /path/to/CodeGraphContext
```

## 3 Format Families

The MCP ecosystem uses 3 subtly different JSON formats. The config generator handles all of them:

### Family A: `mcpServers` — 14 platforms

Used by: **Claude Code, Codex, Cursor, Cline, Roo Code, Continue.dev, Windsurf, Augment Code, FactoryAI, Gemini CLI, Hermes, Mastra Code, Pi Agent, GitHub Copilot (CLI)**

```json
{
  "mcpServers": {
    "gitnexus": {
      "command": "npx",
      "args": ["-y", "gitnexus@latest", "mcp"]
    },
    "codegraphcontext": {
      "command": "uv",
      "args": ["run", "cgc", "mcp"],
      "cwd": "/path/to/CodeGraphContext"
    }
  }
}
```

File paths by platform:
- Claude Code → `.mcp.json`
- Codex → `.mcp.json`
- Cursor → `.cursor/mcp.json`
- Cline → `.cline/mcp.json`
- Roo Code → `.roo/mcp.json`
- Continue.dev → `.continue/mcpServers/gitnexus-cgc.json` (standalone file)
- Windsurf → `~/.codeium/windsurf/mcp_config.json` (manual — paste into global MCP Settings)
- Augment Code → `~/.augment/settings.json` (manual — paste via IDE Easy MCP panel)
- FactoryAI → `.mcp.json`
- Gemini CLI → `.mcp.json`
- Hermes → `.mcp.json`
- Mastra Code → `.mcp.json`
- Pi Agent → `.mcp.json`
- GitHub Copilot (CLI) → `.mcp.json` (shared detection)

### Family B: `mcp` — 3 platforms

Used by: **Kilo, Opencode, Kiro**

```json
{
  "mcp": {
    "gitnexus": {
      "type": "local",
      "command": ["npx", "-y", "gitnexus@latest", "mcp"]
    },
    "codegraphcontext": {
      "type": "local",
      "command": ["uv", "run", "cgc", "mcp"],
      "workdir": "/path/to/CodeGraphContext"
    }
  }
}
```

Key differences from `mcpServers`:
- Top-level key is `"mcp"` (not `"mcpServers"`)
- Each server has `"type": "local"`
- `command` is a single array (not separate `command` + `args`)
- Working directory is `"workdir"` (not `"cwd"`)

File paths:
- Kilo → `.kilo/kilo.json` (merged with existing `mcp` entries)
- Opencode → `opencode.json` (merged with existing `mcp` entries)
- Kiro → `kiro.json` (merged with existing `mcp` entries)

### Family C: `servers` — 1 platform

Used by: **GitHub Copilot (VS Code)**

```json
{
  "servers": {
    "gitnexus": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "gitnexus@latest", "mcp"]
    },
    "codegraphcontext": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "cgc", "mcp"],
      "cwd": "/path/to/CodeGraphContext"
    }
  }
}
```

Key differences from `mcpServers`:
- Top-level key is `"servers"`
- Each server has `"type": "stdio"`

File path:
- Copilot (VS Code) → `.vscode/mcp.json`

## Merge Behavior

When a config file already exists, `config_gen.py`:

1. Parses the existing JSON
2. Adds only `gitnexus` and `codegraphcontext` entries
3. **Preserves all existing MCP servers untouched**
4. Re-running on an already-configured project returns `[SKIP]` (idempotent)

If a config file contains invalid JSON:
- Runs with `--force` to back up the corrupted file as `.bak` and write fresh
- Without `--force`, reports the error without modifying anything

## CGC Path Detection

CGC's MCP config needs a working directory (`workdir` / `cwd`). The path depends on installation method:

| Install Method | CGC Path |
|----------------|----------|
| `uv sync` in combo repo | Path to the combo repo (CGC in `.venv`) — auto-detected |
| `git clone` CodeGraphContext | Absolute path to the clone directory |
| `uv pip install codegraphcontext` | Omit `--cgc-path` (works globally) |

## Windows Paths

`config_gen.py` uses Python's `pathlib` which handles platform paths natively. Windows paths are written correctly:

```json
"cwd": "C:\\Dev\\useful_repos\\02-code-intelligence\\CodeGraphContext"
```

## CGC Source Install (Alternative)

If installing CGC from source instead of PyPI:

```bash
git clone https://github.com/Shashankss1205/CodeGraphContext.git /path/to/CodeGraphContext
cd /path/to/CodeGraphContext
uv pip install -e .
```

Then pass `--cgc-path /path/to/CodeGraphContext` to `config_gen.py`.