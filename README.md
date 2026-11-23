<h1 align="center">
  <img src="assets/hero.svg" alt="vibes. Skills for coding agents: lean context, quiet sessions, careful shipping." width="100%">
</h1>

A collection of agent skills for long or autonomous coding sessions. They keep the context window small and the chat quiet, and they make sure that what an agent publishes (pull requests, releases, issue comments) says clearly what changed and who wrote it.

Each skill is a self-contained `SKILL.md` in the [Agent Skills](https://agentskills.io) format. They work in Claude Code, the Claude apps, Hermes Agent, and any other agent that reads skill files. Use whichever ones you need.

<p align="center">
  <img src="assets/skills-flow.svg" alt="How the skills fit into one long agent session: github-lookup before building, repo-map and frugal-context to get oriented, lean-output, radical-compression and checkpoint in every work cycle, then github-actions, github-docs, github-releases and linear-issues when shipping. silent-mode spans the whole session." width="100%">
</p>

## Skills

### Long sessions

| Skill | What it does |
|---|---|
| [`silent-mode`](.claude/skills/silent-mode/SKILL.md) | Work quietly: no play-by-play narration, only questions on important decisions and one final summary. |
| [`lean-output`](.claude/skills/lean-output/SKILL.md) | Keep tool output small: quiet flags, capped output, verbose logs routed to files and grepped instead of dumped. |
| [`frugal-context`](.claude/skills/frugal-context/SKILL.md) | Search and read the codebase economically: grep before reading, read slices instead of whole files, never re-read what is already in context. |
| [`checkpoint`](.claude/skills/checkpoint/SKILL.md) | Maintain a compact running state file during long autonomous tasks so context compaction doesn't force expensive re-exploration. |
| [`radical-compression`](.claude/skills/radical-compression/SKILL.md) | Compress after each cycle of work: distill the cycle into a few lines, drop everything else, and keep long sessions tight. |
| [`repo-map`](.claude/skills/repo-map/SKILL.md) | Build and maintain a cached, annotated map of a big repository so navigating it costs one small read instead of a fresh exploration every session. |

### GitHub

| Skill | What it does |
|---|---|
| [`github-lookup`](.claude/skills/github-lookup/SKILL.md) | Before building a new project or feature from scratch, search GitHub for existing repos that already solve it, then decide whether to depend, fork, inline, or contribute upstream. |
| [`github-actions`](.claude/skills/github-actions/SKILL.md) | Write and debug GitHub Actions workflows: start from how the repo already builds, keep permissions minimal, pin actions to commit SHAs, validate before pushing, then watch the run. |
| [`github-docs`](.claude/skills/github-docs/SKILL.md) | Document a change where its readers will look, scaled to its blast radius: the README in a solo repo, the PR description in a team repo, with migration and rollback notes when a change is wide. |
| [`github-releases`](.claude/skills/github-releases/SKILL.md) | Cut a release: work out the next version, tag the right commit, and publish release notes people can act on. Confirms before the irreversible public steps. |

### Linear

| Skill | What it does |
|---|---|
| [`linear-issues`](.claude/skills/linear-issues/SKILL.md) | Work Linear issues and comment in short plain language, wrapped in quotation marks with an `— agent` tag, so teammates always know an agent wrote it. |

### Writing, design and building

| Skill | What it does |
|---|---|
| [`humanize-language`](.claude/skills/humanize-language/SKILL.md) | Rewrite text so it reads like a person wrote it: strip AI tells, formulaic structure, hedging, and marketing sheen while keeping the meaning intact. |
| [`web-ux-design`](.claude/skills/web-ux-design/SKILL.md) | Audit and improve the UX and visual design of web pages and apps: hierarchy, spacing, typography, color, states, forms, responsiveness, and accessibility. |
| [`prompt-to-code`](.claude/skills/prompt-to-code/SKILL.md) | Transform a system prompt into working code: deterministic rules become schemas, tools, guards, and orchestration, and only genuine judgment stays in a much smaller prompt. |

## Hermes skills

Written for Hermes Agent and its tools:

| Skill | What it does |
|---|---|
| [`github-repo-finder`](.hermes/skills/github/github-repo-finder/SKILL.md) | Search GitHub for existing repositories with similar concepts to avoid duplication and enable forking. |
| [`github-workflow`](.hermes/skills/github/github-workflow/SKILL.md) | Repository selection, PAT authentication, and PR workflow conventions for Hermes: finds which repo to work in and creates draft PRs only. |

Four of the skills above are also kept in the Hermes layout, with Hermes frontmatter and the same instructions: [`github-actions`](.hermes/skills/github/github-actions/SKILL.md), [`github-docs`](.hermes/skills/github/github-docs/SKILL.md), [`github-releases`](.hermes/skills/github/github-releases/SKILL.md) and [`linear-issues`](.hermes/skills/productivity/linear-issues/SKILL.md). These copies are generated from `.claude/skills`; see [Maintaining](#maintaining).

## Installation

All examples start from a clone:

```bash
git clone --depth 1 https://github.com/richardkfm/vibes /tmp/vibes-skills
```

### Claude Code

For one project:

```bash
mkdir -p .claude/skills
cp -r /tmp/vibes-skills/.claude/skills/* .claude/skills/
```

For all your projects:

```bash
mkdir -p ~/.claude/skills
cp -r /tmp/vibes-skills/.claude/skills/* ~/.claude/skills/
```

### Claude apps

Each [release](https://github.com/richardkfm/vibes/releases/latest) attaches one zip per skill. Download the ones you want and upload them where you manage skills in Claude's settings.

### Hermes Agent

```bash
mkdir -p ~/.hermes/skills
cd /tmp/vibes-skills
# Hermes-layout skills, grouped by category
cp -r .hermes/skills/* ~/.hermes/skills/
# The rest are agent-agnostic; skip the four already copied above
for dir in .claude/skills/*/; do
  name=$(basename "$dir")
  ls -d .hermes/skills/*/"$name" >/dev/null 2>&1 || cp -r "$dir" ~/.hermes/skills/
done
```

Hermes picks up skills from `~/.hermes/skills/` automatically. You can also place them in a project's `.hermes/skills/` for repo-scoped availability.

### Any other agent

The skills follow the standard format: a YAML frontmatter block with `name` and `description`, then a Markdown body. Copy the folders from `.claude/skills/` into whatever skills directory your agent reads.

## Maintaining

`.claude/skills/` is the source of truth. After editing a skill, run the same two checks CI runs on every pull request:

```bash
pip install pyyaml
python3 scripts/validate_skills.py        # spec limits, links, cross-references, README entries
python3 scripts/sync_hermes_skills.py     # regenerate the Hermes copies
```

The validator keeps frontmatter to the fields every agent accepts (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`), so a skill that passes can be uploaded anywhere. To mirror another skill into the Hermes layout, add it to `MIRRORS` in `scripts/sync_hermes_skills.py`.

To publish a release, tag a commit on `main` and push the tag:

```bash
git switch main && git pull
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

The release workflow validates the skills, refuses a tag that is not on `main`, zips each skill, and publishes a GitHub release with generated notes. Edit the notes afterwards if the list of merged pull requests needs a summary on top. A tag with a suffix, such as `v0.1.0-rc.1`, is published as a pre-release.

The workflows pin every action to a commit SHA; Dependabot opens a pull request when a newer version is out.

## License

MIT. See [LICENSE](LICENSE).
