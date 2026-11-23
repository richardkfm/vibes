# Troubleshooting workflow runs

Read this when no run appears after a push, a run fails for a reason that does
not reproduce locally, the push itself is rejected, or a workflow is too slow.

## No run appeared

Likeliest first:

- A `branches:`, `tags:` or `paths:` filter does not match what was pushed.
- The trigger is `workflow_dispatch` or `schedule` and the file is not on the
  default branch yet. To exercise such a workflow, or a tag-triggered one,
  before merge, add a temporary `pull_request` trigger with the publishing
  steps guarded by `if:`, and remove it before merging.
- The file is invalid. The Actions tab lists it by file path with the error;
  `actionlint` usually finds the cause faster.
- The PR has a merge conflict. `pull_request` workflows do not run until it is
  resolved.
- Actions is disabled for the repo or fork, or a first-time contributor's run
  is waiting for a maintainer's approval.
- The push or PR came from a workflow using its own `GITHUB_TOKEN`. Events
  caused by that token start no new runs, and PRs it opens wait for approval.

## Fails in CI, passes locally

Read the failing step first: send `gh run view <run-id> --log-failed` to a file
and grep it. For more detail, `gh run rerun <run-id> --failed --debug`. A
runner is a clean machine, so the usual differences are:

- **Shallow clone.** Checkout fetches one commit and no tags. `git describe`,
  version-from-git tools and diffs against the base branch need
  `fetch-depth: 0`.
- **Files that exist only on a laptop**: untracked or ignored files, a local
  `.env`, a warm cache, globally installed tools.
- **`Resource not accessible by integration` (HTTP 403).** The token lacks a
  permission. Add that scope to the job's `permissions`. On a fork PR the token
  is read-only by design; see `privileged-triggers.md`.
- **Missing secrets.** An unset secret expands to an empty string, and fork and
  Dependabot PRs receive none of the repository's secrets.
- **Environment.** A different tool version than local (take it from the repo's
  version file), a case-sensitive file system, a missing system package or
  service, `CI=true` changing a tool's behaviour.

## Push rejected over the `workflow` scope

The token may not create or change files under `.github/workflows`. Tell the
user: `gh auth refresh -s workflow` for a `gh` login, or the Workflows
permission on a fine-grained token. Do not route around it.

## Slow runs

Measure before changing anything:

```bash
gh run view <run-id> --json jobs \
  --jq '.jobs[] | .name, (.steps[] | [.name, .startedAt, .completedAt] | @tsv)'
```

Then fix the largest item first:

- dependency install without a cache: use `cache:` on the setup action
- one long serial job that could be several parallel jobs
- a matrix wider than what the project supports
- superseded runs still running: add `concurrency` with `cancel-in-progress`
- a heavy job running on changes that cannot affect it: add a `paths:` filter,
  though never on a required check, because a skipped required check blocks the
  PR
