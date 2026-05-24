# Phase 09: Non-Docker Distribution Channels

## Status: 🔄 IN PROGRESS (3/4 channels complete: P0 ✅, P1 ✅, P2 VS Code ✅)

> **Goal:** Give non-technical users alternative ways to access the bootstrap kit without Docker.
> Docker is unfamiliar to non-technical users. This phase adds four incremental distribution
> channels optimized for accessibility, ranked by impact-to-effort ratio.

---

## P0: GitHub Codespaces Pre-Config (09-1)

### Concept
A `.devcontainer/devcontainer.json` in the template repo so users can click "Open with Codespaces"
on GitHub and get a fully provisioned cloud environment — zero local installs.

### User Experience
1. User opens the template repo on GitHub
2. Clicks green "Code" → "Codespaces" → "Create codespace on main"
3. GitHub spins up a cloud VM with Node.js 20 + Python 3.12 + uv
4. `postCreateCommand` runs `uv sync` — all deps installed
5. User opens their AI coding tool connected to the codespace
6. Says "set up code intelligence" → agent provisions everything

### Files to Create

| File | LOC | Purpose |
|------|-----|---------|
| `.devcontainer/devcontainer.json` | 30 | Codespaces config: universal image, uv + node features, postCreateCommand, postStartMessage |

### Devcontainer Config

```json
{
  "name": "Code Intelligence (GitNexus + CGC)",
  "image": "mcr.microsoft.com/devcontainers/universal:2",
  "features": {
    "ghcr.io/astral-sh/uv:0": {},
    "ghcr.io/devcontainers/features/node:1": { "version": "20" }
  },
  "postCreateCommand": "uv sync && npx gitnexus --version",
  "postStartCommand": "echo 'Code Intelligence ready. Tell your AI agent: set up code intelligence'",
  "customizations": {
    "codespaces": {
      "openFiles": ["README.md"]
    }
  }
}
```

### Prerequisites for User
- GitHub account
- Web browser
- That's it — no Node.js, Python, or Docker needed locally

### Implementation Effort
- 1 file, ~30 LOC
- Test on a fork once
- **~30 minutes**

### Verification
- Create a codespace from the template repo
- Confirm `uv sync` completes, `npx gitnexus --version` shows version
- Say "set up code intelligence" to agent → verify provisioning succeeds
- Check `.kilo/kilo.json` or `.mcp.json` has gitnexus + cgc entries

---

## P1: `npx` Starter (09-2)

### Concept
A single `npx` command that scaffolds the bootstrap kit into any project directory.
No clone, no template — just point it at a project.

```bash
npx create-code-intelligence /path/to/my-project
```

### Package Structure

```
packages/create-code-intelligence/
├── package.json
├── bin/
│   └── create-code-intelligence.js    # Entry point (pure Node.js, no deps)
├── templates/
│   ├── AGENTS.md                      # Template with gitnexus markers, empty index stats
│   ├── .kilo/skills/                  # 8 skill files (gitnexus × 6 + cgc × 1 + combo × 1)
│   ├── platforms/matrix.json
│   ├── src/{config_gen,setup_combo,inject_agents_md,bootstrap_state,uninstall}.py
│   └── templates/{cgc-watcher.service,com.gitnexus.cgc-watcher.plist}
└── README.md
```

### Entry Point Logic (`bin/create-code-intelligence.js`)

```
parse CLI args (targetDir = argv[2] || process.cwd())
    │
    ├─ Validate targetDir exists, is writable
    ├─ Check targetDir is a git repo (warn if not, offer `git init`)
    ├─ Dry-run: list files to create, check for conflicts
    ├─ Copy template files into targetDir:
    │   ├─ platforms/ → {targetDir}/platforms/
    │   ├─ templates/ → {targetDir}/templates/
    │   ├─ src/       → {targetDir}/src/
    │   ├─ .kilo/     → {targetDir}/.kilo/
    │   └─ AGENTS.md  → {targetDir}/AGENTS.md
    │       (append if exists, create if not; always with gitnexus markers)
    ├─ Add `.gitnexus/` to .gitignore if present
    ├─ Run `uv run python src/setup_combo.py` (environment detection)
    └─ Print setup summary + next steps
```

### `package.json`

```json
{
  "name": "create-code-intelligence",
  "version": "0.1.0",
  "description": "Scaffold GitNexus + CodeGraphContext bootstrap kit into any project",
  "bin": {
    "create-code-intelligence": "./bin/create-code-intelligence.js"
  },
  "keywords": ["gitnexus", "codegraphcontext", "code-intelligence", "mcp", "ai-agent"],
  "license": "MIT",
  "engines": { "node": ">=18" },
  "files": ["bin/", "templates/"]
}
```

### Embedded Template Files

The npx package bundles the entire bootstrap kit as template files. When published to npm:

