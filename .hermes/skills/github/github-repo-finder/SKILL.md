---
name: github-repo-finder
description: "Use before building something new: find repos to reuse."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Search, Repository, Fork, Code Reuse, Planning]
    related_skills: [github-workflow, github]
---

# GitHub Repo Finder

Before a new project or large feature gets built, search GitHub for repositories that already solve it and recommend one of five outcomes: depend, contribute upstream, fork, inline, or build. A search costs minutes; a parallel implementation costs the build plus its upkeep. This skill researches and recommends. The user picks the path.

## When to Use

- The user asks to build a new tool, library, service, bot or other project from scratch.
- The user asks whether something already exists, which library to use, or for alternatives to a package.
- A plan is about to include a sizeable component that is probably a solved problem.

Skip it for small self-contained changes (a bugfix, a one-off script, a function inside an existing codebase), and when the user has already named the approach ("build this from scratch", "fork X and add Y").

## Prerequisites

`gh` on the PATH and authenticated (`gh auth status`); if it is not, load `github-workflow`. Without `gh`, run the same queries with `web_search`. Run every command below through the `terminal` tool.

## Procedure

1. **Name the concept.** Write the need as one sentence, then list two or three synonyms and adjacent terms (the problem's usual name, framework names).

2. **Search** with two to four queries, with and without a language filter:
   ```bash
   gh search repos "<concept>" --sort=stars --limit=10 --archived=false \
     --json fullName,description,stargazersCount,pushedAt,license,language
   gh search repos "<synonym>" --language=python --sort=stars --limit=10
   ```
   Add `web_search` for projects that GitHub search ranks poorly: "open source <concept>", "<concept> alternative".

3. **Shortlist up to five candidates** and pull the signals for each:
   ```bash
   gh repo view owner/repo --json nameWithOwner,description,stargazerCount,pushedAt,isArchived,licenseInfo,latestRelease
   gh run list -R owner/repo --limit 5      # is CI passing on recent commits?
   ```

4. **Vet each candidate.** Note one line per repo:
   - Maintenance: pushed within about six months, a recent release, not archived.
   - Adoption: stars show that someone else relies on it. A signal, not proof.
   - Responsiveness: maintainers answer issues and review pull requests.
   - Build health: CI passes. Broken tests suggest abandonment.
   - Dependencies: no heavy or contested dependency tree.
   - Documentation: a README with examples, not code alone.
   - Fit: a rough percentage match to the need.

5. **Check the license before recommending fork or inline**, because it decides whether copying is allowed at all:

   | License | Meaning |
   |---|---|
   | Permissive (MIT, Apache-2.0, BSD) | Fork or inline with attribution: keep the license file and credit the source in the commit or pull request. |
   | Copyleft (GPL, AGPL) | Can force the same license onto the user's project. Flag it to the user before going further. |
   | No license file | No permission granted. Use the repo as a reference only. |
   | Several licenses in one repo | Check the license of the specific files to be used, not only the top-level one. |

6. **Decide.** Match quality drives the outcome, cheapest first:

   | Match | Outcome |
   |---|---|
   | About 90% or better, actively maintained | **Depend** on it. If the last 10% is missing, **contribute upstream** (an issue or pull request to the maintainer) rather than forking a parallel copy. Recommend this explicitly: it is the option most tempting to skip, because building feels more productive than asking. |
   | Partial: a rough fit with missing pieces, license permits | **Fork** and build the delta when most of the repo is wanted. **Inline** (vendor) the specific files or functions when only a part is. |
   | No good match, or license or maintenance rules out every candidate | **Build** from scratch, and state why in one line so the decision is on record. |

7. **Present the shortlist and one recommendation, then ask.** The paths differ in long-term cost (maintenance, control, review latency), so the choice belongs to the user. Example:

   ```
   acme/feedparse   4.1k stars   pushed last month   MIT   ~90% fit, no Atom 0.3
   oldfeed/reader   900 stars    archived            GPL-3.0   ~60% fit

   Recommendation: depend on acme/feedparse and open an upstream issue for Atom 0.3.
   A fork is not worth maintaining for one format.
   ```
   Ask with `clarify`, recommended path first and at most four choices.

8. **Act on the answer:**

   | Outcome | Next step |
   |---|---|
   | Depend | Add it with the project's package manager and pin the version. |
   | Contribute upstream | Open an issue there first; for a pull request follow `github-workflow` (draft, never merged by the agent). |
   | Fork | `gh repo fork owner/repo --clone`, then build the delta on a branch. |
   | Inline | `gh repo clone owner/repo vendor-src -- --depth=1`, copy only the files needed, keep their license header, and record the source repo and commit next to them. |
   | Build | Record the one-line reason, then start. |

## Pitfalls

- **No results is not proof of absence.** Broaden the terms, drop the language filter and try the problem's other names before concluding nothing exists.
- **Stars measure popularity, not upkeep.** A repo with thousands of stars that is archived or untouched for years is a fork or inline candidate at best. Read `pushedAt` and `isArchived`.
- **Forks are left out of search results by default.** The live successor of a dead project is often a fork; add `--include-forks=true` when the top hit looks abandoned.
- **A sound but unmaintained repo** can still serve as a fork base or a source to inline if the license allows. Say plainly that the user would own its maintenance.

## Verification

- The user saw the shortlist (stars, last push, license and fit for each candidate) and one recommendation with its reason.
- The license of the chosen repo was checked before anything was forked or copied.
- The user chose the path. For **build**, the one-line reason is on record.
