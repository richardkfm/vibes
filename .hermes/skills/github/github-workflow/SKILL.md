---
name: github-workflow
description: Authenticate with GitHub (fine-grained PAT workaround), create draft PRs, and avoid user-guides as agent skills.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Authentication, PAT, Draft, PR, Workflow]
    related_skills: [github-auth, github-pr-workflow]
---

# GitHub Workflow

Extends the bundled `github-auth` and `github-pr-workflow` skills with user-specific conventions and discovered workarounds.

## Target Repository Selection (run first)

**Before any other GitHub work, determine which repository to operate on.** Unlike Claude Code (which has a project directory pinned at session start), Hermes sessions have no default repo — the user may have multiple repos cloned locally or on GitHub.

### Trigger

Run this check at the beginning of a session whenever the user's request involves GitHub operations (PRs, commits, clones, branches, issues, etc.).

### Procedure

1. **Check if the user already specified a repo** — scan the user's initial message for:
   - An explicit repo name (`"in my project-x repo"`, `"on the vibes repo"`)
   - A full URL (`github.com/user/repo`)
   - A clear project reference that maps to one repo

2. **If clearly stated:** note the repo and proceed to the next section.

3. **If ambiguous or missing:** use `clarify` to ask:
   ```
   clarify(question="Which repository should I work in?", choices=[list of known repos])
   ```
   To build the choices, discover repos:
   ```bash
   # Check locally cloned repos under common paths
   find ~ -maxdepth 3 -name ".git" -type d 2>/dev/null | while read gitdir; do
     cd "$gitdir/.." 2>/dev/null && git remote get-url origin 2>/dev/null
   done | sort -u

   # OR list repos via GitHub API (if gh is authed)
   gh repo list --limit 20 2>/dev/null || echo "gh not available"
   ```
   Present the most relevant options (recently worked-on repos, or ones matching the task). If only 1 repo exists, default to it and confirm briefly.

### After selection

Record the choice and work inside that repository:
```bash
cd /path/to/selected/repo
git fetch origin
```

If the repo isn't cloned locally yet, clone it first:
```bash
gh repo clone owner/repo  # or: git clone https://github.com/owner/repo.git
```

### Example

- User says: "can you make a PR to fix that auth bug?"
  → No repo specified → `clarify("Which repository should I work in?", choices=["vibes", "project-x", "api-server"])`
- User says: "open a PR in vibes to update the README"
  → Repo is clear → proceed to authentication and work in the `vibes` repo

## Create Draft PRs Only

**ALWAYS create PRs as drafts — never merge without explicit instruction.** Richard prefers to review PRs himself before merging. This prevents accidental merges and gives the user full control.

### Creating a Draft PR

**With gh:**
```bash
gh pr create \
  --draft \
  --title "feat: description of changes" \
  --body "## Summary\nDescription of changes.\n"
```

**Via API (curl):**
```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{\"title\":\"feat: description\",\"body\":\"...\",\"head\":\"$BRANCH\",\"base\":\"main\",\"draft\":true}"
```

### After creating the draft PR

Tell the user:
- PR number and URL
- That it's a draft and ready for their review
- They can merge it when satisfied

Do **not** call `gh pr merge` or the merge API under any circumstances unless the user explicitly says "merge this PR myself" — even then, prefer to let them do it.

## Authentication with Fine-Grained PATs

Fine-grained PATs (`github_pat_...`) fail with `missing required scope 'read:org'`. Workaround:

```bash
# Write token directly to gh config
python3 -c "
import pathlib
hosts = pathlib.Path('$HOME/.config/gh/hosts.yml')
# Backup
pathlib.Path('$HOME/.config/gh/hosts.yml.bak').write_text(hosts.read_text())
hosts.write_text(f'''github.com:
    users:
        <USER>:
            oauth_token: <TOKEN>
    git_protocol: https
    oauth_token: <TOKEN>
    user: <USER>
''')
"

# Also set env var as fallback
export GH_TOKEN="<TOKEN>"

# Store for git credential helper
echo "https://<USER>:<TOKEN>@github.com" > ~/.git-credentials

gh auth status
```

## What Makes an Agent Skill (vs. User Guide)

A Hermes skill must be **procedural** — it tells the agent *what to do* in numbered steps with checkable completion criteria. It is NOT valid as a Hermes skill if it is:
- A user-facing installation tutorial
- A CLI flag reference (e.g. `llama-server --ctx-size`)
- Empty Python class stubs with no working code
- A "how to set up X on your hardware" guide

**Valid agent skills** have: trigger conditions, procedural steps, tool commands, pitfalls, and verification. See `hermes-agent-skill-authoring` for the full spec.