| Source in combo repo | Destination in npm package |
|----------------------|---------------------------|
| `platforms/matrix.json` | `templates/platforms/matrix.json` |
| `templates/cgc-watcher.service` | `templates/templates/cgc-watcher.service` |
| `templates/com.gitnexus.cgc-watcher.plist` | `templates/templates/com.gitnexus.cgc-watcher.plist` |
| `src/*.py` (all 5 files) | `templates/src/{config_gen,setup_combo,...}.py` |
| `.kilo/skills/**/*.md` (8 files) | `templates/.kilo/skills/**/*.md` |
| `AGENTS.md` | `templates/AGENTS.md` |

### Why This Works for Non-Technical Users
- Familiar pattern: `create-react-app`, `create-next-app`, `create-astro`
- One command, no `git clone`, no navigating folders
- Instructions printed at the end: "open in AI tool, say 'set up code intelligence'"
- `npx` auto-fetches — no `npm install -g` needed

### Implementation Effort
- `bin/create-code-intelligence.js`: ~80 LOC (CLI args, fs copy, child_process, dry-run)
- `package.json`: ~15 LOC
- Template file sync script (keep npm package in sync with combo repo): ~30 LOC
- `README.md` for npm: ~30 LOC
- npm publish: `npm publish --access public`
- **~3 hours**

### Verification
- Run `npx create-code-intelligence /tmp/test-project`
- Verify all template files copied
- Verify `AGENTS.md` has `<!-- gitnexus:start -->` markers
- Verify `.gitignore` includes `.gitnexus/`
- Verify environment detection report prints
- Test on clean directory (no git repo) → confirm `git init` prompt
- Test re-run (idempotent — should skip existing files, update AGENTS.md section)

---

## P2: VS Code / Cursor Extension (09-3)

### Concept
A lightweight VS Code extension that detects bootstrap kit presence, provides
one-click scaffolding, and shows index freshness in the status bar.

### Extension Structure

```
packages/vscode-code-intelligence/
├── package.json
├── tsconfig.json
├── .vscodeignore
├── src/
│   ├── extension.ts          # Activation, command registration
│   ├── detector.ts           # Check for bootstrap kit presence
│   ├── scaffolder.ts         # Copy template files into project
│   ├── statusBar.ts          # Index freshness indicator
│   └── commands.ts           # Command palette handler implementations
├── templates/                # Bundled bootstrap kit files
│   ├── AGENTS.md
│   ├── platforms/matrix.json
│   ├── src/*.py
│   ├── templates/*.service, *.plist
│   └── .kilo/skills/**/*.md
└── README.md
```

### Commands (Command Palette)

| Command ID | Title | Description |
|-----------|-------|-------------|
| `codeIntelligence.setup` | Code Intelligence: Setup | Detect environment, scaffold bootstrap kit if missing, guide provisioning |
| `codeIntelligence.checkStatus` | Code Intelligence: Check Status | Show GitNexus + CGC index freshness, watcher status |
| `codeIntelligence.diagnose` | Code Intelligence: Diagnose | Full health check (equivalent to `/combo-diagnose`) |
| `codeIntelligence.reindex` | Code Intelligence: Reindex | Force re-index both GitNexus and CGC |

### Status Bar

| State | Text | Color | Tooltip |
|-------|------|-------|---------|
| All fresh | `CI: ✓ GitNexus · ✓ CGC` | Green | Both indexes up to date |
| Stale GitNexus | `CI: ⚠ GitNexus stale · ✓ CGC` | Yellow | Run "Code Intelligence: Reindex" |
| Stale CGC | `CI: ✓ GitNexus · ⚠ CGC stale` | Yellow | Run "Code Intelligence: Reindex" |
| Both stale | `CI: ⚠ Both stale` | Yellow | Run "Code Intelligence: Reindex" |
| Not set up | `CI: Not set up` | Gray | Run "Code Intelligence: Setup" |
| No git repo | `CI: —` | Dim | Not a git repository |

### Activation Flow

```
VS Code activates extension onStartupFinished
    │
    ├─ detector.ts checks workspace root for AGENTS.md with gitnexus markers
    │
    ├─ IF found:
    │   ├─ statusBar.ts checks index freshness:
    │   │   ├─ npx gitnexus status (parse "up-to-date" or "stale")
    │   │   └─ uv run cgc stats {workspace} (parse file/function counts)
    │   └─ Update status bar item
    │
    └─ IF not found:
        ├─ statusBar.ts shows "CI: Not set up" (gray, clickable)
        └─ On click → toast: "Set up Code Intelligence?"
            ├─ [Not now] → dismiss
            └─ [Set up] → scaffolder.ts copies template files
                        → runs `uv run python src/setup_combo.py` in terminal
                        → status bar updates to "needs indexing"
                        → toast: "Now tell your AI agent: 'set up code intelligence'"
```

