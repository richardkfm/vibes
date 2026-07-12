---
name: lean-output
description: Keep tool output small - every byte a command prints lands in the context window and costs tokens. Use quiet flags, cap long output, and route verbose logs to files that get grepped instead of dumped. Use when the user invokes /lean-output, asks to save tokens, or at the start of any long autonomous run involving builds, tests, or package installs.
---

# Lean Output

Tool results are the biggest hidden token cost in a session: a single verbose
test run or `npm install` can eat more context than an hour of conversation.
Treat every command's stdout/stderr as something you are paying for.

## Core rules

1. **Prefer quiet flags.** Reach for the low-noise form of a command first:
   - `pytest -q` (add `-x` to stop on first failure), not bare `pytest`
   - `npm test -- --silent`, `npm install --no-audit --no-fund --loglevel=error`
   - `pip install -q`, `cargo build -q`, `mvn -q`, `gradle -q`
   - `git log --oneline -20`, `git diff --stat` before a full `git diff`
   - `make 2>&1 | tail -30` when there is no quiet mode

2. **Cap anything that can scroll.** If output size is unpredictable, bound it:
   append `| tail -50` (failures usually print last) or `| head -50`
   (listings usually matter first). Never run an uncapped command twice in a
   row hoping for different output.

3. **Big logs go to a file, not the context.** For builds, test suites, and
   servers, redirect to the scratchpad and inspect selectively:

   ```bash
   npm run build > "$SCRATCH/build.log" 2>&1; echo "exit=$?"
   grep -n -i -m 20 'error\|fail' "$SCRATCH/build.log"
   ```

   Pull only the matching lines (plus `-A 3` context if needed) into the
   conversation. The log file stays available if deeper digging is needed —
   re-grep it rather than re-running the build.

4. **Ask for the verdict, not the transcript.** When you only need
   pass/fail or a count, request exactly that: `... > /dev/null 2>&1; echo $?`,
   `grep -c`, `wc -l`, `--dry-run` summaries.

5. **One diagnostic pass, not a firehose.** When debugging, form a hypothesis
   and run the narrow command that tests it, instead of dumping full state
   (`env`, `cat` of whole configs, entire stack traces) "just in case".

## What NOT to do

- Do not `cat` a file to "show" it when nothing needs showing.
- Do not re-run a failing suite in verbose mode when the quiet failure
  message already names the broken test — run just that test.
- Do not paste long output back to the user; summarize the finding and cite
  the file/line.

## Exception

Correctness beats thrift: if capped output hides the actual error, widen the
window (bigger `tail`, targeted `grep -B/-A`) until you can see it. Saving
tokens on a wrong answer saves nothing.
