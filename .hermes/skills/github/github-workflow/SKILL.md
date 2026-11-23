---
name: github-workflow
description: "Use before any PR, push, clone or gh auth. Draft PRs only."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Authentication, PAT, Draft, PR, Workflow]
    related_skills: [github, github-repo-finder, github-docs]
---

# GitHub Workflow

The user's conventions for GitHub work, on top of the bundled `github` skill (`github-auth` and `github-pr-workflow` on older installs), which covers the mechanics. Three things are fixed here: settle the repository before anything else, open pull requests as drafts and never merge without an explicit instruction, and authenticate `gh` with a personal access token without leaving that token in chat or in `~/.git-credentials`.

## When to Use

- The request touches GitHub in any way: pull requests, commits, pushes, clones, branches, issues.
- A pull request is about to be created, updated or merged.
- `gh auth status` fails, or `gh auth login --with-token` rejects a token with `missing required scope 'read:org'`.

## Prerequisites

`git` and `gh` on the PATH. Run every command below through the `terminal` tool.

## Target Repository Selection (run first)

Decide which repository to work in before any other GitHub step. A Hermes session has no project directory pinned at start and the user may have several repos, locally or on GitHub, so a guess can put commits or a pull request in the wrong one.

1. **Look for a repo in the user's message**: an explicit name ("in my project-x repo", "on the vibes repo"), a URL (`github.com/user/repo`), or a project reference that maps to exactly one repo. If it is there, note it and go to step 3.

2. **Otherwise ask.** Collect the candidates:
   ```bash
   # repos cloned under the home directory
   find ~ -maxdepth 3 -name .git -type d 2>/dev/null | while read -r gitdir; do
     git -C "${gitdir%/.git}" remote get-url origin 2>/dev/null
   done | sort -u

   # or the user's repos on GitHub, when gh is authenticated
   gh repo list --limit 20
   ```
   Then ask with `clarify`: the question "Which repository should I work in?" with up to four choices, most likely first (recently worked on, or matching the task). The tool adds a free-text row for anything else. If only one repo exists, default to it and confirm in one line.

3. **Work inside the selected repo**, cloning it first if it is not on disk:
   ```bash
   gh repo clone owner/repo        # only when not cloned yet; or: git clone https://github.com/owner/repo.git
   cd /path/to/selected/repo
   git fetch origin
   ```

Examples:

- "can you make a PR to fix that auth bug?" names no repo, so ask: `clarify` with the choices `vibes`, `project-x`, `api-server`.
- "open a PR in vibes to update the README" names the repo, so go straight to work in `vibes`.

## Create Draft PRs Only

Open every pull request as a draft, and do not merge one unless the user explicitly tells you to merge that pull request. The user reviews pull requests themselves before anything merges; a draft cannot be merged by accident and keeps that decision with them.

```bash
gh pr create --draft --title "feat: <what changed>" --body-file pr-body.md
```

Write the body to a file with `write_file` first (the `github-docs` skill, if installed, says what belongs in it). An inline `--body "## Summary\n..."` posts the `\n` literally, because the shell does not expand it inside double quotes.

Without `gh`, create the pull request through the REST API (`POST /repos/{owner}/{repo}/pulls`) with `"draft": true` in the JSON body, and use the repository's default branch as `base` instead of assuming `main`.

After creating it, tell the user:

- the PR number and URL
- that it is a draft, waiting for their review
- that they can mark it ready and merge it when satisfied

Never run `gh pr merge` (with or without `--auto`), call the merge API, or take the pull request out of draft with `gh pr ready` unless the user explicitly asks for that on this pull request. Even with permission to merge, offer to leave the merge to them.

## Authentication with Fine-Grained PATs

Only needed when `gh auth status` fails. If it reports a logged-in account, skip this section.

`gh auth login --with-token` checks a token for the classic scopes `repo` and `read:org` and can reject a personal access token with `error validating token: missing required scope 'read:org'`. A fine-grained PAT (`github_pat_...`) has no classic scopes to add, so when that happens the token has to reach `gh` another way. Whether the check fires depends on the token and the `gh` version, so try the normal login before the fallback. In both cases keep the token out of chat, off command lines and out of `~/.git-credentials`.

