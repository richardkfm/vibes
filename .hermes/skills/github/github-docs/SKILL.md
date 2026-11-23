---
name: github-docs
description: "Use when opening a PR or changing documented behavior."
version: 1.0.0
author: richardkfm/vibes
license: MIT
metadata:
  hermes:
    tags: [GitHub, Documentation, README, Pull Requests]
    related_skills: [humanize-language, github-actions, github-releases, linear-issues]
---

<!-- Generated from .claude/skills/github-docs/SKILL.md by scripts/sync_hermes_skills.py. Edit the source and re-run the script. -->
# GitHub Docs

A change is finished when the people it affects can find out what changed
without asking the author. On GitHub that record lives in two places: the
README and the docs next to it describe the project as it is now, and the
pull request description explains one change to whoever has to approve it
or later lands on it from `git blame`. Which one carries the weight, and how
much to write, follows from the blast radius: who reviews the change and who
is affected by it.

For a diff that is plainly contained (a typo, a comment, formatting), skip
steps 1 and 2. It is the Contained row below and gets the same two lines in
any repo.

Commands use git and the `gh` CLI. Where `gh` or its `pr` commands are
unavailable, the REST API (`gh api`, where `-F body=@FILE` reads a body
from a file) and the GitHub MCP tools `create_pull_request` and
`update_pull_request` do the same job.

## When to Use

Use when the user invokes /github-docs, asks to open a PR, write its description, update the README or document a change, and whenever the agent is about to open or update a PR or has changed behavior, setup or configuration that a README describes, even if nobody mentions documentation.

## 1. Solo or team repo

If the user has said who reviews their PRs, that settles it. Otherwise
decide from evidence, once per repo per session:

```bash
# Recent committers. HEAD is required: in a non-interactive shell,
# shortlog without a revision reads stdin and prints nothing.
git shortlog -sne --no-merges --since="6 months ago" HEAD
# Review machinery checked into the repo, wherever it lives
git ls-files | grep -iE '(^|/)(codeowners|contributing|pull_request_template)'
# Owner type, fork status, default branch. Type {owner} and {repo}
# literally; gh fills them in from the current repo.
gh api 'repos/{owner}/{repo}' --jq '{owner: .owner.type, fork: .fork, default: .default_branch}'
# Is merging gated? Substitute the default branch for main.
gh api 'repos/{owner}/{repo}/branches/main' --jq .protected
gh api 'repos/{owner}/{repo}/rules/branches/main' --jq '[.[].type]'
```

It is a **team repo** if any one of these holds:

- More than one person committed recently. Count people, not identities:
  bots (dependabot, renovate, github-actions) and agent commit identities
  belong to whoever runs them.
- A CODEOWNERS file, a PR template or a CONTRIBUTING file exists.
- The owner is an Organization, or the PR goes from a fork to someone
  else's repo.
- The default branch is protected, or its rules include `pull_request`.

It is a **solo repo** when none hold: one person, a user-owned repo, nothing
gating merges. When the evidence conflicts, treat it as a team repo. Writing
for a reviewer who turns out not to exist wastes a few lines; leaving a real
reviewer without context costs a review round or a bad merge.

## 2. Size the blast radius

```bash
git diff --stat origin/main...HEAD           # what changed against the default branch
git grep -n 'CHANGED_NAME'                   # every user of a changed name in this repo
gh search code 'CHANGED_NAME' --owner ORG    # users in the organization's other repos
```

Then answer the two questions a line count cannot:

- **Who consumes what changed?** Nobody outside the module, the tool's
  users, or other teams, services, pipelines and deploys.
- **Does reverting the commit undo it?** An applied migration, a published
  package version, deleted data or a variable already renamed in a deployed
  environment all outlive a revert, which makes a change wide whatever its
  size.

| Radius | The diff touches | Solo repo | Team repo |
|---|---|---|---|
| **Contained** | Internals behind an unchanged interface, tests, comments, typos, formatting | Commit message; one or two lines if there is a PR | Title plus one to three lines, no headings |
| **Visible** | Something a user or caller can observe (a new flag, option, endpoint, output, default, a fixed bug) while nothing existing breaks | README and docs updated in the same change; PR body of two to four lines | Three-heading PR description (step 3); README only if it describes the behavior |
| **Wide** | Something other people's work depends on: public API or exported names, a shared library, config keys or env vars, CI and build, database schema, dependencies, auth and permissions, deploy config. Or anything a revert does not undo | README plus an upgrade note where users will see it; PR body states the break in its first line | Three headings with Risk expanded into Blast radius, Migration, and Rollout and rollback; README and config docs updated |

Size by the riskiest hunk, not the line count: a one-line env var rename is
wide, a 600-line refactor behind an unchanged interface is contained. When
torn between two rows, take the larger.

## 3. Write the PR description

If commits go straight to the default branch and there is no PR, the commit
message carries the what and why; go to step 4.

**With a PR template** (the `git ls-files` line in step 1 finds it; with
several under `PULL_REQUEST_TEMPLATE/`, pick the one that fits), fill in
its layout. `gh pr create --body-file` and the API do not insert it, so
read the file. Keep its headings and order, tick only the checkboxes that
are true, and under a heading that does not apply write "n/a" with the
reason instead of deleting it, because reviewers and bots scan for those
headings. A contained change needs a few words per heading. A wide change
appends the wide sections the template lacks.

