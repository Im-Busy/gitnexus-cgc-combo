---
phase: 04
name: Watcher Hardening — Survivable Background Process
status: complete
depends_on: [01]
blocks: []
completed: 2026-05-23
---

# Phase 04: Watcher Hardening

## Goal

Make the CGC live watcher survive terminal closes and machine reboots across all platforms. Provide platform-native service templates (systemd, launchd) and cross-platform status checks.

## Tasks

| Priority | Task# | Task | Status | Notes |
|----------|-------|------|--------|-------|
| P0 | 04-1 | Windows Start-Process | ✅ Done | Already correct in AGENTS.md — `Start-Process -NoNewWindow -PassThru` survives terminal close |
| P0 | 04-2 | Linux systemd user service | ✅ Done | `templates/cgc-watcher.service` with Restart=on-failure, RestartSec=5, journald logging, security hardening |
| P0 | 04-3 | macOS launchd plist | ✅ Done | `templates/com.gitnexus.cgc-watcher.plist` with KeepAlive, RunAtLoad, ThrottleInterval=5, log paths |
| P1 | 04-4 | Cross-platform watcher status | ✅ Done | AGENTS.md Phase 5: pgrep, systemctl is-active, launchctl list, Get-Process |
| P1 | 04-5 | Auto-restart on crash | ✅ Done | systemd `Restart=on-failure`, launchd `KeepAlive`, Windows survives terminal close (existing) |
| P2 | 04-6 | Watcher health metric | ⏳ Deferred | CLI to check CPU/memory/last update. Deferred: combo-diagnose covers basic status. |

## Files Created/Modified

```
NEW:
  templates/cgc-watcher.service           (systemd user service, 28 LOC)
  templates/com.gitnexus.cgc-watcher.plist (macOS launchd plist, 48 LOC)

MODIFIED:
  AGENTS.md Phase 5                       (added systemd, launchd, cross-platform status sections)
```

## Verification

- [x] systemd template has `[Unit]`, `[Service]`, `[Install]` sections
- [x] systemd template has `Restart=on-failure` + `RestartSec=5`
- [x] systemd template has security hardening (NoNewPrivileges, PrivateTmp, ProtectSystem)
- [x] launchd template has `KeepAlive`, `RunAtLoad`
- [x] launchd template has `StandardOutPath` + `StandardErrorPath`
- [x] Both templates use `<CGCDIR>`, `<PROJECT>` placeholders (non-destructive, filled by agent)
- [x] AGENTS.md Phase 5 documents all 3 platform watcher methods
- [x] Cross-platform status checks documented