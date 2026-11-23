---
name: lean-output
description: Keeps command and tool output small, because every byte a command prints lands in the context window and costs tokens. Prefers quiet flags, caps anything that can scroll, and routes verbose logs to a file that is grepped instead of dumped. Use when the user invokes /lean-output, asks to save tokens or context, complains that output is too long or noisy, or at the start of any long autonomous run involving builds, tests, linters, package installs or CI logs. Also use as soon as a command has flooded the context with output.
---

# Lean Output

Tool results are the biggest hidden token cost in a session: a single verbose
test run or `npm install` can eat more context than an hour of conversation.
Treat every command's stdout/stderr as something you are paying for.

## Core rules

1. **Prefer quiet flags.** Reach for the low-noise form of a command first:
   - `pytest -q` (add `-x` to stop on first failure), not bare `pytest`
   - `npm test --silent`, `npm install --no-audit --no-fund --loglevel=error`
   - `pip install --quiet`, `cargo build --quiet`, `mvn -q`, `gradle -q`
   - `git log --oneline -20`, `git diff --stat` before a full `git diff`
   - `yarn --silent`, `pnpm --silent`
   - When there is no quiet flag: `make 2>&1 | tail -30`

2. **Cap anything that can scroll.** If output size is unpredictable, bound it:
   append `| tail -50` (failures usually print last) or `| head -50`
   (listings usually matter first). Never run an uncapped command twice in a
   row hoping for different output. A pipeline exits with `tail`'s status,
   not the command's, so a failing build piped to `tail` looks green: when
   pass/fail matters, use the log-file form below or `set -o pipefail`.

3. **Big logs go to a file, not the context.** For builds, test suites, and
   servers, redirect to the scratchpad and inspect selectively:

   ```bash
   npm run build > /tmp/build.log 2>&1; echo "exit=$?"
   grep -n -i -m 20 'error\|fail' /tmp/build.log
   grep -n -i -A 3 'error' /tmp/build.log   # add context lines
   ```

   Pull only the matching lines into the conversation. The log file stays
   available if deeper digging is needed — re-grep it rather than re-running
   the build.

4. **Ask for the verdict, not the transcript.** When you only need
   pass/fail or a count, request exactly that:
   - `command > /dev/null 2>&1; echo $?`
   - `grep -c 'pattern' file`
   - `wc -l file` for line counts
   - `--dry-run` summaries for package managers and task runners

5. **One diagnostic pass, not a firehose.** When debugging, form a hypothesis
   and run the narrow command that tests it, instead of dumping full state
   (`env`, `cat` of whole configs, entire stack traces) "just in case".

6. **Use diff output for changes.** When verifying edits, `git diff --stat`
   tells you scope; the full diff shows what changed. Don't re-read the whole
   file to confirm an edit landed.

## Language-specific quiet patterns

```bash
# Python
pytest -q -x --tb=short                    # quiet, stop first fail, short trace
mypy . 2>&1 | tail -30                     # last errors only
ruff check --output-format=concise .       # concise lint output
black --check --diff . 2>&1 | head -20     # formatting diff, capped
pylint --score=n src/ 2>&1 | tail -40      # messages only, no score footer

# JavaScript/TypeScript
tsc --noEmit 2>&1 | tail -20              # compile check, last errors only
eslint --quiet . 2>&1 | tail -20          # errors only, warnings dropped
npx vitest run --reporter=dot             # one dot per test, failures in full
npx jest --silent                         # jest silent mode
npm ci --no-audit --no-fund --loglevel=error  # silent install

# Rust
cargo check --quiet                        # compile check only, quiet
cargo test --quiet 2>&1 | tail -30        # test results, capped
cargo clippy --quiet --no-deps 2>&1 | tail -20  # own crate lints only

# Go
go vet ./... 2>&1 | tail -20              # static analysis
go test ./... -count=1 2>&1 | tail -30    # tests, bypass cache
staticcheck ./... 2>&1 | tail -20        # deeper lints, capped

# Infrastructure & ops
terraform plan -no-color -detailed-exitcode > /tmp/plan.log 2>&1; echo "exit=$?"  # 0 none, 1 error, 2 changes
kubectl get pods -o name                   # names only, no table
docker ps --format '{{.Names}}'            # container names only
helm list --short                          # release names only
gh run view <run-id> --log-failed > /tmp/ci.log 2>&1   # CI: failed steps only, then grep
```

## Habits that waste context

- `cat`-ing a file to "show" it when nothing needs showing.
- Re-running a failing suite in verbose mode when the quiet failure
  message already names the broken test. Run just that test with its
  full path: `pytest tests/api/test_auth.py::test_login`
- Pasting long output back to the user. Summarize the finding and cite
  the file/line.
- `ls -la` on large directories. Use `ls` or glob for the specific
  files you need.
- `print(os.environ)` or bare `env` to "see what variables are set". Use
  `env | grep -i prefix` for targeted lookup; a full dump also pulls
  secrets into the transcript.

## Exception

Correctness beats thrift: if capped output hides the actual error, widen the
window (bigger `tail`, targeted `grep -B/-A`) until you can see it. Saving
tokens on a wrong answer saves nothing.

## Related skills

- `frugal-context`: the same thrift for reading files. Grep before reading
  so you only feed relevant sections into context.
- `checkpoint`: record which quiet flags work for this project so you
  don't have to rediscover them after context compaction.
- `radical-compression`: carries a log's path across cycles instead of its
  contents, so keep the log file where it can be grepped again.
- `github-actions`: when the long log is a CI run and the fix belongs in
  the workflow itself.
