"""
Multi-platform MCP config generator for GitNexus + CGC combo.

Reads platforms/matrix.json and generates the correct MCP server configuration
for any supported AI coding platform. Handles merge-with-existing, create-new,
and print-for-manual-paste strategies.

Usage:
    # Full setup (MCP configs + indexing)
    uv run combo-setup setup /path/to/project [--cgc-path /path/to/cgc]

    # Config-only mode
    uv run combo-setup --platform cursor --project-path /path/to/project
    uv run combo-setup --detect --project-path /path/to/project
    uv run combo-setup --print --platform windsurf
"""

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

MATRIX_PATH = Path(__file__).parent.parent / "platforms" / "matrix.json"


def load_matrix() -> dict:
    with open(MATRIX_PATH, encoding="utf-8") as f:
        return json.load(f)


def detect_platforms(project_path: Path) -> list[str]:
    """Scan project directory for platform config markers. Returns detected platform IDs."""
    matrix = load_matrix()
    detected = []
    for pid, pdef in matrix["platforms"].items():
        for marker in pdef.get("detection_markers", []):
            full = project_path / marker
            if marker.endswith("/"):
                if full.is_dir():
                    detected.append(pid)
                    break
            elif full.exists():
                detected.append(pid)
                break
    return detected


def generate_server_entry(server_name: str, server_def: dict, mcp_family: str) -> dict:
    """Generate a single MCP server entry in the target family's format."""
    family_def = server_def.get(f"{mcp_family}_format", server_def.get("mcpServers_format", {}))
    return {server_name: dict(family_def)}


def generate_mcp_config(platform_id: str, cgc_path: str | None = None) -> dict | None:
    """Generate MCP config for a single platform. Returns None if platform unknown."""
    matrix = load_matrix()
    pdef = matrix["platforms"].get(platform_id)
    if not pdef:
        return None

    family = pdef["mcp_family"]
    wrapper_key = matrix["mcp_families"][family]["wrapper_key"]

    gn_entry = generate_server_entry("gitnexus", matrix["gitnexus_server"], family)
    cgc_entry = generate_server_entry("codegraphcontext", matrix["codegraphcontext_server"], family)

    if cgc_path:
        cgc_entry["codegraphcontext"]["cwd" if "cwd" in cgc_entry["codegraphcontext"] else "workdir"] = cgc_path

    return {wrapper_key: {**gn_entry, **cgc_entry}}


def merge_into_existing(existing: dict, new_entries: dict) -> dict:
    """Merge new MCP server entries into existing config. Existing entries are preserved."""
    for wrapper_key, servers in new_entries.items():
        if wrapper_key not in existing:
            existing[wrapper_key] = {}
        for server_name, server_config in servers.items():
            if server_name not in existing[wrapper_key]:
                existing[wrapper_key][server_name] = server_config
    return existing


