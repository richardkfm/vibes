---
name: frugal-context
description: Read and search the codebase economically - grep before reading, read slices instead of whole files, never re-read what is already in context. Use when the user invokes /frugal-context, asks to save tokens, or at the start of any autonomous task that involves exploring an unfamiliar or large codebase.
---

# Frugal Context

Every file you read is paid for again on every subsequent model call in the
session. Exploration discipline early in a task compounds into a much longer
usable session later — which matters most in auto mode, where nobody is
around to restart you when context runs out.

## Search funnel: cheap to expensive

Work down this ladder and stop at the first rung that answers the question:

1. **Glob** — does the file/module exist, and where? (`**/auth*`, `src/**/*.test.ts`)
2. **Grep, files-only** — which files mention the symbol? (`output_mode: files_with_matches`)
3. **Grep, content with small context** — what does the usage look like?
   (`output_mode: content`, `-C 2`, always set a `head_limit` like 20–30)
4. **Read a slice** — the specific function or section, using `offset`/`limit`
   around the line numbers grep just gave you.
5. **Read the whole file** — only for small files (< ~200 lines) or when the
   task is genuinely about the file as a whole.

## Rules

- **Grep gives you line numbers — use them.** Reading a 1,500-line file to
  find one function that grep already located at line 812 wastes ~1,300
  lines of context. `Read` with `offset: 800, limit: 60` instead.
- **Never re-read what you already have.** A file you read or edited earlier
  in the session is still in context. After an Edit, do not read the file
  back to check — the edit would have errored if it failed.
- **Don't spider the codebase.** Follow imports only when the current task
  requires understanding them. "Might be relevant" is not a reason to read
  a file; "the fix touches it" is.
- **Batch independent lookups** into one parallel tool block instead of
  ping-ponging one lookup per turn.
- **Summarize instead of quoting.** When reporting findings, cite
  `path/to/file.ts:123` and describe the behavior in a sentence; don't paste
  code blocks unless the user needs to review the exact code.
- **Docs and configs count too.** Read the relevant section of a README or
  the one key in a large JSON config (grep for the key first), not the whole
  document.

## When breadth is genuinely needed

If the task really does require sweeping many files (a rename, an audit, a
"where is X used everywhere" question), keep the sweep out of your own
context: use grep counts and file lists to plan, then visit files one at a
time only as you change them. For pure research sweeps where only the
conclusion matters, an Explore subagent keeps hundreds of file excerpts out
of the main session — but only reach for it when the sweep is large enough
that its cold-start cost is cheaper than the reading it absorbs.

## Exception

If you find yourself guessing about code you chose not to read, stop and
read it. Frugality applies to *how* you look things up, never to *whether*
you verify what your change depends on.
