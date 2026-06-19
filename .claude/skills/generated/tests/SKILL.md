---
name: tests
description: "Skill for the Tests area of gitnexus_CGC_combo. 56 symbols across 2 files."
---

# Tests

56 symbols | 2 files | Cohesion: 74%

## When to Use

- Working with code in `tests/`
- Understanding how detect_platforms, write_mcp_config, generate_server_entry work
- Modifying tests-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/test_config_gen.py` | test_detection_on_empty_project, test_detection_kilo, test_detection_kilo_json, test_detection_claude_code, test_detection_claude_md (+42) |
| `src/config_gen.py` | detect_platforms, write_mcp_config, generate_server_entry, generate_mcp_config, load_matrix (+4) |

## Entry Points

Start here when exploring this area:

- **`detect_platforms`** (Function) — `src/config_gen.py:33`
- **`write_mcp_config`** (Function) — `src/config_gen.py:86`
- **`generate_server_entry`** (Function) — `src/config_gen.py:50`
- **`generate_mcp_config`** (Function) — `src/config_gen.py:56`
- **`write_json`** (Function) — `tests/test_config_gen.py:26`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `detect_platforms` | Function | `src/config_gen.py` | 33 |
| `write_mcp_config` | Function | `src/config_gen.py` | 86 |
| `generate_server_entry` | Function | `src/config_gen.py` | 50 |
| `generate_mcp_config` | Function | `src/config_gen.py` | 56 |
| `write_json` | Function | `tests/test_config_gen.py` | 26 |
| `load_matrix` | Function | `src/config_gen.py` | 28 |
| `validate_platform` | Function | `src/config_gen.py` | 141 |
| `cmd_setup` | Function | `src/config_gen.py` | 149 |
| `main` | Function | `src/config_gen.py` | 223 |
| `merge_into_existing` | Function | `src/config_gen.py` | 75 |
| `test_detection_on_empty_project` | Method | `tests/test_config_gen.py` | 271 |
| `test_detection_kilo` | Method | `tests/test_config_gen.py` | 277 |
| `test_detection_kilo_json` | Method | `tests/test_config_gen.py` | 284 |
| `test_detection_claude_code` | Method | `tests/test_config_gen.py` | 291 |
| `test_detection_claude_md` | Method | `tests/test_config_gen.py` | 298 |
| `test_detection_cursor_directory` | Method | `tests/test_config_gen.py` | 305 |
| `test_detection_cursorrules` | Method | `tests/test_config_gen.py` | 312 |
| `test_detection_multiple_platforms` | Method | `tests/test_config_gen.py` | 319 |
| `test_detection_cline` | Method | `tests/test_config_gen.py` | 330 |
| `test_detection_roo_code` | Method | `tests/test_config_gen.py` | 337 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → Load_matrix` | cross_community | 5 |
| `Main → Generate_server_entry` | cross_community | 5 |
| `Main → Merge_into_existing` | cross_community | 4 |

## How to Explore

1. `gitnexus_context({name: "detect_platforms"})` — see callers and callees
2. `gitnexus_query({query: "tests"})` — find related execution flows
3. Read key files listed above for implementation details
