---
name: combo-diagnose
description: "Health check for GitNexus + CodeGraphContext — verifies indexes, watcher, and MCP connectivity"
agent: combo-diagnose
---

Usage: `/combo-diagnose`

Runs a full health check on your GitNexus + CGC setup:
- Index freshness (both tools)
- Watcher status
- MCP connectivity
- Disk usage
- Version checks

Produces a report with status, issues found, and recommended actions.
