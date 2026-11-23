# Privileged triggers and fork pull requests

Read this before writing or changing a workflow that uses
`pull_request_target`, `workflow_run` or `issue_comment`, and whenever fork
pull requests are supposed to reach secrets or a write token.

## Why these triggers are different

`pull_request` runs the workflow file from the PR's merge commit, so for a fork
GitHub hands it a read-only token and no secrets. The three triggers above take
the workflow file from the default branch instead and run it with the base
repository's secrets and a write-capable token, and an outsider can cause the
event by opening a PR or writing a comment. That is safe exactly as long as
only default-branch code executes.

## How it goes wrong

The compromise (a "pwn request") takes two steps: fetch code from the PR, then
execute something from it. The second step is easy to miss, because "execute"
covers anything the fetched tree controls:

- checkout with `ref: ${{ github.event.pull_request.head.sha }}`,
  `refs/pull/<n>/merge` or `repository:` set to the fork, followed by install,
  build, test or lint. `npm install` runs lifecycle scripts; a Makefile, a
  tool's config file or a plugin list is code too.
- `git fetch` or `gh pr checkout` of the PR in a `run:` step.
- downloading an artifact from the fork's `pull_request` run and running or
  sourcing it.
- pasting PR text into a script (see "Untrusted input and secrets" in
  SKILL.md), which needs no checkout at all.

## Decide in this order

1. **Stay on `pull_request`.** Most "CI needs secrets" cases do not: guard the
   secret-dependent steps so they skip for forks.

   ```yaml
   if: >-
     github.event_name != 'pull_request' ||
     github.event.pull_request.head.repo.full_name == github.repository
   ```
2. **Split the work.** An unprivileged `pull_request` workflow runs the fork's
   code and uploads its results as an artifact. A `workflow_run` workflow
   starts when that one completes, downloads the artifact and only reads it:
   posts the comment, sets the label. It never executes it, and it validates
   what it reads (a PR number is digits only; text goes in through a file or
   `env`, not the command line).
3. **Use `pull_request_target` without any PR code** for jobs that need only
   the event itself: labeling, triage, a welcome comment.
4. **Anything beyond that is the owner's decision.** Describe the risk in the
   PR and wait for it.

## Hardening when one is used

- Least `permissions` on every job, and only the secrets that job needs.
- Leave GitHub's guard rails on. `actions/checkout` refuses fork PR code under
  `pull_request_target` and `workflow_run` unless
  `allow-unsafe-pr-checkout: true` is set. Low-trust triggers get read-only
  access to the default branch's cache unless a write-capable `cache-mode` is
  declared. A public repository can have `pull_request_target` blocked by
  GitHub's default event policy until an event policy explicitly allows it.
  Each opt-out is named to stand out in review. Do not add one unless the owner
  says so.
- No self-hosted runners on workflows an outsider can trigger.
- Source material, both worth reading in full: "Securely using
  pull_request_target" in GitHub Docs, and "Preventing pwn requests" from
  GitHub Security Lab.
