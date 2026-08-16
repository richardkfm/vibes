---
name: repo-map
description: Build and maintain a compact cached map of the repository — an annotated tree with module one-liners, entry points, and conventions — so navigating a big codebase costs one small read instead of a fresh exploration every session. Use when the user invokes /repo-map, asks for a visualization or overview of the repo structure, or at the start of work in a large unfamiliar repository.
---

# Repo Map

In a big repository, every session pays the same exploration tax: listing
directories, opening READMEs, grepping to figure out where things live.
A repo map converts that repeated cost into a one-time cost — a single
~100-line file, read once per session, that answers "where would X be?"
without touching the tree.

## Using an existing map

Before exploring any repository, check for `.repo-map.md` at the repo root.
If it exists, read it FIRST and treat it as the primary index: navigate
straight to the directories/files it names instead of running discovery
listings and greps. Fall back to live exploration only for areas the map
doesn't cover — and add what you learn to the map afterwards.

Trust but verify freshness: the map header records the commit it was built
at. If `git log --oneline <that-sha>..HEAD -- <dir> | head -5` shows
heavy churn in the area you care about, re-check that area live.

## Building the map

Generate the skeleton cheaply from git metadata, not by reading files:

```bash
# Directory shape with file counts (no content reads)
git ls-files | cut -d/ -f1-2 | sort | uniq -c | sort -rn | head -40

# Likely entry points and manifests
git ls-files | grep -E '(main|index|app|cli)\.[a-z]+$|package\.json$|pyproject\.toml$|Cargo\.toml$|go\.mod$'

# File count by extension
git ls-files | grep -oE '\.[a-z]+$' | sort | uniq -c | sort -rn
```

Then read ONLY the manifests and any top-level README to annotate. Write
`.repo-map.md` (~100 lines max, hard cap 150):

```markdown
# Repo map — built at a3f8d2c, 2026-08-16

## What this is
Python API service for user management. FastAPI, SQLAlchemy, Postgres.
Run with `uvicorn app.main:app`, tests with `pytest -q`.

## Layout
- `app/api/` (42 files) — HTTP layer; routes in `routes/`, one file per resource
- `app/core/` (28 files) — domain logic; start at `core/engine.py`
- `app/db/` (15 files) — migrations + query builders; schema: `db/schema.sql`
- `web/` (83 files) — React frontend, talks only to `app/api`
- `tools/` (7 files) — one-off scripts, safe to ignore for product work

## Entry points
- server: `app/main.py` → `core/engine.py`
- CLI: `tools/cli.py`
- tests: `pytest -q` from repo root; e2e in `web/e2e/` needs server running
- Docker: `docker-compose up` spins up API + DB + Redis

## Conventions & gotchas
- errors: always via `core/errors.py` helpers, never raw raise
- `app/legacy/` is frozen — do not extend, only bugfix
- DB migrations must be backwards-compatible (zero-downtime deploys)
- Config loaded from `.env.development` (gitignored) or env vars
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

## Map variations by project type

**Monorepo:**
```markdown
## Workspaces
- packages/auth/ — shared auth middleware (npm, used by apps/*)
- packages/ui/ — component library (Storybook storybook in /stories)
- apps/web/ — customer-facing SPA (Next.js)
- apps/admin/ — internal dashboard (Next.js, same UI pkg)
```

**Backend microservice:**
```markdown
## Service layout
- cmd/api/ — main binary, server startup
- internal/handlers/ — HTTP handlers, one per route
- internal/domain/ — business logic, tests co-located
- pkg/ — shared utilities (importable by other services)
- proto/ — gRPC protobuf definitions
- docker/ — container config
```

**Data/ML project:**
```markdown
## Structure
- src/etl/ — data ingestion pipelines (scheduled via Airflow in dags/)
- src/models/ — training scripts; artifacts in models/ (gitignored)
- notebooks/ — exploratory analysis
- tests/ — pytest; integration tests need db running
```

## Visual mode (for the user, on request)

The markdown map is for agent navigation. If the user asks to *see* the
structure, additionally render a visual from the same data — a Mermaid
diagram of the top-level modules and their dependencies, or an ASCII tree
sized by file count. Send it as a file or artifact; don't paste large
diagrams into chat.

## Exception

The map is a hint, not ground truth. Any change you make still gets
verified against the real code — if the map and the code disagree, the code
wins and the map gets corrected.

## Combining with other skills

- **frugal-context**: use the map to jump to the right directory before
  searching within it — skip the "find the directory" step entirely.
- **checkpoint**: store the map path and sha in your state file so you can
  verify freshness without reading the map every cycle.
- **lean-output**: build the map using git metadata (file paths only),
  never the verbose content of the files it references.
