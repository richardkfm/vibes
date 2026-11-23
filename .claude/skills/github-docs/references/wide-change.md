# Wide-radius changes

Read this when step 2 of the skill puts a change in the Wide row.

1. [The three wide sections](#the-three-wide-sections)
2. [What the reviewer needs, by kind of change](#what-the-reviewer-needs-by-kind-of-change)
3. [Worked example: an env var renamed in a team repo](#worked-example-an-env-var-renamed-in-a-team-repo)
4. [The same change in a solo repo](#the-same-change-in-a-solo-repo)

## The three wide sections

They take the place of `## Risk`. Put Blast radius and Migration straight
after What and why: the people affected look for their own name before they
care how the change was tested.

**Blast radius.** Who and what is affected, by name: teams, services,
environments, pipelines, downstream repos. Include how they were found (the
`git grep` or `gh search code` result), and what is not affected when a
reviewer would otherwise worry about it. Mention a team (`@org/team`) only
when it has to act, because a mention notifies it.

**Migration.** Numbered steps a reader can copy, one list per affected
group, in the order they must happen, with old and new values side by side.
Say whether the old way keeps working, and until when.

**Rollout and rollback.** The order things must be merged or deployed in,
any flag or compatibility window, how to undo the change, and what a revert
does not undo.

## What the reviewer needs, by kind of change

| Change | State in the description |
|---|---|
| Config key or env var | Old and new name. Whether the old one is still read, and for how long. Every place it is set: deploy manifests, CI variables and secrets, `.env.example`, each developer's local environment. What happens when it is missing: a startup failure or a silent default |
| Database schema | Whether the previous version of the code runs against the new schema, which fixes the deploy order. Locking or runtime on large tables. Whether a down migration exists and what data it loses |
| Public API or exported name | Which callers break and how they were found. The deprecation path or version bump. A before-and-after snippet |
| Shared library or package | Which repos consume it and whether they pin a version. What they must change when they upgrade |
| Dependencies | From and to versions. Breaking changes in its changelog that touch this codebase. Whether only the lockfile changed. New transitive dependencies or a license change worth a look |
| CI, build, workflows | Which jobs, branches and secrets are affected. Whether the new workflow has actually run on this PR. Any renamed job that branch protection lists as a required check: the rename blocks every open PR until the rule is updated |
| Auth and permissions | Who gains or loses access. Token scopes or roles that change. Whether existing sessions or tokens are invalidated |

Writing these down sometimes shows that the change is harder to roll out
than the diff suggested: the old variable is still set in three environments
the PR cannot touch. That is the documentation doing its job. Put the
finding at the top of the description and tell the user, instead of
softening it to keep the PR tidy.

## Worked example: an env var renamed in a team repo

Evidence: twelve people in `git shortlog`, a CODEOWNERS file, a protected
`main`, so a team repo. `git grep -n REDIS_URL` finds the settings module,
`.env.example`, `docker-compose.yml`, the test workflow, two Helm values
files, the README and `docs/configuration.md`: an env var, deploy config and
CI, so the radius is wide. The same PR updates the README configuration
table, `docs/configuration.md` and `.env.example`, because setup changed for
everyone who runs the service.

Title: `Rename REDIS_URL to CACHE_URL, keep REDIS_URL as a fallback`

```markdown
## What and why
The cache no longer has to be Redis (#530 adds a Memcached backend), so the
setting that points at it is renamed from `REDIS_URL` to `CACHE_URL`. The
app still reads `REDIS_URL` when `CACHE_URL` is unset and logs a deprecation
warning, so nothing breaks on merge.

## Blast radius
Everyone who runs or deploys the service.
- Deploys: staging and production set `REDIS_URL` in
  `deploy/helm/values-*.yaml`. Updated here.
- CI: `.github/workflows/test.yml`. Updated here.
- Local development: each developer's `.env` is not in the repo and still
  says `REDIS_URL`. It keeps working, with a warning.
- Other repos: `gh search code REDIS_URL --owner acme` finds `acme/worker`
  and `acme/ops-scripts`. They read their own copy of the variable and are
  not changed or broken by this PR.
- Not affected: the Redis instance, its data, key names.

## Migration
1. In your local `.env`, rename `REDIS_URL=` to `CACHE_URL=`. Same value.
2. Nothing to do for staging or production; the Helm values in this PR
   carry the rename.
3. The fallback is removed in the next major version, tracked in #541.

## How it was verified
- `pytest -q`: 412 passed, including the new
  `test_cache_url_falls_back_to_redis_url`.
- Started the app locally three ways: only `REDIS_URL` set (cache works,
  warning logged), only `CACHE_URL` set (no warning), neither set (fails at
  startup with "CACHE_URL is not set").
- Not verified: the Helm change has not been deployed. `helm template`
  renders both values files without errors.

## Rollout and rollback
Safe to merge and deploy in any order because of the fallback. To roll
back, revert this PR: the reverted Helm values set `REDIS_URL` again, and
the old code reads it. Nothing here outlives a revert.
```

## The same change in a solo repo

The README's configuration section carries it, in the present tense:
"`CACHE_URL`: where the cache lives. `REDIS_URL` is still accepted." If the
repo keeps a `CHANGELOG.md` or publishes releases, the upgrade note goes
there. The PR body opens with the break and stays short: "Renames
`REDIS_URL` to `CACHE_URL`; the old name still works and logs a warning.
README and `.env.example` updated. `pytest -q`: 412 passed."
