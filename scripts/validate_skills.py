#!/usr/bin/env python3
"""Validate every skill in this repo.

Checks the Agent Skills spec (https://agentskills.io/specification) plus this
repo's own rules: portable frontmatter, working links, no orphaned reference
files, cross-links that point at real skills, and a README that lists every
skill.

Usage:  python3 scripts/validate_skills.py
Needs:  PyYAML
Exit 1 if any check fails.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_DIR = ROOT / ".claude" / "skills"
HERMES_DIR = ROOT / ".hermes" / "skills"
README = ROOT / "README.md"

# The spec's fields. Skills in .claude/skills are also uploaded to claude.ai,
# which rejects any other key, so nothing harness-specific is allowed there.
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# Hermes reads the same fields plus a few of its own.
HERMES_KEYS = SPEC_KEYS | {"version", "author", "platforms", "prerequisites"}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_WORDS = ("claude", "anthropic")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
MAX_LINES = 500

FENCE_RE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?[^)]*\)")
HTML_SRC_RE = re.compile(r"""\b(?:src|href|srcset)=["']([^"']+)["']""")
RELATED_RE = re.compile(r"^#{2,}\s*Related skills\s*$(.*?)(?=^#{1,6}\s|\Z)", re.M | re.S | re.I)

errors: list[tuple[Path, str]] = []


def fail(path: Path, message: str) -> None:
    errors.append((path, message))


def split_frontmatter(path: Path) -> tuple[dict | None, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(path, "file must start with a '---' frontmatter block")
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        fail(path, "frontmatter block is never closed with '---'")
        return None, text
    try:
        meta = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        fail(path, f"frontmatter is not valid YAML: {exc}")
        return None, text
    if not isinstance(meta, dict):
        fail(path, "frontmatter must be a YAML mapping")
        return None, text
    body = text[end + 4 :].lstrip("\n")
    return meta, body


def prose(text: str) -> str:
    """Text with code removed, so sample links inside examples are not checked."""
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def local_targets(text: str) -> list[str]:
    targets = MD_LINK_RE.findall(prose(text)) + HTML_SRC_RE.findall(prose(text))
    return [
        t.split("#", 1)[0]
        for t in targets
        if not re.match(r"^[a-z][a-z0-9+.-]*:", t, re.I) and not t.startswith("#")
    ]


def check_links(path: Path, text: str) -> None:
    for target in local_targets(text):
        if target and not (path.parent / target).exists():
            fail(path, f"link target does not exist: {target}")


def check_frontmatter(path: Path, meta: dict, allowed: set[str]) -> None:
    extra = sorted(set(meta) - allowed)
    if extra:
        fail(path, f"frontmatter keys not allowed here: {', '.join(extra)}")

    name = meta.get("name")
    folder = path.parent.name
    if not isinstance(name, str) or not name:
        fail(path, "frontmatter needs a 'name'")
    else:
        if not NAME_RE.match(name):
            fail(path, f"name '{name}' must be lowercase letters, digits and single hyphens")
        if len(name) > MAX_NAME:
            fail(path, f"name is {len(name)} characters; the limit is {MAX_NAME}")
        if name != folder:
            fail(path, f"name '{name}' must match its folder '{folder}'")
        for word in RESERVED_WORDS:
            if word in name:
                fail(path, f"name must not contain the reserved word '{word}'")

    description = meta.get("description")
    if not isinstance(description, str) or not description.strip():
        fail(path, "frontmatter needs a non-empty 'description'")
    else:
        if len(description) > MAX_DESCRIPTION:
            fail(path, f"description is {len(description)} characters; the limit is {MAX_DESCRIPTION}")
        if "<" in description or ">" in description:
            fail(path, "description must not contain angle brackets")

    compatibility = meta.get("compatibility")
    if compatibility is not None and (
        not isinstance(compatibility, str) or not 0 < len(compatibility) <= MAX_COMPATIBILITY
    ):
        fail(path, f"compatibility must be a string of 1-{MAX_COMPATIBILITY} characters")

    if "metadata" in meta and not isinstance(meta["metadata"], dict):
        fail(path, "metadata must be a mapping")


def check_skill(path: Path, allowed: set[str], known: set[str], strict: bool) -> None:
    meta, body = split_frontmatter(path)
    if meta is None:
        return
    check_frontmatter(path, meta, allowed)

    text = path.read_text(encoding="utf-8")
    lines = text.count("\n") + 1
    if lines > MAX_LINES:
        fail(path, f"SKILL.md is {lines} lines; the limit is {MAX_LINES}. Move detail into references/")
    if not body.strip():
        fail(path, "SKILL.md has no instructions after the frontmatter")
    check_links(path, body)

    if not strict:
        return

    # Spec metadata is a flat string-to-string map.
    for key, value in (meta.get("metadata") or {}).items():
        if not isinstance(value, str):
            fail(path, f"metadata.{key} must be a string")

    # Every bundled file must be mentioned in SKILL.md, or nothing will ever load it.
    for extra_file in sorted(p for p in path.parent.rglob("*") if p.is_file() and p != path):
        rel = extra_file.relative_to(path.parent).as_posix()
        if rel not in text:
            fail(path, f"bundled file is never referenced from SKILL.md: {rel}")
        elif extra_file.suffix == ".md":
            check_links(extra_file, extra_file.read_text(encoding="utf-8"))

    # Cross-links in "Related skills" must point at skills that exist.
    for section in RELATED_RE.findall(body):
        for token in re.findall(r"`([^`\n]+)`", section):
            if NAME_RE.match(token) and "-" in token and token not in known:
                fail(path, f"'Related skills' names a skill that does not exist: {token}")


def check_readme(skill_files: list[Path]) -> None:
    if not README.exists():
        fail(README, "README.md is missing")
        return
    text = README.read_text(encoding="utf-8")
    check_links(README, text)
    for skill_file in skill_files:
        rel = skill_file.relative_to(ROOT).as_posix()
        if rel not in text:
            fail(README, f"README does not link to {rel}")


def main() -> int:
    claude_skills = sorted(CLAUDE_DIR.glob("*/SKILL.md"))
    hermes_skills = sorted(HERMES_DIR.glob("*/*/SKILL.md"))
    known = {p.parent.name for p in claude_skills + hermes_skills}

    for folder in sorted(p for p in CLAUDE_DIR.iterdir() if p.is_dir()):
        if not (folder / "SKILL.md").exists():
            fail(folder, "skill folder has no SKILL.md")
    for category in sorted(p for p in HERMES_DIR.iterdir() if p.is_dir()):
        if not (category / "DESCRIPTION.md").exists():
            fail(category, "Hermes category folder has no DESCRIPTION.md")

    for path in claude_skills:
        check_skill(path, SPEC_KEYS, known, strict=True)
    for path in hermes_skills:
        check_skill(path, HERMES_KEYS, known, strict=False)
    check_readme(claude_skills + hermes_skills)

    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    for path, message in errors:
        rel = path.relative_to(ROOT).as_posix()
        print(f"{rel}: {message}")
        if in_actions:
            print(f"::error file={rel}::{message}")

    total = len(claude_skills) + len(hermes_skills)
    if errors:
        print(f"\n{len(errors)} problem(s) in {total} skills.")
        return 1
    print(f"{total} skills OK ({len(claude_skills)} in .claude/skills, {len(hermes_skills)} in .hermes/skills).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