**Without a template**, use three headings. *What and why*: the problem or
need first, then what the change does about it, with the issue linked. *How
it was verified*: the commands that ran and what they showed, and what was
not tested. *Risk*: what could break, who would notice, how to roll back.
A small team PR, titled `Fix last search page being dropped`:

```markdown
## What and why
Search returned an empty last page when the result count was an exact
multiple of the page size (#412). `page_count` used floor division; it now
rounds up.

## How it was verified
- New `test_last_page_exact_multiple` fails on main and passes here.
- `pytest tests/search -q`: 87 passed.
- Not checked against production data.

## Risk
Only `search/pagination.py` changes behavior. Revert to roll back.
```

Scale that to the table in step 2:

- **Contained, or any solo repo**: no headings. A typo fix in a comment is
  title `Fix typo in retry backoff comment`, body `Comment only; no behavior
  change.`, not a Summary / Changes / Testing skeleton with one line under
  each. A solo PR says what and why, what was run, and where the README
  covers it.
- **Wide**: expand `## Risk` into `## Blast radius`, `## Migration` and
  `## Rollout and rollback`. Read
  [references/wide-change.md](references/wide-change.md) before writing
  them: it lists what a reviewer needs for each kind of wide change (env
  vars, schema, API, dependencies, CI, auth) and works through an env var
  rename. When such a change affects no one (a patch bump of a dev-only
  dependency), keep the headings at one line each; a missing section reads
  as "not considered".

Write for a reviewer who has seen none of the session:

- **Why before what.** The diff shows what changed; only the description can
  say why. Do not list files. Name one only to steer attention: "Start with
  `billing/proration.py`; the other 14 files are the mechanical rename."
- **Evidence, not assurances.** State what ran in this session and what it
  showed, and say what was not run. "All tests pass and the change is fully
  backward compatible" is an assurance; the example above is evidence.
- **No session narration.** "First I explored the codebase, then I
  noticed..." gives the reviewer nothing to check, and "as discussed" needs
  a conversation they never saw. Keep a rejected alternative, in one line,
  only when the reviewer would otherwise propose it.
- **A title that states the outcome** in the repo's commit style (check
  `git log --oneline -10`), not "Update pagination.py". On squash-merge
  repos it usually becomes the commit subject on the default branch.

```bash
gh pr create --draft --title "TITLE" --body-file /tmp/pr-body.md
gh pr edit NUMBER --body-file /tmp/pr-body.md    # after pushes that change scope
```

Pass the body as a file kept outside the working tree: an inline `--body`
string loses its backticks to shell substitution and turns `\n` into literal
text. Open as a draft unless the user asked for a ready PR, so they can read
the description before anyone is notified; code owners are only requested
once a draft is marked ready, and that is the user's call. Edit the
description when later commits change the scope, the verification or the
risk: one that covers the first commit of five misleads.

## 4. Update the README and existing docs

In a solo repo, update them on every change to behavior, setup or usage,
because nothing else will remember it. In a team repo, update them only
when user-facing behavior, setup or usage changed; internal changes are
documented by the PR. Either way the docs go in the same commit or PR as
the code, so the two cannot drift apart. Find every place that describes
what changed, not just the README:

```bash
git grep -n -i 'OLD_NAME_OR_FLAG'   # README, docs/, .env.example, sample configs, CI, help text
```

- **Put it where it already belongs.** Edit the section that covers the
  topic; add a section only when none fits. A README answers four things:
  what this is, a quick start that runs from a fresh clone, configuration
  (every option and env var with its default), and an example or two. If
  there is no README at all, write a short one that answers those four, not
  one about today's change.
- **Run what you write.** Run every command, check that every path exists,
  compare flag names and defaults against `--help` or the code. When
  something could not be run (it needs credentials, a paid API, hardware),
  say so instead of presenting it as checked.
- **Match what is there.** Heading levels, tables versus lists, code-fence
  languages, tone, emoji or none. Leave unrelated sections alone so the
  diff stays reviewable.
- **Describe the present, not the change.** No "New", "Recently added" or
  dated update sections: they are stale after the next change. History
  belongs in the commit, the PR and `CHANGELOG.md` if the repo keeps one
  (add an entry in its format).

A solo repo gains a `--timeout` flag. The README's existing options table
gets a row in the same commit, checked against `linkcheck --help`, and the
PR body is two lines: why the flag exists, and the command that showed it
working. The README does not get a "What's new" section announcing "a
powerful new `--timeout` flag".

```diff
 | `--depth N` | `2` | How many links deep to follow |
+| `--timeout SECS` | `10` | Give up on a URL after this many seconds |
```

## 5. Keep out of both

- The agent's reasoning, apologies, self-assessment and sales talk: "Sorry
  for the large diff", "this should hopefully work", "powerful",
  "seamless", exclamation marks, emoji the repo's own docs do not use.
- Secrets and internals: tokens, connection strings, internal hostnames and
  IPs, customer names or data, absolute paths from the local machine. PR
  descriptions are emailed to watchers and indexed on public repos, and
  editing one later recalls neither. Use placeholders such as
  `postgres://USER:PASSWORD@HOST/db`.

## Related skills

- `humanize-language`: run the finished README section or PR description
  through it so the prose reads like a person wrote it.
- `github-actions`: a workflow change is always wide; give it the wide
  sections.
- `github-releases`: release notes are the third place documentation goes.
- `linear-issues`: the issue comment links to the PR instead of repeating
  it.
