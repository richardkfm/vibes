---
name: github-releases
description: Cuts a release on GitHub. Works out the next version from what changed since the last tag, creates and pushes an annotated git tag on the right commit, and publishes a GitHub release with notes people can act on (summary, breaking changes first, upgrade steps) plus any assets. Follows the repo's existing tag, changelog and version-file conventions, confirms before the irreversible public steps, and verifies the result. Use when the user invokes /github-releases, asks to release, ship, publish, cut or tag a version, bump the version, write release notes or a changelog entry, make a pre-release or release candidate, or automate releases, even if they only say "tag it" or "ship v2".
---

# GitHub Releases

Pushing a tag and publishing a release are public and, in practice,
irreversible. Watchers are notified, package caches and other people's
lockfiles record the tag, and a tag push can start workflows that publish to
registries. So nearly all of the work happens before the push: find the
convention, choose the version, write the notes, get a yes.

## Find the repo's convention

```bash
git fetch --tags --quiet origin
git tag --sort=-v:refname | head -5      # v1.2.3 or 1.2.3? pre-release style?
gh release list --limit 5                # are tags published? drafts waiting?
ls CHANGELOG* HISTORY* NEWS* .github/release.yml 2>/dev/null
grep -rlE 'tags:|release' .github/workflows/ 2>/dev/null
git grep -nF '<last version, without v>' -- ':!*lock*' | head   # version files
```

What exists wins over this skill's defaults:

- **A release tool is configured** (release-please, semantic-release,
  changesets, goreleaser and the like): drive the tool by merging its
  release PR or adding the changeset. A hand-made tag corrupts its state.
- **A workflow fires on tags or `release` events**: read it. It decides
  whether pushing the tag is the whole release or only the first step, and
  what else goes out with it (packages, images, docs).
- **Tag format, titles and signing** continue what is there. If `git
  cat-file -p <last-tag>` shows a signature, sign the new tag too (`-s` in
  place of `-a`).
- **No tags yet**: start at `v0.1.0`, or `v1.0.0` when the project is
  already relied on in production.

## Work out the next version

```bash
last=$(git describe --tags --abbrev=0 origin/<default-branch>)
git log --oneline --no-merges "$last"..origin/<default-branch>
git diff --stat "$last"..origin/<default-branch>
```

Read the diff of the public surface as well as the commit subjects, which
under-report breaking changes.

| Changed since the last tag | Bump |
|---|---|
| Something users rely on was removed, renamed or changed: API, CLI flag, config key, default, output format, minimum runtime | major |
| New capability, existing usage untouched | minor |
| Fixes, performance, docs, internals | patch |

Before 1.0 a breaking change bumps the minor instead. A release candidate
carries a semver suffix (`v2.0.0-rc.1`). If nothing user-visible changed,
say so instead of releasing. State the proposal with its reason in one
line: "v1.5.0: adds `--json` output (#212), nothing breaking".

When the version also lives in files (`package.json`, `pyproject.toml`,
`Cargo.toml`, a changelog), change them in a PR (see `github-docs`) and
merge it before tagging. The tag has to point at a commit that already
carries the new version, or the tagged source disagrees with its own tag
for good. Use the ecosystem's bump command where one exists (`npm version
1.5.0 --no-git-tag-version`) so lockfiles stay consistent.

## Write notes people can act on

GitHub's generated notes are a list of merged PR titles. Treat them as raw
material. Fetch them without creating anything:

```bash
gh api repos/{owner}/{repo}/releases/generate-notes \
  -f tag_name=v1.5.0 -f target_commitish=<default-branch> \
  -f previous_tag_name=v1.4.2 --jq .body > generated.md
