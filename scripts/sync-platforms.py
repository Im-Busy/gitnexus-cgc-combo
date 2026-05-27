#!/usr/bin/env python3
"""
sync-platforms.py — Sync shared skill assets from canonical (.kilo/skills/)
to all per-platform mirrors.

Run from repo root:
    python scripts/sync-platforms.py
    python scripts/sync-platforms.py --dry-run
    python scripts/sync-platforms.py --verify

What it syncs:
  - All SKILL.md files (canonical source)
  - All templates, scripts, references associated with skills

What it NEVER touches:
  - Platform-specific files (hooks.json, plugin manifests)
  - Platform-specific directories that don't exist yet until the first sync

Per-platform manifest defines where each skill lives.
Uses SHA-256 comparison to only touch files that actually changed.
"""

import argparse
import shutil
import sys
import hashlib
from pathlib import Path

CANONICAL = Path(".kilo/skills")

SKILL_DIRS = [
    "codegraphcontext",
    "dual-repo-setup",
    "dual-repo-sync",
    "git-commit-push",
    "gitnexus",
    "graph-combo",
]

PLATFORM_MANIFESTS = {
    ".claude":    ".claude/skills",
    ".codebuddy": ".codebuddy/skills",
    ".codex":     ".codex/skills",
    ".continue":  ".continue/skills",
    ".cursor":    ".cursor/skills",
    ".factory":   ".factory/skills",
    ".gemini":    ".gemini/skills",
    ".hermes":    ".hermes/skills",
    ".kiro":      ".kiro/skills",
    ".mastracode": ".mastracode/skills",
    ".opencode":  ".opencode/skills",
    ".pi":        ".pi/skills",
}


def file_hash(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except FileNotFoundError:
        return None


def sync_tree(src_dir, dst_dir, *, dry_run=False, verbose=True):
    """Recursively sync all files from src_dir to dst_dir via SHA-256 comparison.

    Returns dict of {action: count}.
    """
    stats = {"created": 0, "updated": 0, "skipped": 0, "missing_src": 0}
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)

    if not src_dir.exists():
        stats["missing_src"] += 1
        if verbose:
            print(f"    MISSING canonical: {src_dir}")
        return stats

    for src_file in sorted(src_dir.rglob("*")):
        if src_file.is_dir():
            continue
        rel = src_file.relative_to(src_dir)
        dst_file = dst_dir / rel
        src_h = file_hash(src_file)
        dst_h = file_hash(dst_file)

        if src_h == dst_h:
            stats["skipped"] += 1
            continue

        action = "created" if dst_h is None else "updated"
        stats[action] += 1

        if not dry_run:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            if verbose:
                print(f"    {action.upper()}: {dst_file}")
        else:
            if verbose:
                print(f"    WOULD {action}: {dst_file}")

    return stats


def verify_tree(src_dir, dst_dir):
    """Check for drift between canonical and mirror. Returns list of drifted paths."""
    drifted = []
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)

    if not src_dir.exists():
        return [f"{src_dir} (canonical missing)"]

    for src_file in sorted(src_dir.rglob("*")):
        if src_file.is_dir():
            continue
        rel = src_file.relative_to(src_dir)
        dst_file = dst_dir / rel
        src_h = file_hash(src_file)
        dst_h = file_hash(dst_file)

        if src_h and dst_h and src_h != dst_h:
            drifted.append(str(dst_file))
        elif src_h and not dst_h:
            drifted.append(f"{dst_file} (missing)")

    return drifted


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Sync shared skill assets from .kilo/skills/ to all platform mirrors."
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    parser.add_argument("--verify", action="store_true", help="Check for drift; exit 1 if found.")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-file output.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if not CANONICAL.exists():
        print(f"Error: Canonical source not found at {CANONICAL}/")
        print("Run this script from the repo root.")
        sys.exit(1)

    label = "[DRY RUN] " if args.dry_run else "[VERIFY] " if args.verify else ""
    print(f"{label}Syncing skills from {CANONICAL}/\n")

    if args.verify:
        total_drift = 0
        for platform, mirror_base in sorted(PLATFORM_MANIFESTS.items()):
            mirror_dir = Path(mirror_base)
            if not mirror_dir.exists():
                continue
            print(f"  {platform}/")
            for skill in SKILL_DIRS:
                src = CANONICAL / skill
                dst = mirror_dir / skill
                drifted = verify_tree(src, dst)
                for d in drifted:
                    print(f"    DRIFT: {d}")
                    total_drift += 1
                if not drifted and src.exists():
                    if not args.quiet:
                        print(f"    {skill}: up to date")
            print()
        if total_drift > 0:
            print(f"DRIFT DETECTED: {total_drift} file(s) out of sync.")
            print("Run 'python scripts/sync-platforms.py' to fix.")
            sys.exit(1)
        else:
            print("All platform mirrors are in sync.")
            sys.exit(0)

    grand_total = {"created": 0, "updated": 0, "skipped": 0, "missing_src": 0}

    for platform, mirror_base in sorted(PLATFORM_MANIFESTS.items()):
        mirror_dir = Path(mirror_base)
        print(f"  {platform}/")
        for skill in SKILL_DIRS:
            src = CANONICAL / skill
            dst = mirror_dir / skill
            stats = sync_tree(src, dst, dry_run=args.dry_run, verbose=not args.quiet)
            for k, v in stats.items():
                grand_total[k] += v
            if args.quiet:
                created_updated = stats["created"] + stats["updated"]
                if created_updated > 0:
                    print(f"    {skill}: {created_updated} changed ({stats['skipped']} skipped)")
        print()

    print("-" * 50)
    print(f"  Created:  {grand_total['created']}")
    print(f"  Updated:  {grand_total['updated']}")
    print(f"  Skipped:  {grand_total['skipped']} (already up to date)")
    if grand_total["missing_src"] > 0:
        print(f"  Missing:  {grand_total['missing_src']} (canonical source not found)")
    if args.dry_run:
        print("\n  This was a dry run. No files were modified.")
        print("  Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
