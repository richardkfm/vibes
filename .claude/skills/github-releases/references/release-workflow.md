# Tag-triggered release workflow

Read this when adding or reviewing a workflow that creates a GitHub release
once a version tag is pushed. Write and ship it with the `github-actions`
skill: pinning, permissions, validation and the draft PR apply here too.

## Minimal workflow

```yaml
name: Release

on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'     # v1.2.3
      - 'v[0-9]+.[0-9]+.[0-9]+-*'   # v1.2.3-rc.1

permissions:
  contents: read

concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false

jobs:
  release:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: write   # create the release and upload its assets
    steps:
      - uses: actions/checkout@<40-char-commit-sha> # vX.Y.Z
        with:
          fetch-depth: 0   # full history, for the ancestry check below
          persist-credentials: false

      - name: Refuse tags that are not on the default branch
        env:
          DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}
        run: git merge-base --is-ancestor "$GITHUB_SHA" "origin/$DEFAULT_BRANCH"

      - name: Build
        run: make dist   # the repo's own build command; writes to dist/

      - name: Create draft release
        env:
          GH_TOKEN: ${{ github.token }}
          TAG: ${{ github.ref_name }}
        run: |
          flags=(--verify-tag --draft --generate-notes --title "$TAG")
          case "$TAG" in *-*) flags+=(--prerelease) ;; esac
          gh release create "$TAG" "${flags[@]}" dist/*
```

Resolve both placeholders the way `github-actions` describes; do not copy a
SHA or version from memory. `gh` is preinstalled on GitHub-hosted runners
and reads its token from `GH_TOKEN`.

## The choices behind it

- **Version-shaped tag patterns, not `v*`**, so a tag such as
  `vendor-import` starts nothing.
- **Draft by default.** The workflow attaches assets and generated notes.
  Then a person, or the agent once it has the go-ahead, puts the written
  notes in place and publishes: `gh release edit <tag> --notes-file notes.md
  --draft=false`. Watchers are notified with the final notes, not the raw
  list. Drop `--draft` for hands-off publishing and edit the notes
  afterwards. With immutable releases enabled, draft, upload, publish is the
  only order that works, because assets cannot change once published.
- **Write access on one job only.** The workflow default is `contents:
  read`; build and test jobs added later stay read-only.
- **Tag name through `env`.** Ref names may contain shell metacharacters, so
  `${{ github.ref_name }}` never goes straight into the script.
- **Ancestry check.** A tag can be pushed on any commit. This refuses one
  that never reached the default branch, such as an unmerged feature branch.
- **`cancel-in-progress: false`.** A half-finished release is worse than a
  queued one.

## Worth adding when relevant

- **Version check.** Fail when the tag and the version file disagree; it
  catches a tag pushed before the bump merged. For npm: `test "v$(node -p
  "require('./package.json').version")" = "$TAG"`.
- **Tests before release.** Run the CI checks as a job the release job
  `needs:`, or call the CI workflow as a reusable workflow, so a red commit
  cannot ship.
- **Package publishing** in a separate job that `needs:` the build, with its
  own minimal permissions, a protected `environment`, and OIDC trusted
  publishing (`id-token: write`) where the registry supports it, in place of
  a stored token.

## Gotchas

- **Events caused by `GITHUB_TOKEN` start no other workflows.** A release
  created here will not fire workflows listening on `release: published`,
  and a tag pushed from a workflow will not fire this one. Chain the steps
  as jobs in one workflow or call a reusable workflow.
- **The first real tag is a bad moment to find a typo.** Before merging, run
  the build and guard steps on the PR through a temporary `pull_request`
  trigger, with the release step guarded by `if: github.ref_type == 'tag'`,
  then remove the trigger. If the user agrees, make the first tagged run a
  pre-release (`v0.1.0-rc.1`) to exercise publishing at low stakes.
- **Re-running does not pick up a fix.** A tag-triggered run uses the
  workflow file from the tagged commit, so after fixing the workflow on the
  default branch a re-run repeats the failure. Cut the next patch version
  rather than moving the tag.