```

Name the last stable tag as `previous_tag_name`; otherwise a final release
that follows release candidates lists only the changes since the last
candidate. Then write `notes.md` for a reader deciding whether and how to
upgrade: what the release means for them in two or three sentences,
breaking changes first with what to do about each, upgrade steps, then
additions and fixes in user terms, and the generated list last, pruned of
dependency bumps and chores. A changelog entry is the same text; write it
once.

````markdown
Configuration moves from environment variables to one `app.toml`, and Node
18 is no longer supported. Startup is about twice as fast on large projects.

## Breaking changes
- **`app.toml` replaces the `APP_*` environment variables** (#231). Run
  `app migrate-config` once; it writes the file from your environment.
- **Node 20 or newer is required** (#236).

## Upgrade
1. Move to Node 20 or newer.
2. Install 2.0.0 and run `app migrate-config`.
3. Remove the `APP_*` variables from your deployment.

## Added
- `app check --json` for machine-readable output (#240)

## Fixed
- Crash when the cache directory is read-only (#228)

**Full changelog**: https://github.com/OWNER/REPO/compare/v1.4.2...v2.0.0
````

## Confirm before anything public

Everything so far is local or reviewable. Before pushing the tag, show the
user the version and the reason for it, the commit it will point at (short
SHA, subject, CI status), what the push sets off according to the workflow
files (builds, package publishes, deploys), and the notes. Then wait for a
yes.

Skip the question only when the user has already given both the version
and the instruction to publish ("release v1.5.0 now"). "Prepare a release"
or "what should the next version be?" is neither. In an unattended run
without that go-ahead, stop here and leave the notes file and the exact
commands.

## Tag and publish

```bash
git fetch origin
sha=$(git rev-parse origin/<default-branch>)   # the merged bump commit
gh run list --commit "$sha" --json workflowName,status,conclusion
git tag -a v1.5.0 "$sha" -m "v1.5.0"
git push origin v1.5.0
gh release create v1.5.0 --verify-tag --title "v1.5.0" --notes-file notes.md
```

- **CI is green on that exact commit** before the tag exists. If no runs
  are listed for it, check the merged PR's checks.
- **Annotated tag on an explicit SHA.** `-a` records who tagged and when,
  and `git describe` skips lightweight tags. Naming the SHA avoids tagging
  whatever `HEAD` is in a stale or feature-branch checkout.
- **Push the one tag by name.** `git push --tags` publishes every local
  tag, stale experiments included.
- **`--verify-tag`** makes `gh` refuse when the tag is not on the remote.
  Without it, `gh` silently creates a lightweight tag on the tip of the
  default branch, whatever that is by then.
- **`--draft`** when someone should review first or assets come later (`gh
  release upload v1.5.0 dist/*`); publish with `gh release edit v1.5.0
  --draft=false`. With immutable releases enabled, assets cannot change
  after publishing, so always go draft, upload, publish.
- **`--prerelease`** for candidates and betas. **`--latest=false`** for a
  fix on an older line (v1.9.5 while v2 exists), so "Latest" stays put.

When a workflow creates the release from the tag, stop after the push.
Watch the run (`gh run watch <run-id> --exit-status`), then put the written
notes in place with `gh release edit v1.5.0 --notes-file notes.md`, adding
`--draft=false` if the workflow left a draft. Running `gh release create`
as well would collide with it.

## A published tag never moves

Once a tag is pushed, someone may have fetched it. Git does not update a
tag that already exists in a clone, and package caches and SHA pins keep
the old target, so moving it, or deleting and recreating it, leaves two
different things named v1.5.0. With immutable releases enabled GitHub
refuses outright. When a release is wrong, fix forward: publish v1.5.1 and
edit the bad release's notes to point at it. Withdraw a package through its
registry's own yank or deprecate mechanism. If the user asks for a tag to
be deleted anyway, explain this first; the decision is theirs, not the
agent's. The one tag meant to move is a floating major tag such as `v1` in
a repo that publishes a GitHub Action; follow that repo's practice.

## Verify

```bash
git ls-remote --tags origin 'v1.5.0*'    # the ^{} line is the commit: equals $sha
gh release view v1.5.0 --json tagName,isDraft,isPrerelease,assets,url
gh release list --limit 3                # "Latest" sits on the right release
gh run list --commit "$sha" --limit 5    # tag-triggered workflows finished green
```

Read the rendered notes once (`gh release view v1.5.0`): no broken lists,
no leftover placeholders. Every expected asset is attached and not empty.
Whatever the tag set off downstream has landed, for example the new version
showing in its registry. Report the release URL.

Then tell the people waiting on it: comment on the issues that shipped,
with the version and the release link (`linear-issues` when they live in
Linear), and update install instructions or docs that name a version
(`github-docs`).

## Automate it

Once releases recur, a tag-triggered workflow makes them repeatable: push
the tag, and CI builds, attaches assets and creates the release. Read
`references/release-workflow.md` when adding or reviewing that automation;
it holds a minimal hardened workflow and the choices behind it. Build it
with `github-actions`, since it is a workflow like any other.

Without `gh`, or in a sandbox that blocks some of its subcommands, the same
steps exist as REST calls (`POST /repos/{owner}/{repo}/releases`,
`.../releases/generate-notes`, `GET .../releases/tags/{tag}`) through `gh
api`, `curl` or the release tools of a GitHub MCP server. Tagging stays
plain git.

## Related skills

- `github-actions`: writes, hardens and verifies the release workflow.
- `github-docs`: the version-bump PR, and README or docs that name a version.
- `linear-issues`: comment on the issues a release ships.
- `lean-output`: release builds log a lot. Send logs to a file and grep.
