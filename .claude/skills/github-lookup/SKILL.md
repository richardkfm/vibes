---
name: github-lookup
description: Before starting a new project or major feature from scratch, search GitHub for existing repos that already solve it, then decide whether to depend on one, fork it, inline pieces of its code, or skip building entirely and contribute upstream instead. Use when the user invokes /github-lookup, proposes building a new tool/library/project, or asks whether something already exists for a use case.
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
gh search repos "<concept>" --language=python --sort=stars

# Web search for broader coverage
# "python library <concept>"
# "open source <concept>"
# "<concept> alternative"
# "best <concept> library 2025"
```

For each candidate, note in one line: stars/last-commit (maintenance
signal), license, language, and a rough % match to the use case.

## Decision framework

Match quality drives the decision — cheapest option first:

1. **~90%+ match, actively maintained** → Don't build a competing project.
   The right move is usually to *use* it as a dependency, or — if it's
   missing the last 10% — open an issue or PR against the upstream
   maintainer rather than forking a parallel copy. Recommend this to the
   user explicitly; it's the option most tempting to skip because building
   feels more productive than asking.

2. **Partial match (rough fit, missing pieces, license permits)** →
   Fork it and build the delta on top, or vendor/inline the specific
   files/functions that fit rather than reimplementing them. Inlining
   saves the tokens of re-deriving working code; forking saves them at
   project scale instead of function scale.

3. **No good match, or license/maintenance disqualifies every candidate** →
   Build from scratch. State why in one line (e.g. "closest match is
   unmaintained since 2019, license is unclear") so the decision is
   recorded, not silently skipped.

## License check (mandatory before fork or inline)

- **Permissive** (MIT, Apache-2.0, BSD) → safe to inline/fork with attribution
  (keep the license file, credit the source in the commit/PR).
- **Copyleft** (GPL, AGPL) → inlining can obligate your project's license;
  **flag this to the user** before proceeding, don't decide unilaterally.
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

## Combining with other skills

- **silent-mode**: if you're working silently, do the search silently and
  include your findings and recommendation as a single design question.
- **frugal-context**: when exploring candidate repos, use the search funnel
  — grep for what you need before reading entire files.
- **lean-output**: cap search result descriptions; you only need
  stars, last commit, language, and a one-line summary per candidate.
