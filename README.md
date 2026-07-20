# vibes 🌈

This is a repository for the vibes project.

## Skills

| Skill | What it does |
|---|---|
| [`silent-mode`](.claude/skills/silent-mode/SKILL.md) | Work quietly — no play-by-play narration, just questions on important decisions and one final summary. |
| [`lean-output`](.claude/skills/lean-output/SKILL.md) | Keep tool output small: quiet flags, capped output, verbose logs routed to a file and grepped instead of dumped into context. |
| [`frugal-context`](.claude/skills/frugal-context/SKILL.md) | Search and read the codebase economically — grep before reading, read slices instead of whole files, never re-read what's already in context. |
| [`checkpoint`](.claude/skills/checkpoint/SKILL.md) | Maintain a compact running state file during long autonomous tasks so context compaction doesn't force expensive re-exploration. |
| [`radical-compression`](.claude/skills/radical-compression/SKILL.md) | Radically compress after each cycle of work — distill the cycle into a few lines, drop everything else, and keep long sessions tight. |
| [`repo-map`](.claude/skills/repo-map/SKILL.md) | Build and maintain a cached, annotated map of a big repository so navigating it costs one small read instead of a fresh exploration every session. |
| [`github-lookup`](.claude/skills/github-lookup/SKILL.md) | Before building a new project or feature from scratch, search GitHub for existing repos that already solve it, then decide whether to depend on one, fork it, inline some of its code, or contribute upstream instead of building at all. |
| [`humanize-language`](.claude/skills/humanize-language/SKILL.md) | Rewrite text so it reads like a person wrote it — strip AI tells, formulaic structure, hedging, and marketing sheen while keeping the meaning intact. |
| [`web-ux-design`](.claude/skills/web-ux-design/SKILL.md) | Audit and improve the UX and visual design of web pages and apps — hierarchy, spacing, typography, color, states, forms, responsiveness, and accessibility. |
| [`prompt-to-code`](.claude/skills/prompt-to-code/SKILL.md) | Transform a system prompt into working code — deterministic rules become schemas, tools, guards, and orchestration; only genuine judgment stays in a much smaller prompt. |

Each skill is a self-contained `SKILL.md` under `.claude/skills/<name>/` and
can be used independently — invoke by name (`/lean-output`) or let Claude
pick it up automatically when its description matches what you're asking for.

## Adding these skills to your own project

### Claude Code CLI (or IDE extension)

Copy the skill folder(s) you want into your project's `.claude/skills/`
directory:

```bash
# from inside your project
mkdir -p .claude/skills
git clone --depth 1 https://github.com/richardkfm/vibes /tmp/vibes-skills
cp -r /tmp/vibes-skills/.claude/skills/<skill-name> .claude/skills/
rm -rf /tmp/vibes-skills
```

Or copy just the skills you want manually — each is a single `SKILL.md`
file, no dependencies. Commit `.claude/skills/` to your repo so the skills
are available to anyone (or any session) working on the project.

To make a skill available across *all* of your projects instead of one repo,
copy it into `~/.claude/skills/` (your user-level skills directory) rather
than a project's `.claude/skills/`.

### Claude Code on the web / Cowork

1. Add this repo (`richardkfm/vibes`) as a source, or add just the skill
   files to your own repo's `.claude/skills/` directory as above.
2. Skills under `.claude/skills/` in any repo attached to a session are
   picked up automatically — no separate install step.

In both environments, skills show up as slash commands (e.g. `/repo-map`)
and are also triggered automatically when their description matches the
task at hand.

## License

MIT — see [LICENSE](LICENSE).

✨ This is a test change to verify the PR process
✨ Test change to verify PR process works correctly