### `package.json` (excerpt)

```json
{
  "name": "code-intelligence",
  "displayName": "Code Intelligence (GitNexus + CGC)",
  "version": "0.1.0",
  "publisher": "kilocode",
  "engines": { "vscode": "^1.85.0" },
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      { "command": "codeIntelligence.setup", "title": "Code Intelligence: Setup" },
      { "command": "codeIntelligence.checkStatus", "title": "Code Intelligence: Check Status" },
      { "command": "codeIntelligence.diagnose", "title": "Code Intelligence: Diagnose" },
      { "command": "codeIntelligence.reindex", "title": "Code Intelligence: Reindex" }
    ]
  },
  "scripts": {
    "vscode:prepublish": "tsc -p ./",
    "compile": "tsc -watch -p ./",
    "package": "vsce package"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "typescript": "^5.4.0",
    "@vscode/vsce": "^2.24.0"
  }
}
```

### Key Design Decisions
- **No MCP integration in extension** — the AI agent provisions MCP configs via `config_gen.py`. The extension only scaffolds files and shows status.
- **Read-only status bar** — shows freshness, never auto-runs commands.
- **Terminal passthrough** — the extension runs `setup_combo.py` and `config_gen.py` in the VS Code terminal so the user can see the output.

### Implementation Effort
- `src/extension.ts`: ~60 LOC (activate, register commands, status bar init)
- `src/detector.ts`: ~40 LOC (check workspace for AGENTS.md markers)
- `src/scaffolder.ts`: ~50 LOC (copy bundled template files to workspace)
- `src/statusBar.ts`: ~50 LOC (parse npx/cgc output, color-coded status)
- `src/commands.ts`: ~40 LOC (command implementations)
- `package.json`: ~30 LOC
- `tsconfig.json`: ~15 LOC
- Marketplace publishing (vsce package + publish)
- **~4 hours** (core extension); **~1 day** total with testing + publishing

### Verification
- Install extension in VS Code / Cursor
- Open project without bootstrap kit → status bar shows "CI: Not set up"
- Click status bar → toast appears → click "Set up" → files scaffolded
- Open project with bootstrap kit → status bar shows freshness
- Open non-git directory → status bar shows "CI: —"
- Run "Check Status" and "Diagnose" from command palette

---

## P3: Standalone Binary (09-4)

### Concept
Package the entire bootstrap kit as a single self-contained executable using PyInstaller.
No Python, no Node.js, no uv needed — the binary bundles everything. The user downloads
a single file, drags it to their project folder, and double-clicks.

### Build Configuration

#### `packages/standalone/build.spec` (PyInstaller spec)

```python
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

a = Analysis(
    [str(Path('../../src/setup_combo.py').resolve())],
    pathex=[],
    binaries=[],
    datas=[
        (str(Path('../../platforms/').resolve()), 'platforms'),
        (str(Path('../../templates/').resolve()), 'templates'),
        (str(Path('../../.kilo/skills/').resolve()), '.kilo/skills'),
        (str(Path('../../AGENTS.md').resolve()), '.'),
    ],
    hiddenimports=[
        'codegraphcontext',
        'json',
        'argparse',
        'pathlib',
        'shutil',
        'subprocess',
        'socket',
        'os',
        'sys',
        'platform',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='code-intelligence-setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=True,
    icon='icon.ico' if sys.platform == 'win32' else None,
)

# macOS .app bundle (macOS only)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Code Intelligence Setup.app',
        icon='icon.icns',
        bundle_identifier='com.gitnexus.code-intelligence',
    )
```

### Multi-Platform Build Matrix

| Platform | Output | Build Host |
|----------|--------|-----------|
| Windows x64 | `code-intelligence-setup.exe` | `windows-latest` |
| macOS Intel | `code-intelligence-setup` + `.app` | `macos-13` |
| macOS ARM | `code-intelligence-setup` + `.app` | `macos-14` |
| Linux x64 | `code-intelligence-setup` | `ubuntu-latest` |

### GitHub Actions Release Workflow

```yaml
# .github/workflows/release.yml (new)
name: Release Binaries
on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            artifact: code-intelligence-setup-linux
          - os: macos-13
            artifact: code-intelligence-setup-macos-x64
          - os: macos-14
            artifact: code-intelligence-setup-macos-arm64
          - os: windows-latest
            artifact: code-intelligence-setup-win.exe
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: uv run pyinstaller packages/standalone/build.spec
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

### What the Binary Does

```
./code-intelligence-setup [/path/to/project]
    │
    ├─ 1. Parse target directory (default: CWD)
    ├─ 2. Run environment detection (Node.js, git — check system PATH)
    ├─ 3. Extract embedded template files to target
    │     (platforms/, templates/, src/, .kilo/, AGENTS.md)
    ├─ 4. Print environment report
    ├─ 5. Print next steps:
    │     "Open this project in your AI coding tool"
    │     "Say: 'set up code intelligence' or /combo-setup"
    └─ Exit
