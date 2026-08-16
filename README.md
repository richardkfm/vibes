# vibes 🌈

A small collection of agent skills for working leaner and quieter in long or autonomous sessions. Compatible with Claude Code, Hermes Agent, and any tool-augmented AI assistant that supports skill files.

## Claude Skills

| Skill | What it does |
|---|---|
| [`silent-mode`](.claude/skills/silent-mode/SKILL.md) | Work quietly — no play-by-play narration, just questions on important decisions and one final summary. |
| [`lean-output`](.claude/skills/lean-output/SKILL.md) | Keep tool output small: quiet flags, capped output, verbose logs routed to files and grepped instead of dumped. |
| [`frugal-context`](.claude/skills/frugal-context/SKILL.md) | Search and read the codebase economically — grep before reading, read slices instead of whole files, never re-read what's already in context. |
| [`checkpoint`](.claude/skills/checkpoint/SKILL.md) | Maintain a compact running state file during long autonomous tasks so context compaction doesn't force expensive re-exploration. |
| [`radical-compression`](.claude/skills/radical-compression/SKILL.md) | Radically compress after each cycle of work — distill the cycle into a few lines, drop everything else, and keep long sessions tight. |
| [`repo-map`](.claude/skills/repo-map/SKILL.md) | Build and maintain a cached, annotated map of a big repository so navigating it costs one small read instead of a fresh exploration every session. |
| [`github-lookup`](.claude/skills/github-lookup/SKILL.md) | Before building a new project or feature from scratch, search GitHub for existing repos that already solve it, then decide whether to depend, fork, inline, or contribute upstream. |
| [`humanize-language`](.claude/skills/humanize-language/SKILL.md) | Rewrite text so it reads like a person wrote it — strip AI tells, formulaic structure, hedging, and marketing sheen while keeping the meaning intact. |
| [`web-ux-design`](.claude/skills/web-ux-design/SKILL.md) | Audit and improve the UX and visual design of web pages and apps — hierarchy, spacing, typography, color, states, forms, responsiveness, and accessibility. |
| [`prompt-to-code`](.claude/skills/prompt-to-code/SKILL.md) | Transform a system prompt into working code — deterministic rules become schemas, tools, guards, and orchestration; only genuine judgment stays in a much smaller prompt. |

## Hermes Skills

| Skill | What it does |
|---|---|
| [`github-repo-finder`](.hermes/skills/github/github-repo-finder/SKILL.md) | Search GitHub for existing repositories with similar concepts to avoid duplication and enable forking. |
| [`github-workflow`](.hermes/skills/github/github-workflow/SKILL.md) | Repository selection, PAT authentication, and PR workflow conventions for Hermes — auto-discovers which repo to work in and creates draft PRs. |

Each skill is self-contained and independent — use whichever ones you need.

## Installation

### Claude Code CLI

```bash
mkdir -p .claude/skills
git clone --depth 1 https://github.com/richardkfm/vibes /tmp/vibes-skills
cp -r /tmp/vibes-skills/.claude/skills/* .claude/skills/
rm -rf /tmp/vibes-skills
```

Or for a global install across all projects:
```bash
mkdir -p ~/.claude/skills
cp -r /tmp/vibes-skills/.claude/skills/* ~/.claude/skills/
```

### Hermes Agent

```bash
mkdir -p ~/.hermes/skills
git clone --depth 1 https://github.com/richardkfm/vibes /tmp/vibes-skills
cp -r /tmp/vibes-skills/.claude/skills/* ~/.hermes/skills/
rm -rf /tmp/vibes-skills
```

Hermes picks up skills from `~/.hermes/skills/` automatically. You can also
place them in a project's `.hermes/skills/` for repo-scoped availability.

### Any agent that supports SKILL.md

These skills follow the standard SKILL.md format: a YAML frontmatter block
with `name` and `description`, followed by markdown body. Place them in
whatever skills directory your agent uses.

## License

MIT — see [LICENSE](LICENSE).
