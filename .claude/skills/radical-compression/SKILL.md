---
name: radical-compression
description: Radically compress working state after each completed cycle of work — distill what the cycle proved into a few lines, discard everything else, and carry only the compressed residue forward. Use when the user invokes /radical-compression, asks to keep the session tight, or at the start of long multi-cycle tasks (debug loops, migrations, PR babysitting) that would otherwise bloat the context window.
---

# Radical Compression

A long session is a sequence of cycles: explore → change → verify, fix →
test → repeat, push → CI → respond. Each cycle generates far more context
than it's worth keeping — file reads, failed attempts, log dumps, dead
ends. Left alone, that residue accumulates until compaction hits and
squashes it indiscriminately. Compressing *yourself*, at the end of every
cycle, keeps the session tight on your own terms: you choose what
survives, and it's a few lines instead of a few thousand.

## The cycle boundary

A cycle ends when a unit of work reaches a verdict: a test run finishes, a
hypothesis is confirmed or killed, a plan step completes, a CI round comes
back, a review comment is resolved. At every such boundary, stop and
compress before starting the next cycle.

## The compression ritual

At each boundary, distill the entire cycle into at most 3–5 lines:

1. **Verdict** — what the cycle established, in one sentence.
   ("Root cause: stale cache key in `src/cache.ts:41`, confirmed by test.")
2. **Residue worth keeping** — only facts that were expensive to earn:
   the command incantation that finally worked, the `file:line` of the
   proof, the gotcha that cost you two attempts.
3. **Next** — the one thing the next cycle does.

Write it into your running state file if you keep one (see `checkpoint`),
*replacing* the previous cycle's working notes rather than appending to
them. Everything else from the cycle — the paths not taken, the logs, the
intermediate diffs, the three wrong hypotheses — is deliberately dropped.
If it mattered, it's in the verdict; if it's not in the verdict, stop
referring back to it.

## Rules

- **Compress at every boundary, not just when the session feels long.**
  The point of compressing cycle N is that cycles N+1..N+20 each re-pay
  for whatever you keep. By the time the session feels heavy, the debt is
  already booked.

- **Replace, don't append.** A state file that grows one section per cycle
  is a journal, not a compression. Overwrite the working-notes section
  each cycle; only durable facts (commands, decisions, `file:line` proofs)
  accumulate — and prune even those when they stop being load-bearing.

- **Dead ends compress to one line or zero.** "Not the config loader —
  ruled out" is worth keeping only if you're otherwise likely to re-check
  it. The full story of *how* it was ruled out never survives the boundary.

- **Never carry raw output across a boundary.** Test logs, stack traces,
  and command output are inputs to the cycle's verdict, not things to
  keep. If a trace matters later, note the file it's saved in and grep it
  then (see `lean-output`).

- **Trust the compression.** After compressing, work from the distilled
  lines — don't scroll back to re-derive confidence from the raw history.
  If the compressed version turns out to be missing something, that's a
  fact-finding step in the new cycle, not a reason to stop compressing.

- **The final summary is the last compression.** When the task completes,
  the accumulated verdicts *are* the report: what was done, what was
  decided, how it was verified. No end-of-task re-reading required.

## Compression examples

**Before (raw context after a debugging cycle):**
```
- Read src/auth/login.ts (180 lines)
- Read src/auth/middleware.ts (95 lines)
- Grep for "token" found 14 matches across 6 files
- Ran pytest tests/test_auth.py - 3 passed, 1 failed: test_refresh_token
- Error: "TokenExpiredError at src/auth/refresh.py:23"
- Read src/auth/refresh.py lines 1-50
- Added debug print, ran again — token was expired because clock skew > tolerance
- The tolerance was 30s; prod clock is 45s behind
```

**After compression:**
```
Verdict: test_refresh_token fails because clock tolerance (30s) < skew (45s)
Proof: src/auth/refresh.py:23 raises TokenExpiredError; prod time skew confirmed
Next: increase tolerance to 60s or add NTP sync check
```

**Multi-hypothesis cycle compressed to one line:**
```
Ruled out: network (ping passes), disk (df ok), DB (healthcheck OK) → issue is in app-level connection pool
```

## Why this saves tokens

Harness compaction is lossy, generic, and arrives at the worst time —
mid-task, squashing proof and noise alike. Per-cycle self-compression is
the opposite: lossless where it counts (you pick what survives while it's
fresh) and radical everywhere else. Twenty cycles at five lines each is a
hundred lines of perfect recall; twenty uncompressed cycles is a full
context window and a lossy squash you don't control.

## Combining with other skills

- **checkpoint**: the state file is where you store compressed cycles.
  Checkpoint gives the file structure; compression fills it with distilled
  content.
- **lean-output**: compressed cycles reference log files by path, so
  lean-output's file-redirect patterns and grep strategies pair naturally.
- **silent-mode**: compress silently — the compression is internal housekeeping,
  not user-facing narration.
