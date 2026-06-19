---
description: "Health check for GitNexus + CodeGraphContext — verifies indexes, watcher, and MCP connectivity"
---

Run a full health check on the GitNexus + CGC setup in this project:

- Index freshness (both tools)
- Watcher status
- MCP connectivity
- Disk usage
- Version checks

Use `--verify` to also test MCP tool connectivity. Use `--quick` to skip MCP tests. Produce a report with status, issues found, and recommended actions.
