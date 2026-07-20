---
name: github-workflow
description: Authenticate with GitHub from Hermes, work within local Qwen model constraints, and create draft PRs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Authentication, PR, Draft, Qwen, Local, Workflow]
    related_skills: [github-auth, github-pr-workflow]
---

# GitHub Workflow for Hermes Agents

Authenticate with GitHub, work efficiently with local Qwen models, and commit changes as draft PRs for human review.

## 1. GitHub Authentication

### Detect current auth state

```bash
gh auth status 2>/dev/null || echo "gh not authenticated"
```

### Token sources (check in this order)

1. `GH_TOKEN` environment variable
2. `~/.git-credentials` — extract with: `grep "github.com" ~/.git-credentials | head -1 | awk -F'://' '{print $2}' | awk -F'@' '{print $1}'`
3. `~/.config/gh/hosts.yml` — extract with: `grep "oauth_token:" ~/.config/gh/hosts.yml | tail -1 | awk '{print $2}'`
4. `~/.hermes/.env` — if it contains `GITHUB_TOKEN=`

### Re-authenticate when user provides a new token

```bash
# Auth gh CLI
echo "<TOKEN>" | gh auth login --with-token

# Set git credentials
gh auth setup-git
git config --global credential.helper store

# Also store for git fallback
echo "https://<USERNAME>:<TOKEN>@github.com" > ~/.git-credentials

# Verify
gh auth status
```

**Pitfall:** Fine-grained PATs (`github_pat_...`) may be missing `read:org` scope — `gh` will still auth even with the warning. Classic PATs (`ghp_...`) need `repo` scope for write access.

**Pitfall:** If `gh auth login --with-token` fails with `missing required scope 'read:org'`, write the token directly to `~/.config/gh/hosts.yml` and `~/.git-credentials` instead. Alternatively, set `export GH_TOKEN="<TOKEN>"` — `gh` will use the env var.

## 2. Working with Local Qwen Models

Local Qwen models (especially 30B) are context-sensitive and slow. Optimize your interactions:

### Context budgeting

- **Default context:** 8192 is available, but stay under 6000 per message for speed
- **Read files selectively:** Use `read_file` with small `limit` instead of dumping entire files
- **Search before reading:** Use `search_file` or `grep` before reading to avoid loading irrelevant code
- **Batch tool calls:** Run independent tool calls in parallel when possible

### Prompt efficiency

- Keep instructions concise — include only what's needed
- Avoid restating context you already shared
- Use `execute_code` for programmatic work instead of verbose terminal steps
- For `read_file`, use `offset` and `limit` to read only relevant sections

### When context is running low

- Use `frugal-context` techniques: search, grep, read slices
- Summarize prior work in a compact commit message rather than repeating it
- If you need to re-read a file you just changed, use `git diff` — it's smaller than the full file

## 3. Commit and Draft PR Workflow

**Always create a draft PR unless explicitly told to merge.** The user reviews and merges.

### Step-by-step

```bash
# 1. Start from the correct base branch
git checkout main && git pull origin main

# 2. Create a feature branch
git checkout -b feature/<short-description>

# 3. Make changes (use your file tools)

# 4. Stage and commit with conventional commit message
git add -A
git commit -m "feat: short description

What changed and why."

# 5. Push the branch
git push -u origin HEAD

# 6. Create a DRAFT PR
gh pr create \
  --draft \
  --title "feat: short description" \
  --body "What this PR does and why.
- Bullet of changes"
```

### Commit message conventions

| Type | When |
|------|------|
| `feat:` | New feature or functionality |
| `fix:` | Bug fix |
| `refactor:` | Code restructuring without behavior change |
| `docs:` | Documentation changes |
| `chore:` | Maintenance, config, dependencies |
| `test:` | Adding or modifying tests |

### PR body template

```
[Summary line of what changed]

- Specific change 1 and why
- Specific change 2

[Any notes for the reviewer]
```

### When you need to update an already-created PR

```bash
# Make more changes...
git add -A
git commit -m "type: follow-up change"
git push
# The existing PR updates automatically — no new PR needed
```

### Never merge without explicit instruction

- **Default:** Always create as `--draft`
- **Merging:** Only if the user explicitly says "merge the PR" or "squash merge"
- **When merging:** `gh pr merge --squash --delete-branch <PR_NUMBER>`

## Complete Example

```bash
# Check auth
gh auth status || { echo "Not authenticated"; }

# Work on a repo
cd /path/to/repo

# Branch and change
git checkout -b feature/add-login-flow
# ... make changes with file tools ...

# Commit and draft PR
git add -A
git commit -m "feat: add login flow

User can now login with email/password and receives a JWT."
git push -u origin HEAD

gh pr create \
  --draft \
  --title "feat: add login flow" \
  --body "User can now login with email/password and receives a JWT."
```