def write_mcp_config(
    platform_id: str,
    project_path: Path,
    cgc_path: str | None = None,
    force: bool = False,
) -> tuple[str, str]:
    """
    Generate and write MCP config for a platform.
    Returns (status, message) where status is 'merged', 'created', 'skipped', 'manual', or 'error'.
    """
    matrix = load_matrix()
    pdef = matrix["platforms"].get(platform_id)
    if not pdef:
        return ("error", f"Unknown platform: {platform_id}")

    if not pdef.get("auto_mcp"):
        config = generate_mcp_config(platform_id, cgc_path)
        dest = pdef.get("mcp_manual_destination", "MCP settings panel")
        return ("manual", f"Manual config for {pdef['name']}:\nPaste into {dest}:\n{json.dumps(config, indent=2)}")

    new_config = generate_mcp_config(platform_id, cgc_path)
    if not new_config:
        return ("error", f"Failed to generate config for {platform_id}")

    config_file = project_path / pdef["mcp_file"]
    config_file.parent.mkdir(parents=True, exist_ok=True)

    should_create = False
    if config_file.exists():
        try:
            existing = json.loads(config_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            if force:
                backup = config_file.with_suffix(config_file.suffix + ".bak")
                config_file.rename(backup)
                print(f"\u26a0 Backed up invalid JSON to {backup}")
                should_create = True
            else:
                return ("error", f"{config_file} exists but is not valid JSON. Use --force to overwrite.")
        else:
            wrapper_key = matrix["mcp_families"][pdef["mcp_family"]]["wrapper_key"]
            existing_servers = set(existing.get(wrapper_key, {}).keys())
            new_servers = set(new_config[wrapper_key].keys())
            if new_servers <= existing_servers:
                return ("skipped", f"All servers already configured in {config_file}")
            merged = merge_into_existing(existing, new_config)
            config_file.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
            added = new_servers - existing_servers
            return ("merged", f"Merged {', '.join(sorted(added))} into existing {config_file}")

    if not config_file.exists() or should_create:
        config_file.write_text(json.dumps(new_config, indent=2) + "\n", encoding="utf-8")
        return ("created", f"Created {config_file} with gitnexus + codegraphcontext")


def validate_platform(platform_id: str) -> tuple[bool, str]:
    """Check if platform is valid."""
    matrix = load_matrix()
    if platform_id in matrix["platforms"]:
        return (True, "")
    return (False, f"Unknown platform '{platform_id}'. Known: {', '.join(sorted(matrix['platforms'].keys()))}")


def cmd_setup(project_path: Path, cgc_path: str | None, skip_index: bool = False) -> None:
    """Run full setup: detect platforms, write MCP configs, index both tools, print summary."""
    matrix = load_matrix()

    print(f"\n{'=' * 60}")
    print(f"GitNexus + CGC Setup")
    print(f"Project: {project_path}")
    print(f"{'=' * 60}\n")

    platforms = detect_platforms(project_path)
    if not platforms:
        print("No supported AI coding platforms detected.")
        print(f"Run with --platform to specify one explicitly.")
        print(f"Known: {', '.join(sorted(matrix['platforms'].keys()))}")
        sys.exit(1)
    print(f"Detected platforms: {', '.join(platforms)}")

    print(f"\n--- MCP Config Generation ---")
    errors = 0
    for pid in platforms:
        pdef = matrix["platforms"][pid]
        status, message = write_mcp_config(pid, project_path, cgc_path, force=False)
        prefix = {
            "created": "[NEW]", "merged": "[OK]", "skipped": "[SKIP]",
            "manual": "[MANUAL]", "error": "[ERR]",
        }.get(status, "[?]")
        print(f"  {prefix} {pdef['name']}: {message}")
        if status in ("error", "manual"):
            errors += 1

    if skip_index:
        print("\nSkipping indexing (--skip-index). Run manually:")
        print(f"  npx gitnexus analyze --embeddings --skills")
        print(f"  uv run cgc index {project_path}")
        return

    print(f"\n--- GitNexus Indexing ---")
    try:
        subprocess.run(
            ["npx", "gitnexus", "analyze", "--embeddings", "--skills"],
            cwd=str(project_path), check=True,
        )
        print("  [OK] GitNexus indexed successfully")
    except subprocess.CalledProcessError:
        print("  [WARN] GitNexus indexing failed. Run manually: npx gitnexus analyze --embeddings --skills")
    except FileNotFoundError:
        print("  [WARN] npx not found. Install Node.js >= 18 and try again.")

    print(f"\n--- CodeGraphContext Indexing ---")
    try:
        subprocess.run(
            ["uv", "run", "cgc", "index", str(project_path)],
            cwd=str(project_path), check=True,
        )
        print("  [OK] CGC indexed successfully")
    except subprocess.CalledProcessError:
        print(f"  [WARN] CGC indexing failed. Run manually: uv run cgc index {project_path}")
    except FileNotFoundError:
        print("  [WARN] uv not found. Install uv and try again.")

    print(f"\n--- Summary ---")
    print(f"Platforms configured: {', '.join(platforms)}")
    print(f"Next steps:")
    print(f"  1. Restart your AI coding tool to load MCP servers")
    print(f"  2. Start CGC watcher: uv run cgc watch {project_path}/src")
    print(f"  3. Verify: npx gitnexus status && uv run cgc stats {project_path}")

    if errors:
        print(f"\n{errors} manual/external actions needed. See [MANUAL] entries above.")
        sys.exit(1)

    print(f"\nSetup complete.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GitNexus + CGC combo: MCP config generator and setup orchestrator"
    )
    subparsers = parser.add_subparsers(dest="command")

    setup_parser = subparsers.add_parser("setup", help="Full setup: detect, configure MCP, index")
    setup_parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="Path to the user's project root (default: current directory)",
    )
    setup_parser.add_argument(
        "--cgc-path",
        default=None,
        help="Path to CodeGraphContext clone (for workdir/cwd in MCP config)",
    )
    setup_parser.add_argument(
        "--skip-index",
        action="store_true",
        help="Skip GitNexus and CGC indexing (config generation only)",
    )

    parser.add_argument(
        "--platform",
        help="Target platform ID (kilo, claude-code, cursor, cline, roo-code, continue, opencode, copilot-vscode, copilot-cli, windsurf, augment)",
    )
    parser.add_argument(
        "--detect",
        action="store_true",
        help="Detect all platforms present in project and generate configs for each",
    )
    parser.add_argument(
        "--project-path",
        default=".",
        help="Path to the user's project root (default: current directory)",
    )
    parser.add_argument(
        "--cgc-path",
        default=None,
        help="Path to CodeGraphContext clone (for workdir/cwd in MCP config). Omit if CGC is pip-installed.",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print config to stdout instead of writing to file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing config files even if they contain invalid JSON",
    )
    parser.add_argument(
        "--list-platforms",
        action="store_true",
        help="List all supported platforms and exit",
    )

    args = parser.parse_args()

    if args.command == "setup":
        project_path = Path(args.project).resolve()
        if not project_path.is_dir():
            print(f"Error: project path does not exist: {project_path}", file=sys.stderr)
            sys.exit(1)
        cgc_path = args.cgc_path
        if cgc_path:
            cgc_path = str(Path(cgc_path).resolve())
        cmd_setup(project_path, cgc_path, skip_index=args.skip_index)
        return

    project_path = Path(args.project_path).resolve()

    if not project_path.is_dir():
        print(f"Error: project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)

    matrix = load_matrix()

    if args.list_platforms:
        print("Supported platforms:")
        for pid, pdef in sorted(matrix["platforms"].items()):
            auto = "auto" if pdef.get("auto_mcp") else "manual"
            print(f"  {pid:20s} {pdef['name']:25s} MCP: {auto:6s}  family: {pdef['mcp_family']}")
        sys.exit(0)

    if args.detect:
        platforms = detect_platforms(project_path)
        if not platforms:
            print("No supported platforms detected. Use --platform to specify one explicitly.")
            print(f"Known platforms: {', '.join(sorted(matrix['platforms'].keys()))}")
            sys.exit(1)
        print(f"Detected platforms: {', '.join(platforms)}")
    elif args.platform:
        valid, err = validate_platform(args.platform)
        if not valid:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        platforms = [args.platform]
    else:
        parser.print_help()
        sys.exit(1)

    cgc_path = args.cgc_path
    if cgc_path:
        cgc_path = str(Path(cgc_path).resolve())

    errors = 0
    for pid in platforms:
        pdef = matrix["platforms"][pid]
        if args.print:
            config = generate_mcp_config(pid, cgc_path)
            if config:
                print(f"\n# {pdef['name']} ({pid}) -> {pdef.get('mcp_file', 'manual')}")
                print(json.dumps(config, indent=2))
        else:
            status, message = write_mcp_config(pid, project_path, cgc_path, force=args.force)
            prefix = {"created": "[NEW]", "merged": "[OK]", "skipped": "[SKIP]", "manual": "[MANUAL]", "error": "[ERR]"}.get(status, "[?]")
            print(f"  {prefix} {pdef['name']} {message}")
            if status == "error":
                errors += 1
            elif status == "manual":
                errors += 1

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
