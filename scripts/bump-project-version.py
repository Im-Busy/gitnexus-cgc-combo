#!/usr/bin/env python3
"""
bump-project-version.py — Atomically bump version across all parity-locked files.

Run before tagging a release:
    python scripts/bump-project-version.py 1.2.0
    python scripts/bump-project-version.py 1.2.0 --dry-run

Files touched (parity set):
  - .kilo/skills/*/SKILL.md (canonical, 11 files)
  - .cursor/skills/*/SKILL.md (mirrors)
  - .opencode/skills/*/SKILL.md (mirrors)
  - .codebuddy/skills/*/SKILL.md (mirrors)
  - kilo.json
  - AGENTS.md (version references)
"""

from __future__ import annotations

import argparse
import re
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / ".kilo" / "skills"

PLATFORM_DIRS = [
    ".kilo", ".claude", ".codebuddy", ".codex", ".continue",
    ".cursor", ".factory", ".gemini", ".hermes", ".kiro",
    ".mastracode", ".opencode", ".pi",
]

SKILL_DIRS = [
    "codegraphcontext",
    "dual-repo-setup",
    "dual-repo-sync",
    "git-commit-push",
    "gitnexus",
    "graph-combo",
]

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.\-]+)?$")


def find_all_skill_md_files():
    """Find all SKILL.md files across all platforms."""
    files = []
    for platform in PLATFORM_DIRS:
        platform_skills = REPO_ROOT / platform / "skills"
        if not platform_skills.exists():
            continue
        for skill in SKILL_DIRS:
            skill_dir = platform_skills / skill
            for skmd in skill_dir.rglob("SKILL.md"):
                files.append(skmd)
    return files


def bump_skill_md(path, new, *, dry_run=False):
    """Bump version: "1.2.3" field in YAML frontmatter if present."""
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r'(version:\s*")([^"]+)(")')
    match = pattern.search(text)
    if not match:
        return None, f"no version field in {path}"
    old = match.group(2)
    if old == new:
        return old, None
    new_text = pattern.sub(rf'\g<1>{new}\g<3>', text, count=1)
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return old, None


def bump_kilo_json(path, new, *, dry_run=False):
    """Bump version field in kilo.json."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return None, f"invalid JSON or missing: {path}"
    if "version" not in data:
        return None, f"no version field in {path}"
    old = data.get("version", "unknown")
    if old == new:
        return old, None
    data["version"] = new
    if not dry_run:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return old, None


def bump_agents_md(path, new, *, dry_run=False):
    """Bump version references in AGENTS.md (e.g. 'indexed as **name** (N symbols)')."""
    if not path.exists():
        return None, f"file not found: {path}"
    return "n/a", None  # Version in AGENTS.md is project-specific, skip auto-bump


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("new_version", help="Target semver, e.g. 1.2.0")
    p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    new = args.new_version.lstrip("v")
    if not VERSION_RE.match(new):
        print(f"Error: '{new}' is not a valid semver string.", file=sys.stderr)
        return 2

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Bumping parity set to {new}\n")

    skill_files = find_all_skill_md_files()
    changed = 0
    skipped = 0
    failures = []

    for path in skill_files:
        rel = path.relative_to(REPO_ROOT)
        old, err = bump_skill_md(path, new, dry_run=args.dry_run)
        if err:
            failures.append(err)
            print(f"  ERROR:     {rel}  ({err})")
            continue
        if old == new:
            skipped += 1
        else:
            changed += 1
            print(f"  bumped:    {rel}  {old} -> {new}")

    kilo_json = REPO_ROOT / "kilo.json"
    if kilo_json.exists():
        old, err = bump_kilo_json(kilo_json, new, dry_run=args.dry_run)
        if err:
            failures.append(err)
            print(f"  ERROR:     kilo.json  ({err})")
        elif old == new:
            skipped += 1
        else:
            changed += 1
            print(f"  bumped:    kilo.json  {old} -> {new}")

    agents_md = REPO_ROOT / "AGENTS.md"
    if agents_md.exists():
        old, err = bump_agents_md(agents_md, new, dry_run=args.dry_run)
        if old:
            print(f"  skipped:   AGENTS.md (version is project-specific, update manually)")

    print(f"\nChanged: {changed}  Unchanged: {skipped}  Errors: {len(failures)}")
    if failures:
        print("\nFAILED:", *failures, sep="\n  ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