```

### A GUI Wrapper (Optional P3 Enhancement)

A thin Electron or Tauri wrapper could present a simple dialog for absolute beginners:

```
┌──────────────────────────────────────────────────┐
│  Code Intelligence Setup                         │
│                                                  │
│  Project path: [ /path/to/project          ] [📂]│
│                                                  │
│  AI Tool: [ Auto-detect                    ▼ ]  │
│                                                  │
│  Status                                         │
│  ✅ Node.js 20.11.0                              │
│  ✅ Python 3.12.2 (via uv)                       │
│  ✅ Git 2.44.0                                   │
│                                                  │
│  [ Set Up Code Intelligence ]                    │
└──────────────────────────────────────────────────┘
```

But the CLI binary alone is sufficient for P3; the GUI is an enhancement for a future iteration.

### Distribution Channels for the Binary

| Channel | Platform | Command |
|---------|----------|---------|
| Homebrew | macOS | `brew install kilocode/tap/code-intelligence` |
| Chocolatey | Windows | `choco install code-intelligence` |
| Scoop | Windows | `scoop bucket add kilocode && scoop install code-intelligence` |
| GitHub Releases | All | Download from releases page |
| Direct download | All | `curl -fsSL https://get.codeintelligence.dev/install.sh \| bash` |

### Implementation Effort
- `packages/standalone/build.spec`: ~50 LOC
- GitHub Actions release workflow: ~40 LOC
- Homebrew formula (Ruby): ~20 LOC
- Chocolatey package (nuspec + chocolateyinstall.ps1): ~30 LOC
- Scoop manifest (JSON): ~15 LOC
- Testing on 4 OS targets: ~2 hours
- GUI wrapper (optional): +1 day
- **CLI binary: ~4 hours**; **with GUI: ~1.5 days**

### Verification
- Download binary from GitHub Releases for each OS
- Run on a test project — verify template files extracted
- Verify environment report prints correctly
- Run with `--help` — verify usage message
- Run on non-git directory — verify warning is shown
- Verify binary runs without Python/Node.js installed (clean VM test)

---

## Comparison Matrix

| | Codespaces (P0) | npx Starter (P1) | VS Code Extension (P2) | Standalone Binary (P3) |
|---|---|---|---|---|
| **User action** | Click button on GitHub | 1 terminal command | Click install in marketplace | Download + double-click |
| **Prerequisites** | GitHub account only | Node.js >= 18 | VS Code / Cursor | None |
| **Implementation effort** | ~30 min | ~3 hours | ~1 day | ~4 hours |
| **Maintenance burden** | None (upstream image) | Low (sync templates) | Medium (VS Code API changes) | Medium (per-platform builds) |
| **Reach** | All GitHub users | All Node.js users | VS Code / Cursor users | All desktop users |
| **Non-technical friendly** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| **Docker replacement** | Yes (better) | Yes | Yes | Yes |
| **Works offline** | No (cloud) | Partial (templates cached, tools need network) | No (extension needs marketplace) | Yes (self-contained) |

---

## Rollout Order

1. **09-1: Codespaces** (30 min) ✅ Complete
2. **09-2: npx Starter** (3 hours) ✅ Complete
3. **09-3: VS Code Extension** (1 day) ✅ Complete
4. **09-4: Standalone Binary** (4 hours) — for users who want zero-dependency install

Each channel is independent — no channel blocks any other.

---

## Total

| Priority | Task# | Task | File(s) | LOC | Description |
|----------|-------|------|---------|-----|-------------|
| P0 | 09-1 | GitHub Codespaces pre-config | `.devcontainer/devcontainer.json` | 30 | Universal image + uv + Node.js 20 features. postCreateCommand runs uv sync. Zero local installs. |
| P1 | 09-2 | `npx` starter | `packages/create-code-intelligence/` | 150 | `npx create-code-intelligence <project>` — scaffolds bootstrap kit into any project. Pure Node.js, no deps. |
| P2 | 09-3 | VS Code / Cursor extension | `packages/vscode-code-intelligence/` | ~450 | ✅ Complete — 5 TS modules (detector/scaffolder/statusBar/commands/extension), sync script, 10 templates, README |
| P2 | 09-4 | Standalone binary | `packages/standalone/`, `.github/workflows/release.yml` | 200 | PyInstaller-built single executable. Multi-platform (Win/Mac/Linux). Homebrew + Chocolatey + Scoop formulas. GitHub Actions auto-release on tag. |

**Total:** 2 P0, 1 P1, 1 P2. Estimated ~680 LOC + package configs.

---
