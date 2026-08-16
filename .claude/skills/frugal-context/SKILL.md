---
name: frugal-context
description: Read and search the codebase economically — grep before reading, read slices instead of whole files, never re-read what is already in context. Use when the user invokes /frugal-context, asks to save tokens, or at the start of any autonomous task that involves exploring an unfamiliar or large codebase.
---

# Frugal Context

Every file you read is paid for again on every subsequent model call in the
session. Exploration discipline early in a task compounds into a much longer
usable session later — which matters most in autonomous mode, where nobody is
around to restart you when context runs out.

## Search funnel: cheap to expensive

Work down this ladder and stop at the first rung that answers the question:

1. **Glob / file search** — does the file/module exist, and where?
   - Glob: `**/auth*`, `src/**/*.test.ts`, `*_test.go`
   - `find . -name '*auth*' -type f`
   - `tree --dirsfirst -L 2` for layout overview

2. **Grep, files-only** — which files mention the symbol?
   - `rg -l 'symbol_name'` or `grep -rl`
   - Filter by language: `rg -l 'symbol' --type py`
   - Scope to directory: `rg -l 'fn' src/api/`

3. **Grep, content with small context** — what does the usage look like?
   - `rg 'fn_name' -C 2` for 2 lines of context
   - `rg 'fn_name' -A 5 -m 5` for 5 lines after, max 5 matches
   - `rg '\berror\b' --count` for per-file match counts

4. **Read a slice** — the specific function or section using line numbers
   from grep. Read ~50 lines around the match, not the whole file.

5. **Read the whole file** — only for small files (< ~200 lines) or when the
   task is genuinely about the file as a whole (schema, migration, config).

## Rules

- **Grep gives you line numbers — use them.** Reading a 1,500-line file to
  find one function at line 812 wastes ~1,300 lines of context. Read lines
  800–860 instead.

- **Never re-read what you already have.** A file you read or edited earlier
  is still in context. After an edit, the tool's output confirms what changed
  — don't re-read the file.

- **Don't spider the codebase.** Follow imports only when the current task
  requires understanding them. "Might be relevant" is not a reason to read
  a file; "the fix touches it" is.

- **Batch independent lookups.** When you need to check several files, read
  them all in parallel rather than sequential "oh I need this too" rounds.

- **Summarize instead of quoting.** When reporting findings, cite
  `path/to/file.ts:123` and describe the behavior in a sentence; don't paste
  code blocks unless the user needs the exact code.

- **Docs and configs count too.** Read the relevant section of a README or
  the one key in a large JSON config (grep for the key first), not the whole
  document. For manifests (`package.json`, `pyproject.toml`, etc.), read
  once and memoize.

- **Use AST-aware tools when available.** `pygount` for LOC stats, tree-sitter
  for structural navigation — these give more signal per byte than raw reads.

## Patterns for common scenarios

**Finding function definitions across languages:**
```bash
# Python
rg '(def|class)\s+fn_name'

# JavaScript/TypeScript
rg '(function|const|let)\s+fn_name|fn_name\s*[=:]'

# Rust
rg '^\s*(pub\s+)?(fn|struct|impl|trait)\s+\w+'

# Go
rg '^\s*func\s+\(?\w*\)?\s+\w+' -n src/
```

**Finding environment/config dependencies:**
```bash
# Environment variables
rg '\benv\b|os\.environ|process\.env|getenv' -l

# Config file references
rg 'config\.|settings\.|\.yaml|\.toml|\.env' -l
```

**Quick test coverage estimate:**
```bash
rg '' -l --glob '*_test.py' --glob '*.test.ts' | wc -l  # test files
rg '' -L --glob '*_test*' --type py | wc -l              # source files
```

**Understanding project entry points:**
```bash
# Find main/app/start files
git ls-files | grep -E '(main|app|index|cli)\.[a-z]+$|__main__\.py$'
```

**Finding TODOs and known issues:**
```bash
rg 'TODO|FIXME|HACK|XXX' -C 1
```

## When breadth is genuinely needed

If the task really does require sweeping many files (a rename, an audit, a
"where is X used everywhere" question), keep the sweep out of your own
context: use grep counts and file lists to plan, then visit files one at a
time only as you change them. For pure research sweeps where only the
conclusion matters, delegate to a subagent to keep hundreds of file
excerpts out of the main session — but only reach for it when the sweep is
large enough that its cold-start cost is cheaper than the reading it absorbs.

## Exception

If you find yourself guessing about code you chose not to read, stop and
read it. Frugality applies to *how* you look things up, never to *whether*
you verify what your change depends on.

## Combining with other skills

- **lean-output**: cap grep results so search itself doesn't bloat context.
- **repo-map**: read the map file first to jump to the right directory
  instead of searching blindly.
- **checkpoint**: memoize file:line references you discover so you don't
  have to search for them again after context compaction.
