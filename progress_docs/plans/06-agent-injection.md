# Phase 06: Agent-Executed Injection

## Plan

Inject GitNexus + CGC protocol sections into the user project's AGENTS.md during `/combo-setup`. The agent calls `inject_agents_md.py` after indexing completes.

## Task List

| Priority | Task# | Task | File(s) | LOC | Status |
|----------|-------|------|---------|-----|--------|
| P0 | 06-1 | Template extraction + variable substitution + idempotent injection | `src/inject_agents_md.py` | 210 | ✅ |
| P0 | 06-2 | Tests: 6 classes, 22 tests | `tests/test_inject_agents_md.py` | 200 | ✅ |
| P1 | 06-3 | Dry-run mode (`--dry-run` flag) | `src/inject_agents_md.py` | built-in | ✅ |
| P1 | 06-4 | Multi-section injection (GitNexus + CGC) + removal | `src/inject_agents_md.py` | built-in | ✅ |
| P2 | 06-5 | Unified inject CLI (combined MCP config + AGENTS.md injection) | deferred | — | ⏳ |

## Architecture

### Template Extraction
Reads the combo repo's `AGENTS.md`, finds the `### The sections to inject into AGENTS.md:` section, extracts content from the ` ```markdown ` code block using fence-balancing (handles nested code blocks like ` ```bash `).

### Variable Substitution
Replaces `{repo_name}`, `{symbols}`, `{relationships}`, `{flows}`, `{cgc_path}`, `{user_project_path}`, and legacy `{N}` placeholders.

### Idempotent Injection
- **Create**: AGENTS.md doesn't exist → write full template
- **Update**: AGENTS.md has `<!-- gitnexus:start -->` / `<!-- gitnexus:end -->` markers → replace between markers
- **Append**: AGENTS.md exists without markers → append at end
- **Noop**: Content between markers unchanged → skip

### Section Splitting
The `_split_sections()` function separates the gitnexus section (between markers) from the CGC section (everything after `<!-- gitnexus:end -->`). On update, only the gitnexus section is replaced; the CGC section stays in place.

### Removal
`remove_injection_sections()` removes content between `<!-- gitnexus:start -->` and `<!-- gitnexus:end -->` markers. Used by Phase 07 uninstall.

## CLI

```bash
# Inject into project
uv run python src/inject_agents_md.py \
    --project-path /path/to/project \
    --repo-name myapp \
    --symbols 450 --relationships 1200 --flows 42 \
    --cgc-path /path/to/cgc

# Preview without writing
uv run python src/inject_agents_md.py --project-path . --dry-run --repo-name test

# Print resolved template
uv run python src/inject_agents_md.py --print --repo-name test --symbols 100

# Remove sections
uv run python src/inject_agents_md.py --project-path . --remove --dry-run

# Use builtin template (no file dependency)
uv run python src/inject_agents_md.py --template-source builtin --project-path .
```

## Key Decisions

1. **Template source**: Auto (try file, fallback builtin). The `--template-source` flag controls this: `auto`, `file`, or `builtin`.
2. **`{N}` backwards compatibility**: The AGENTS.md template uses `{N}` for all three stats. The script also supports `{symbols}`, `{relationships}`, `{flows}` in the builtin template.
3. **Only gitnexus section participates in replacement**: The CGC section has no closing marker, so it stays in the file as-is between updates.
4. **Fence balancing**: The `_find_closing_fence()` function counts opening/closing code fences to handle nested ``` blocks correctly.

## Verification

- 22 tests pass (6 classes: TemplateExtraction, VariableSubstitution, IdempotentInjection, DryRun, RemoveSections, EdgeCases)
- Full suite: 160 tests pass
- ruff: clean