1. **Have the user put the token in a file, not in chat.** A token pasted into chat stays in the session log and reaches the model provider. Ask them to run this in their own shell on this machine, paste the token, press Enter, then Ctrl-D:
   ```bash
   (umask 077; cat > ~/.gh-pat)
   ```
   Never print that file or the token. If the user pastes the token into chat anyway, save it to `~/.gh-pat` with `write_file`, restrict that file to mode 600, do not repeat the token in any reply, and mention that it now sits in the session history in case they want to rotate it.

2. **Try the supported login first**, because it stores the token in the operating system's keyring when there is one:
   ```bash
   gh auth login --with-token < ~/.gh-pat
   ```
   If it succeeds, go to step 4. A `401` or `Bad credentials` means the token is wrong or expired; ask for a new one instead of continuing.

3. **On the scope error, write the file `gh` itself falls back to** when no keyring exists. Replace `GITHUB_LOGIN` with the user's GitHub login; ask for it if unknown.
   ```bash
   python3 - GITHUB_LOGIN <<'PY'
   import os, pathlib, re, sys
   home = pathlib.Path.home()
   token = (home / ".gh-pat").read_text().strip()
   user = sys.argv[1]
   cfg = os.getenv("GH_CONFIG_DIR") or pathlib.Path(os.getenv("XDG_CONFIG_HOME") or home / ".config") / "gh"
   hosts = pathlib.Path(cfg) / "hosts.yml"
   hosts.parent.mkdir(parents=True, exist_ok=True)
   old = hosts.read_text() if hosts.exists() else ""
   # keep entries for other hosts, replace a stale github.com entry
   kept = re.sub(r"(?m)^github\.com:\n(?:[ \t].*\n?)*", "", old).strip("\n")
   hosts.touch(mode=0o600)
   hosts.chmod(0o600)
   hosts.write_text((kept + "\n" if kept else "") +
       f"github.com:\n    users:\n        {user}:\n            oauth_token: {token}\n"
       f"    git_protocol: https\n    oauth_token: {token}\n    user: {user}\n")
   PY
   ```

4. **Let git use gh's credential, then remove the temporary file:**
   ```bash
   gh auth setup-git     # adds credential-helper lines to ~/.gitconfig; no token is written
   rm -f ~/.gh-pat
   gh auth status        # names the account and where its token is stored
   ```

5. **Tell the user where the token now lives**, as `gh auth status` reports it:

   | `gh auth status` shows | The token is stored in |
   |---|---|
   | `(keyring)` | the operating system's credential store |
   | a path ending in `hosts.yml` | that file, in plaintext. Mode 600 keeps other accounts out; anything running as the user, this agent included, can read it. |

   Nothing else holds it. `gh auth setup-git` makes git ask `gh` for the credential on every fetch and push, so `~/.git-credentials`, remote URLs and shell profiles stay free of tokens.

## Pitfalls

- **A token exported in Hermes's own environment may not reach `gh`.** Hermes can strip GitHub tokens from the environment of `terminal` commands, so trust `gh auth status`, not the presence of `GH_TOKEN` elsewhere.
- **`GH_TOKEN` or `GITHUB_TOKEN` set inside the shell overrides stored credentials**, and `gh auth login` refuses to store a token while one is set. If `gh auth status` passes that way, there is nothing to set up.
- **A fine-grained PAT only reaches the repositories and permissions picked when it was created.** A 403 or 404 such as `Resource not accessible by personal access token` on a repo the user can open in the browser is the token's reach, not a login failure. Ask the user to grant that repository (pull requests need read and write on Contents and on Pull requests) instead of authenticating again.
- **An SSH remote ignores all of this.** If `git remote get-url origin` starts with `git@`, pushes use SSH keys, not the token.
- **Step 2 hanging with no output** happens on headless Linux hosts without a keyring. Interrupt it and continue with step 3.
- **Old plaintext copies outlive a new login.** A `https://user:token@github.com` line in `~/.git-credentials`, or a `hosts.yml.bak` next to `hosts.yml`, keeps a token readable. Point it out and offer to remove it once `gh auth status` passes.
- **The paths here are for Linux and macOS.** On Windows `gh` uses the Windows credential manager, so step 2 is normally enough.

## Verification

- `git remote get-url origin` in the working directory names the repository the user chose.
- `gh auth status` exits 0 and names the account.
- `gh pr view --json number,url,isDraft,state` shows `"isDraft": true` and `"state": "OPEN"` for the pull request just created.
