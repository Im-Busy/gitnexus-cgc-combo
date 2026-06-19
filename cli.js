#!/usr/bin/env node
"use strict";

const { spawnSync } = require("child_process");
const path = require("path");

const packageRoot = path.resolve(__dirname);
const args = process.argv.slice(2);

function exec(args, opts) {
  return spawnSync(args[0], args.slice(1), {
    cwd: packageRoot,
    stdio: "inherit",
    ...opts,
  });
}

function tryRun(cmd, scriptArgs) {
  const result = exec([cmd, ...scriptArgs]);
  if (result.error && result.error.code === "ENOENT") {
    return null;
  }
  return result;
}

if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
  console.log(`gitnexus-cgc-combo ${require("./package.json").version}

Code Intelligence Bootstrap Kit — provision GitNexus + CodeGraphContext for AI coding agents.

USAGE:
  npx gitnexus-cgc-combo <command> [options]

COMMANDS:
  setup <path>         Full setup: detect platforms, configure MCP, index both tools
                       Options: --cgc-path <path>  --skip-index

OPTIONS:
  --platform <id>      Target a specific platform (kilo, cursor, cline, etc.)
  --detect             Auto-detect all platforms and configure them
  --project-path <p>   Path to the user's project root (default: .)
  --list-platforms     List all supported platforms
  --cgc-path <path>    Path to CodeGraphContext clone directory
  --print              Print MCP config to stdout instead of writing to file
  --force              Overwrite existing configs even if corrupted

EXAMPLES:
  npx gitnexus-cgc-combo setup ./my-project
  npx gitnexus-cgc-combo --detect --project-path ./my-project
  npx gitnexus-cgc-combo --platform cursor --project-path . --print

Requires: Python >= 3.10 and uv.
Install uv: https://docs.astral.sh/uv/getting-started/installation/
`);
  process.exit(0);
}

if (args[0] === "setup" || args[0] === "config") {
  const result = tryRun("uv", ["run", "combo-setup", ...args]);
  if (result) {
    process.exit(result.status || 0);
  }
  const pyResult = tryRun("python3", ["-m", "src.config_gen", ...args]);
  if (pyResult) {
    process.exit(pyResult.status || 0);
  }
  const pyResult2 = tryRun("python", ["-m", "src.config_gen", ...args]);
  if (pyResult2) {
    process.exit(pyResult2.status || 0);
  }
  console.error(
    "Error: Neither 'uv', 'python3', nor 'python' found in PATH.",
  );
  console.error(
    "Install uv: https://docs.astral.sh/uv/getting-started/installation/",
  );
  console.error(
    "Or install Python >= 3.10 with codegraphcontext: pip install codegraphcontext",
  );
  process.exit(1);
}

const result = tryRun("uv", ["run", "combo-setup", ...args]);
if (result) {
  process.exit(result.status || 0);
}
const pyResult = tryRun("python3", ["-m", "src.config_gen", ...args]);
if (pyResult) {
  process.exit(pyResult.status || 0);
}
const pyResult2 = tryRun("python", ["-m", "src.config_gen", ...args]);
if (pyResult2) {
  process.exit(pyResult2.status || 0);
}
console.error(
  "Error: Neither 'uv', 'python3', nor 'python' found in PATH.",
);
console.error(
  "Install uv: https://docs.astral.sh/uv/getting-started/installation/",
);
process.exit(1);
