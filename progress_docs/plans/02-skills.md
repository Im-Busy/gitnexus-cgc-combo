---
phase: 02
name: Portable Skills — Multi-Platform Distribution
status: complete
depends_on: [01]
blocks: []
---

# Phase 02: Portable Skills

## Goal

Ensure the 8 operational skills (gitnexus × 6, cgc × 1, combo × 1) are distributed correctly to each platform's skill system. Kilo and Claude Code have native skill directories. All other platforms rely on behavioral rules embedded in AGENTS.md sections.

## Tasks

| Priority | Task# | Task | Status | Notes |
|----------|-------|------|--------|-------|
| P0 | 02-1 | Skills for Kilo | ✅ Done | `.kilo/skills/` already contains all 8 skills. `kilo.json` points to `.kilo/skills`. |
| P0 | 02-2 | Skills for Claude Code | ✅ Done | AGENTS.md Phase 7 documents copy from `.kilo/skills/` → `.claude/skills/` |
| P0 | 02-3 | Meta-directives documented | ✅ Done | AGENTS.md Phase 6 Step 2: 1-3 line redirects for CLAUDE.md, .cursorrules, .clinerules, .roorules, .windsurfrules, .github/copilot-instructions.md |
| P1 | 02-4 | Skill path normalization | ✅ Done | `inject_agents_md.py` --skills-platform flag: normalizes `.claude/skills/` → `.kilo/skills/` for Kilo, replaces CLI table with inline behavioral rules for non-skill platforms |
| P1 | 02-5 | Platform instruction file detection | ✅ Done | `rule_extractor.py` detect_existing_instruction_files() + get_platform_instruction_files(): uses matrix.json instructions_files, excludes AGENTS.md |
| P1 | 02-6 | Rule extraction for non-skill platforms | ✅ Done | `rule_extractor.py` (290 LOC): extract_always_do(), extract_never_do(), extract_behavioral_rules(), write_meta_directive(), write_rules_to_instruction_file(), write_platform_directives(). Added .cursorrules to matrix.json cursor instructions_files |
| P2 | 02-7 | Skill generation from AGENTS.md | ⏳ Deferred | Auto-generate skill files. Deferred: AGENTS.md inline rules are sufficient. |
| P2 | 02-8 | Cross-skill validation | ⏳ Deferred | Verify skill references consistent. Deferred: low risk, manual review sufficient. |

## Completed Work

### 02-4: Skill Path Normalization
Added `--skills-platform` flag to `inject_agents_md.py`. When set:
- **Kilo**: replaces `.claude/skills/` with `.kilo/skills/` in the CLI table
- **Claude Code**: keeps `.claude/skills/` as-is
- **Non-skill platforms (cursor, cline, roo-code, windsurf, etc.)**: removes the CLI table entirely and replaces it with a "Key Behaviors" section containing extracted Always Do / Never Do rules

### 02-5: Platform Instruction File Detection
Two new functions in `rule_extractor.py`:
- `get_platform_instruction_files(project_path, platform_ids)` — iterates platform instruction files from matrix.json (excluding AGENTS.md)
- `detect_existing_instruction_files(project_path, platform_ids)` — returns {platform_id: [existing_paths]} for files that already exist on disk

### 02-6: Rule Extraction
Created `src/rule_extractor.py` (290 LOC) with:
- `extract_always_do(template)` / `extract_never_do(template)` — extract bullet lists from markdown sections
- `extract_behavioral_rules(template)` — combined Always Do + Never Do block
- `normalize_skill_paths(template, platform_id)` — platform-aware skill path normalization
- `write_meta_directive(path, platform_id)` — writes 1-3 line redirect to AGENTS.md
- `write_rules_to_instruction_file(path, template, platform_id)` — writes full behavioral rules for non-skill platforms
- `write_platform_directives(project_path, platform_ids, template)` — batch writes directives/rules for all platforms
- Standalone CLI: `uv run python src/rule_extractor.py --project-path ... --platforms ... --extract-rules`

Also updated `inject_agents_md.py` with `--skills-platform` and `--write-directives` flags that chain into rule_extractor. |

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Skills only for Kilo + Claude Code | Only two with native skill systems. Behavioral rules in AGENTS.md are read by ALL platforms. |
| Meta-directive pattern (1-3 lines) | Lightweight, least intrusive. Points to AGENTS.md as single source of truth. |
| Skill files live in `.kilo/skills/` | This repo's canonical location. Copied to `.claude/skills/` during Claude Code bootstrap. |