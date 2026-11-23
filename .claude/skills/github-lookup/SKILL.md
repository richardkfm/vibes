---
name: github-lookup
description: Searches GitHub for existing repos that already solve a planned project or major feature before any code is written, then recommends one of five paths (depend on a repo, contribute the missing piece upstream, fork it, inline parts of its code, or build from scratch). Use when the user invokes /github-lookup, proposes building a new tool, library, service, CLI, bot or other project from scratch, asks whether something already exists or which library to use for a use case, or wants alternatives to a package. Also use before starting any nontrivial build the user has not already tied to a specific approach, even if they never ask for a search.
---

# GitHub Lookup

Writing a new implementation from scratch spends tokens re-deriving code that
may already exist, tested and maintained, in a public repo. Before generating
new code for a nontrivial project or feature, spend a small research budget
checking what's already out there — the cost of a search is far lower than
the cost of writing (and later maintaining) a parallel implementation.

## When to run this

At the start of any request to build a new tool, library, service, or
significant feature that isn't a trivial script. Skip it for small,
self-contained changes (a bugfix, a one-off utility, a function inside an
existing codebase) — the research overhead isn't worth it below a certain
size.

## Search strategy

Use web search and GitHub search to find existing projects. Search in plain
terms plus obvious synonyms, adjacent keywords, and framework names:

```bash
# GitHub repository search
gh search repos "<concept>" --sort=stars --limit=10
gh search repos "<concept>" --language=python --sort=stars --limit=10

# Signals for one candidate in a single call
gh repo view OWNER/REPO --json stargazerCount,pushedAt,isArchived,licenseInfo,latestRelease

# Web search for broader coverage
# "python library <concept>"
# "open source <concept>"
# "<concept> alternative"
# "best <concept> library"
```

Without the `gh` CLI, run the same queries through whatever GitHub search
tool is available, or github.com/search.

For each candidate, note in one line: stars/last-commit (maintenance
signal), license, language, and a rough % match to the use case.

## Decision framework

Match quality drives the decision. There are five outcomes — **depend**,
**contribute upstream**, **fork**, **inline**, **build** — cheapest first:

1. **~90%+ match, actively maintained** → Don't build a competing project.
   **Depend** on it, or — if it's missing the last 10% — **contribute
   upstream**: open an issue or PR against the maintainer rather than
   forking a parallel copy. Recommend this to the user explicitly; it's
   the option most tempting to skip because building feels more productive
   than asking.

2. **Partial match (rough fit, missing pieces, license permits)** →
   **Fork** it and build the delta on top when most of the repo is wanted,
   or **inline** (vendor) the specific files/functions that fit rather
   than reimplementing them. Inlining saves the tokens of re-deriving
   working code; forking saves them at project scale instead of function
   scale.

3. **No good match, or license/maintenance disqualifies every candidate** →
   **Build** from scratch. State why in one line (e.g. "closest match has
   been unmaintained for years and its license is unclear") so the
   decision is recorded, not silently skipped.

Example recommendation, as it should reach the user:

> Found `acme/feedparse` (4.1k stars, pushed last month, MIT) covering all
> but Atom 0.3 feeds. Recommend **depend** and open an upstream issue for
> Atom 0.3; a fork is not worth maintaining for one format. OK?

## License check (before any fork or inline)

The license decides whether copying is allowed at all, so settle it before
recommending either path.

- **Permissive** (MIT, Apache-2.0, BSD) → safe to inline/fork with attribution
  (keep the license file, credit the source in the commit/PR).
- **Copyleft** (GPL, AGPL) → inlining or forking can force the same license
  onto the user's project; **flag this to the user** before proceeding,
  don't decide unilaterally.
- **No license file** → treat as "no permission granted"; don't inline or
  fork, only use it as a reference for how the problem was solved.
- **Multiple licenses across a repo** → check the per-file license in the
  files you want to use, not just the top-level LICENSE.

## Vetting checklist

Before recommending a dependency or fork:

- [ ] **Maintenance**: Last commit within last 6 months? Recent releases?
- [ ] **Stars/adopters**: Is anyone else using it? (Not the only signal, but a useful one.)
- [ ] **Issue response rate**: Do maintainers respond to issues/PRs?
- [ ] **Build/test status**: Does CI pass? Broken tests = signal of abandonment.
- [ ] **Dependencies**: Does it pull in a heavy or controversial dependency tree?
- [ ] **Documentation**: README, examples, or docs — or is it just code?
- [ ] **Python-specific**: PyPI version matches repo version? No build steps required?
- [ ] **JS-specific**: Published to npm? ESM/CJS compatible?

## Ask before committing to a path

Forking, taking on a dependency, and contributing upstream all have
different long-term costs (maintenance burden, control, review latency).
Present the candidates and the recommended option to the user rather than
picking silently — this is a decision for the user to make.

## Exception

If the user has already specified the approach ("build this from
scratch", "fork X and add Y"), skip the search-and-decide ritual and do
what was asked — this skill is for the ambiguous "build me X" case, not
for overriding an explicit choice.

## Related skills

- `silent-mode`: when working silently, do the search silently and
  present the findings and recommendation as a single design question.
- `frugal-context`: when exploring candidate repos, use the search funnel
  — grep for what you need before reading entire files.
- `lean-output`: cap search result descriptions; only stars, last commit,
  language, and a one-line summary per candidate are needed.
- `github-actions`: when the thing to build is CI or other automation,
  look for an existing action here first, then hand the workflow itself
  to that skill.
- `github-docs`: when the decision is to contribute upstream, it writes
  the PR description for maintainers who have no context.
