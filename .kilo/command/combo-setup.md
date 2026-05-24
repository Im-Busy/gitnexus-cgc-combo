---
name: combo-setup
description: "Provision GitNexus + CodeGraphContext — detect, install, configure, index, verify"
agent: combo-setup
---

Usage: `/combo-setup`

Provisions GitNexus + CodeGraphContext for your project. The agent:
1. Detects which AI platform(s) you use
2. Checks your environment
3. Installs both tools
4. Generates MCP configs (merges, never replaces)
5. Indexes your project
6. Starts the code graph watcher
7. Writes the combo protocol into your AGENTS.md

Say "set up code intelligence" or `/combo-setup` and the agent handles everything.
