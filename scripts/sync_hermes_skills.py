#!/usr/bin/env python3
"""Generate the Hermes copies of skills that live in both trees.

.claude/skills/<name>/ is the source of truth. For every skill listed in
MIRRORS this writes .hermes/skills/<category>/<name>/ with the same
instructions and bundled files in the shape Hermes expects:

- a short description, because the Hermes skill index shows only the first
  60 characters;
- a "When to Use" section, which Hermes's skill linter looks for, filled from
  the trigger part of the source description;
- Hermes frontmatter (version, author, license, metadata.hermes).

Never edit a Hermes copy by hand: edit the source and re-run this script.

Usage:
  python3 scripts/sync_hermes_skills.py          # write the copies
  python3 scripts/sync_hermes_skills.py --check  # exit 1 if a copy is stale (CI)
Needs: PyYAML
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_DIR = ROOT / ".claude" / "skills"
HERMES_DIR = ROOT / ".hermes" / "skills"

# Skills mirrored into the Hermes tree: category folder, index description
# (at most HERMES_MAX_DESCRIPTION characters, ending in a period) and tags.
MIRRORS: dict[str, dict] = {
    "github-actions": {
        "category": "github",
        "description": "Use when writing, changing or debugging CI workflows.",
        "tags": ["GitHub", "Actions", "CI", "Workflows"],
    },
    "github-releases": {
        "category": "github",
        "description": "Use when tagging a version or publishing a release.",
        "tags": ["GitHub", "Releases", "Tags", "Versioning"],
    },
    "github-docs": {
        "category": "github",
        "description": "Use when opening a PR or changing documented behavior.",
        "tags": ["GitHub", "Documentation", "README", "Pull Requests"],
    },
    "linear-issues": {
        "category": "productivity",
        "description": "Use for any Linear issue work. Marks agent comments.",
        "tags": ["Linear", "Issues", "Comments", "Project Management"],
    },
}

HERMES_MAX_DESCRIPTION = 60

AUTHOR = "richardkfm/vibes"
LICENSE = "MIT"
DEFAULT_VERSION = "1.0.0"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RELATED_RE = re.compile(r"^#{2,}\s*Related skills\s*$(.*?)(?=^#{1,6}\s|\Z)", re.M | re.S | re.I)


def split_frontmatter(text: str) -> tuple[dict, str]:
    end = text.find("\n---", 4)
    if not text.startswith("---\n") or end == -1:
        raise ValueError("no frontmatter block")
    return yaml.safe_load(text[4:end]), text[end + 4 :].lstrip("\n")


def related_skills(body: str, known: set[str], own_name: str) -> list[str]:
    found: list[str] = []
    for section in RELATED_RE.findall(body):
        for token in re.findall(r"`([^`\n]+)`", section):
            if NAME_RE.match(token) and token in known and token != own_name and token not in found:
                found.append(token)
    return found


def flow_list(items: list[str]) -> str:
    return "[" + ", ".join(items) + "]"


def with_when_to_use(body: str, source_description: str) -> str:
    """Insert a "When to Use" section before the first second-level heading."""
    if re.search(r"^## When to Use\s*$", body, re.M | re.I):
        return body
    start = source_description.find("Use when")
    triggers = source_description[start:] if start != -1 else source_description
    section = f"## When to Use\n\n{triggers.strip()}\n\n"
    first_h2 = re.search(r"^## ", body, re.M)
    if first_h2 is None:
        return body.rstrip("\n") + "\n\n" + section.rstrip("\n") + "\n"
    return body[: first_h2.start()] + section + body[first_h2.start() :]


def render_skill_md(name: str, config: dict, known: set[str]) -> str:
    source = CLAUDE_DIR / name / "SKILL.md"
    meta, body = split_frontmatter(source.read_text(encoding="utf-8"))
    version = str((meta.get("metadata") or {}).get("version", DEFAULT_VERSION))
    description = config["description"]
    if len(description) > HERMES_MAX_DESCRIPTION or not description.endswith("."):
        raise SystemExit(
            f"MIRRORS['{name}'] description must be at most {HERMES_MAX_DESCRIPTION} characters"
            f" and end with a period (it is {len(description)})"
        )
    lines = [
        "---",
        f"name: {meta['name']}",
        # A JSON string is a valid YAML double-quoted scalar; this keeps colons and quotes safe.
        f"description: {json.dumps(description, ensure_ascii=False)}",
        f"version: {version}",
        f"author: {AUTHOR}",
        f"license: {LICENSE}",
        "metadata:",
        "  hermes:",
        f"    tags: {flow_list(config['tags'])}",
    ]
    related = related_skills(body, known, name)
    if related:
        lines.append(f"    related_skills: {flow_list(related)}")
    lines += [
        "---",
        "",
        f"<!-- Generated from .claude/skills/{name}/SKILL.md by scripts/sync_hermes_skills.py."
        " Edit the source and re-run the script. -->",
        "",
    ]
    return "\n".join(lines) + with_when_to_use(body, meta["description"])


def expected_files(known: set[str]) -> dict[Path, bytes]:
    """Every file the Hermes tree should contain for the mirrored skills."""
    files: dict[Path, bytes] = {}
    for name, config in MIRRORS.items():
        source_dir = CLAUDE_DIR / name
        target_dir = HERMES_DIR / config["category"] / name
        if not (source_dir / "SKILL.md").exists():
            raise SystemExit(f"MIRRORS lists '{name}' but .claude/skills/{name}/SKILL.md does not exist")
        files[target_dir / "SKILL.md"] = render_skill_md(name, config, known).encode("utf-8")
        for path in sorted(p for p in source_dir.rglob("*") if p.is_file() and p.name != "SKILL.md"):
            files[target_dir / path.relative_to(source_dir)] = path.read_bytes()
    return files


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    known = {p.parent.name for p in CLAUDE_DIR.glob("*/SKILL.md")}
    known |= {p.parent.name for p in HERMES_DIR.glob("*/*/SKILL.md")}
    wanted = expected_files(known)

    # Files already in the mirrored folders that no longer have a source.
    stale = [
        path
        for name, config in MIRRORS.items()
        for path in (HERMES_DIR / config["category"] / name).rglob("*")
        if path.is_file() and path not in wanted
    ]
    changed = [p for p, data in wanted.items() if not p.exists() or p.read_bytes() != data]

    if check_only:
        for path in changed:
            print(f"out of date: {path.relative_to(ROOT).as_posix()}")
        for path in stale:
            print(f"no longer in source: {path.relative_to(ROOT).as_posix()}")
        if changed or stale:
            print("\nHermes copies have drifted. Run: python3 scripts/sync_hermes_skills.py")
            return 1
        print(f"Hermes copies are in sync ({len(MIRRORS)} skills).")
        return 0

    for path in stale:
        path.unlink()
    for path in changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(wanted[path])
        print(f"wrote {path.relative_to(ROOT).as_posix()}")
    if not changed and not stale:
        print("Nothing to do; Hermes copies are already in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
