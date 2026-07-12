---
name: checkpoint
description: Maintain a compact running state file during long autonomous tasks so context compaction stays cheap and nothing is lost when the window fills up. Use when the user invokes /checkpoint, kicks off a long unattended/auto-mode run, or asks Claude to make long sessions survive context limits.
---

# Checkpoint

Long autonomous runs outlive their context window. When the conversation is
compacted, everything not written down must be re-derived by re-reading
files and re-running commands — the most expensive tokens in the whole
session. A small, disciplined state file makes compaction nearly free.

## The state file

At the start of a long task, create `NOTES.claude.md` in the scratchpad
directory (never commit it). Keep it under ~60 lines, overwriting stale
content rather than appending a journal. Structure:

```markdown
# Task
One sentence: what "done" looks like.

# Plan
- [x] step that is finished
- [ ] step in progress  <- CURRENT
- [ ] remaining step

# Key facts (expensive to re-derive)
- build: `npm run build`, output in dist/; tests: `pytest -q tests/api`
- the flaky test is tests/test_sync.py::test_retry - ignore its first failure
- config precedence: env var > .rc file > defaults (checked src/config.ts:88)

# Decisions made
- chose cursor pagination over offset (matches existing /users endpoint)

# Files touched
- src/api/pagination.ts (new), src/api/users.ts (uses it)
```

## Rules

- **Update at boundaries, not continuously.** Refresh the file when a plan
  step completes, a surprising fact is discovered, or a decision is made —
  not after every tool call.
- **Record only what is expensive to re-derive.** Command incantations that
  took trial and error, non-obvious behavior verified from source (with
  `file:line`), gotchas, decisions and their reasons. Never paste code or
  logs into it — cite paths instead.
- **Keep it current-state, not history.** Delete finished sub-plans and
  facts that no longer matter. The file answers "where am I and what do I
  know", not "what happened".
- **After a compaction or fresh wake-up, read the state file first** —
  before re-reading any source files. It should be sufficient to resume
  without re-exploring.
- **On task completion, fold it into the final summary** (what was done,
  decisions, verification) and delete the file. It is scaffolding, not a
  deliverable.

## Why this saves tokens

Compaction summaries are lossy and generic; re-exploration after them is
the single biggest token sink in long sessions. Sixty curated lines read
once per resume replace thousands of lines of re-read source — and double
as the skeleton of the final summary the user gets.
