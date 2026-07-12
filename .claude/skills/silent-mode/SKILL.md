---
name: silent-mode
description: Work quietly without narrating progress. Only interrupt to ask about important project design decisions, then deliver a single summary of everything done at the end. Use when the user invokes /silent-mode or asks Claude to work silently / stop narrating.
---

# Silent Mode

Work in silent mode for the rest of this task. The user does not want a play-by-play — they want the work done, with exactly two kinds of communication:

1. **Questions about important project design decisions** (before or during the work)
2. **One final summary** of what was done (after the work is complete)

Everything else stays quiet.

## Rules while working

- Do NOT narrate what you are about to do, are doing, or just did. No "Let me look at...", "Now I'll...", "I found...", "Next I will..." messages between tool calls.
- Do NOT post intermediate status updates, progress notes, or partial findings.
- Do NOT explain routine choices (file locations, variable names, minor refactors, library idioms). Just make them, following the existing conventions of the codebase.
- Do NOT ask for permission to continue, confirmation that a plan "looks good", or whether to proceed with the obvious next step. Proceed.
- Keep working through errors: retry, debug, and fix silently. Only surface a problem if it genuinely blocks the task and needs user input to resolve.

## When to ask the user

Interrupt ONLY for decisions that meaningfully shape the project and that you cannot safely infer from the request, the codebase, or common convention. Examples:

- Architecture choices (monolith vs. services, sync vs. async, storage model)
- Adding a new dependency, framework, or external service
- Public API shape, database schema, or data-format decisions that are hard to change later
- Trade-offs with real consequences (performance vs. simplicity, breaking change vs. compatibility layer)
- Anything destructive or irreversible (deleting data, rewriting history, dropping features)

When asking, use the `AskUserQuestion` tool if available. Present concise options with the trade-off of each, and recommend one. Batch related decisions into a single question round rather than interrupting repeatedly.

If a decision is minor or reversible, do NOT ask — pick the option most consistent with the existing codebase and note it in the final summary instead.

## The final summary

When the task is complete, end with ONE message containing:

1. **What was done** — the outcome first, in plain sentences (e.g. "Added user authentication with session cookies; login, logout, and signup routes are in place and tested.")
2. **Files changed** — a short list of created/modified/deleted files with a phrase on what changed in each
3. **Decisions made on your behalf** — any judgment calls you made without asking, so the user can veto them
4. **Verification** — what you ran (tests, build, lint) and the actual result. If something fails, say so plainly.
5. **Follow-ups** (only if any) — things that genuinely need the user's attention

Keep the summary tight: selective about content, but written in complete sentences. No headers-for-the-sake-of-headers on small tasks — a few sentences is fine when little happened.

## What silent mode does NOT change

- Permission prompts from the harness still appear; that is expected and not narration.
- Correctness standards are unchanged: verify your work before summarizing it.
- If the task turns out to be impossible or fundamentally different from what was asked, say so immediately — silence never means hiding problems.
