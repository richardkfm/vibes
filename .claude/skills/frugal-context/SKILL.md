---
name: frugal-context
description: Reads and searches a codebase economically so exploration does not eat the context window. Greps before reading, reads slices instead of whole files, and never re-reads what is already in context. Use when the user invokes /frugal-context, asks to save tokens or context, says sessions run out of context too fast, or at the start of any autonomous task that involves exploring an unfamiliar or large codebase, including monorepos and repos with very long files.
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
   - `git ls-files | cut -d/ -f1-2 | sort -u | head -40` for layout overview

2. **Grep, files-only** — which files mention the symbol?
   - `rg -l 'symbol_name' .` or `grep -rl`
   - Filter by language: `rg -l 'symbol' --type py .`
   - Scope to directory: `rg -l 'fn' src/api/`

3. **Grep, content with small context** — what does the usage look like?
   - `rg 'fn_name' -C 2 src/` for 2 lines of context
   - `rg 'fn_name' -A 5 -m 5 src/` for 5 lines after, max 5 matches per file
   - `rg '\berror\b' --count .` for per-file match counts

4. **Read a slice** — the specific function or section using line numbers
   from grep. Read ~50 lines around the match, not the whole file.

5. **Read the whole file** — only for small files (< ~200 lines) or when the
   task is genuinely about the file as a whole (schema, migration, config).

Always give `rg` a path (`.` or a directory). With none, it searches stdin
whenever stdin is a pipe or socket, which is how many agent harnesses run
shell commands, and the call hangs until it times out.

## Rules

- **Grep gives you line numbers — use them.** Reading a 1,500-line file to
  find one function at line 812 wastes ~1,300 lines of context. Read lines
  800–860 instead.

- **Never re-read what you already have.** A file you read or edited earlier
  is still in context until a compaction drops it. After an edit, the tool's
  output confirms what changed — don't re-read the file.

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

- **Use structure-aware tools when available.** Go-to-definition or symbol
  search from a language server, `ctags`, or tree-sitter give more signal
  per byte than raw reads: one definition instead of twenty grep hits.

## Patterns for common scenarios

**Finding function definitions across languages:**
```bash
# Python
rg -n '(def|class)\s+fn_name\b' --type py .

# JavaScript/TypeScript
rg -n '(function|const|let)\s+fn_name\b|fn_name\s*[=:]' --type ts --type js .

# Rust
rg -n '^\s*(pub(\([a-z]+\))?\s+)?(async\s+)?(fn|struct|enum|trait)\s+fn_name\b' --type rust .

# Go (functions and methods)
rg -n '^func\s+(\([^)]*\)\s+)?fn_name\b' --type go .
```

**Finding environment/config dependencies:**
```bash
# Environment variables
rg -l '\benv\b|os\.environ|process\.env|getenv' .

# Config file references
rg -l 'config\.|settings\.|\.yaml|\.toml|\.env' .
```

**Quick test coverage estimate:**
```bash
rg --files -g '*_test.py' -g 'test_*.py' -g '*.test.ts' . | wc -l    # test files
rg --files --type py -g '!*_test.py' -g '!test_*.py' . | wc -l       # Python source files
```

**Understanding project entry points:**
```bash
# Find main/app/start files
git ls-files | grep -E '(^|/)(main|app|index|cli|__main__)\.[a-z]+$' | head -30
```

**Finding TODOs and known issues:**
```bash
rg -n 'TODO|FIXME|HACK|XXX' src/ | head -30
```

## When breadth is genuinely needed

If the task really does require sweeping many files (a rename, an audit, a
"where is X used everywhere" question), keep the sweep out of your own
context: use grep counts and file lists to plan, then visit files one at a
time only as you change them. For pure research sweeps where only the
conclusion matters, delegate to a subagent (where the harness has them) to
keep hundreds of file excerpts out of the main session — but only reach for
it when the sweep is large enough that its cold-start cost is cheaper than
the reading it absorbs.

## Exception

If you find yourself guessing about code you chose not to read, stop and
read it. Frugality applies to *how* you look things up, never to *whether*
you verify what your change depends on.

## Related skills

- `lean-output`: the same thrift for command output. Cap grep results so
  search itself doesn't bloat context.
- `repo-map`: if the repo has a `.repo-map.md`, read it first to jump to
  the right directory instead of searching blindly.
- `checkpoint`: memoize file:line references you discover so you don't
  have to search for them again after context compaction.
