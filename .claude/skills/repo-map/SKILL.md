---
name: repo-map
description: Build and maintain a compact cached map of the repository - an annotated tree with module one-liners, entry points, and conventions - so navigating a big codebase costs one small read instead of a fresh exploration every session. Use when the user invokes /repo-map, asks for a visualization or overview of the repo structure, or at the start of work in a large unfamiliar repository.
---

# Repo Map

In a big repository, every session pays the same exploration tax: listing
directories, opening READMEs, grepping to figure out where things live.
A repo map converts that repeated cost into a one-time cost — a single
~100-line file, read once per session, that answers "where would X be?"
without touching the tree.

## Using an existing map

Before exploring any repository, check for `.claude/repo-map.md`. If it
exists, read it FIRST and treat it as the primary index: navigate straight
to the directories/files it names instead of running discovery listings and
greps. Fall back to live exploration only for areas the map doesn't cover —
and add what you learn to the map afterwards.

Trust but verify freshness: the map header records the commit it was built
at. If `git log --oneline <that-commit>..HEAD -- <dir> | head -5` shows
heavy churn in the area you care about, re-check that area live.

## Building the map

Generate the skeleton cheaply from git metadata, not by reading files:

```bash
# directory shape with file counts (no file-content reads)
git ls-files | cut -d/ -f1-2 | sort | uniq -c | sort -rn | head -40
# likely entry points and manifests
git ls-files | grep -E '(^|/)(main|index|app|cli)\.[a-z]+$|package.json$|pyproject.toml$|Cargo.toml$|go.mod$' | head
```

Then read ONLY the manifests and any top-level README to annotate. Write
`.claude/repo-map.md` (~100 lines max, hard cap 150):

```markdown
# Repo map — built at <short-sha>, <date>

## What this is
One paragraph: what the project does, main language(s), how it's run/tested.

## Layout
- `src/api/` (61 files) — HTTP layer; routes in `routes/`, one file per resource
- `src/core/` (114 files) — domain logic; start at `core/engine.ts`
- `src/db/` — migrations + query builders; schema source of truth: `db/schema.sql`
- `web/` — React frontend, talks only to `src/api`
- `tools/` — one-off scripts, safe to ignore for product work

## Entry points
- server: `src/main.ts` → `core/engine.ts`
- CLI: `src/cli.ts`
- tests: `pytest -q` from repo root; e2e in `web/e2e/` needs the server up

## Conventions & gotchas
- errors: always via `core/errors.ts` helpers, never raw throw
- `src/legacy/` is frozen — do not extend, only bugfix
```

Annotate with *navigation* facts (what lives where, where to start reading),
not implementation detail. If a one-liner needs three sentences, it's too
deep for the map.

## Maintaining it

- When work reveals the map is wrong or silently missing an area you needed,
  fix that line while the knowledge is fresh — a map that lies is worse
  than no map.
- Commit the map with whatever change prompted the update; update the
  header sha. Don't rebuild wholesale unless the structure really shifted.
- Never let it grow into documentation. It's an index; prune as you add.

## Visual mode (for the user, on request)

The markdown map is for agent navigation. If the user asks to *see* the
structure, additionally render a visual from the same data — a Mermaid
diagram of the top-level modules and their dependencies, or an HTML treemap
sized by file count (load the `dataviz` skill first if building a chart).
Send it as a file or artifact; don't paste large diagrams into chat.

## Exception

The map is a hint, not ground truth. Any change you make still gets
verified against the real code — if the map and the code disagree, the code
wins and the map gets corrected.
