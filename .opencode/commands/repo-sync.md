---
description: Sync curated files from private dev repo to public-facing repo
agent: repo-syncer
subtask: true
---

Sync curated files from the private development repo to the public-facing repo. Merges master into public, runs safety checks for leaked private files, verifies, and pushes. Only pushes the public branch — never leaks IDE configs, memory, or progress docs.

Usage:
- `/repo-sync` — Full sync: merge master → public → push
- `/repo-sync check` — Safety check only: verify no private files on public branch
- `/repo-sync status` — Show current branch state and remote config

Read `.kilo/skills/dual-repo-sync/SKILL.md` for the detailed protocol.
