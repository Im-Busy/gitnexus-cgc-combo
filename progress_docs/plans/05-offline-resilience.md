---
phase: 05
name: Offline & Resilience — Error Recovery + No-Network
status: complete
depends_on: [01]
blocks: []
completed: 2026-05-23
---

# Phase 05: Offline & Resilience

## Goal

Graceful degradation when network is unavailable. Phase error boundaries for safe partial installs. Cache detection to skip redundant installs. Bootstrap state tracking for resume after interruption.

## Tasks

| Priority | Task# | Task | Status | Notes |
|----------|-------|------|--------|-------|
| P0 | 05-1 | Network connectivity pre-check | ✅ Done | `setup_combo.py`: `check_network()` checks npmjs.org, pypi.org, github.com via socket connection. Integrated into main(). |
| P0 | 05-2 | Phase error boundaries | ✅ Done | AGENTS.md Critical section: dependency table, failure modes, skip-what-on-failure, agent reports summary |
| P0 | 05-3 | Verify-only mode | ✅ Done | `combo-diagnose.md`: 3 modes (Full/Verify-only/Quick), targeted fix suggestions per failing check, exit code protocol |
| P0 | 05-4 | Cache detection | ✅ Done | `setup_combo.py`: `check_cache()` detects if gitnexus + cgc already installed. Integrated into main() with offline-capable bootstrap message. |
| P1 | 05-5 | Partial bootstrap recovery | ✅ Done | `src/bootstrap_state.py`: compact state file, save_state/mark_phase_failed/get_resume_phase/clear_state. CLI with --save/--fail/--report/--resume/--clear. |
| P1 | 05-6 | Stale index detection | ✅ Done | `combo-diagnose.md`: check `git log -1 --format=%H` vs `.gitnexus/last-indexed-commit`. Indexes marked stale if HEAD differs. |
| P1 | 05-7 | Config backup on corruption | ✅ Done | `config_gen.py` already handles via `--force` flag (backs up to .bak). Error message already tells user about `--force`. |
| P2 | 05-8 | Offline-first mode | ⏳ Deferred | Bundle minimal config templates. Deferred: cache detection + offline warning are sufficient. |
| P2 | 05-9 | Watcher self-healing | ✅ Done | Covered by watcher auto-restart in Phase 04 (systemd Restart=on-failure, launchd KeepAlive). |

## Files Created/Modified

```
NEW:
  src/bootstrap_state.py                 (bootstrap state tracker, ~110 LOC)

MODIFIED:
  src/setup_combo.py                     (added check_network, check_cache, print_network_report, print_cache_report functions)
  AGENTS.md Critical section            (added phase error boundaries table with dependencies and skip-on-failure rules)
  .kilo/agent/combo-diagnose.md         (added verify-only mode, stale index detection, bootstrap state check, targeted fix suggestions)
```

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Socket connection check over HTTP request | Lighter weight, no dependency on requests library, fast timeout |
| 3 registries checked (npm, PyPI, GitHub) | Covers all download sources. Partial failure shows granular status. |
| Bootstrap state file uses JSON | Simple, agent-readable, no schema required. Idempotent save (no duplicate phases). |
| Verify-only mode in combo-diagnose.md | Follows existing agent protocol. Exit code 0/1 for scripting-friendly verification. |
| Phase error boundaries as table | Most scannable format for agents. Shows dependency chain and skip rules at a glance. |

## Verification

- [x] `check_network()` returns dict with per-registry boolean, handles OSError gracefully
- [x] `check_cache()` detects installed gitnexus/cgc, reports versions
- [x] Network report shows UNREACHABLE warning when registries down
- [x] Cache report shows CACHED/NOT CACHED with versions
- [x] `bootstrap_state.py` save/load/clear/idempotent save all work
- [x] `bootstrap_state.py` mark_phase_failed preserves error details
- [x] `bootstrap_state.py` CLI --save/--fail/--report/--resume/--clear all pass
- [x] AGENTS.md contains phase error boundaries table
- [x] combo-diagnose.md has verify-only mode with targeted fix suggestions
- [x] combo-diagnose.md has stale index detection check