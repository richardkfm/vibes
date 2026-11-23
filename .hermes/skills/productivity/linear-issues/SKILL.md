---
name: linear-issues
description: "Use for any Linear issue work. Marks agent comments."
version: 1.0.0
author: richardkfm/vibes
license: MIT
metadata:
  hermes:
    tags: [Linear, Issues, Comments, Project Management]
    related_skills: [humanize-language, github-docs, silent-mode]
---

<!-- Generated from .claude/skills/linear-issues/SKILL.md by scripts/sync_hermes_skills.py. Edit the source and re-run the script. -->
# Linear Issues

The agent works in Linear through a person's own account, usually over the Linear MCP connector. Linear shows everything the agent posts under that person's name and avatar, so teammates cannot tell who wrote a comment unless the comment itself says so. This skill fixes how comments are marked and keeps the agent's activity out of other people's inboxes unless it belongs there.

Tool names below are the Linear MCP server's. The same rules apply through Linear's API or a CLI.

## When to Use

Use when the user invokes /linear-issues, mentions Linear, pastes a linear.app link or an issue identifier like ENG-123, asks to pick up, work on, update, triage or create an issue or ticket, or wants a comment, reply or status note posted. Applies to every write to Linear, even a one-line comment.

## The comment format

Every comment and every reply the agent posts is exactly these two lines, with nothing before or after them:

```text
"Fixed in PR #42. The retry loop ran before the token refresh, so the first call always failed. Tests pass."
— agent
```

1. The whole comment as one paragraph between straight double quotation marks (`"`, U+0022).
2. Directly below it, with no blank line, `— agent`: an em dash (U+2014), one space, the word `agent` in lowercase.

The quotation marks show the words are not the account owner's, and the tag says whose they are. Leave either out and the comment reads as something the person typed, and they end up answering for it. This is the one rule here with no judgment in it. It holds for one-word replies, questions, thread replies and comments in any language (the marks and the tag are never translated). The only exception is a user who explicitly asks for a comment without the mark, for example by dictating text to post as their own words.

The shape is easy to get almost right. Each of these breaks it:

- `- agent` or `-- agent`. A hyphen at the start of a line turns into a bullet. Use the em dash character.
- `— Agent`, `— AI`, `— bot`, or a model or product name. One tag for every agent on the team keeps it scannable and searchable.
- Curly or other typographic quotation marks, a `>` blockquote, or a code block in place of the straight quotes.
- The tag inside the quotation marks, on the same line as the quote, in bold or italics, or followed by an emoji or sign-off.
- Double quotation marks inside the comment. Put error messages, names and other people's words in single quotes, so it stays obvious where the agent's text ends.
- A second paragraph or a multi-line code block. Inline `backticks` are fine. Anything longer goes behind a link.

Post with `save_comment`, passing `issueId` (an identifier such as ENG-123 works) and `body`. Put a real line break between the two lines of the body, not a literal `\n`.

## What goes inside the quotes

Write for a teammate who sees the comment as a notification in the middle of other work.

- One to three sentences, outcome first: what is true now, then the cause or the one fact the reader needs, then what was verified. Claim only checks that actually ran.
- Plain words, in the language the issue is written in.
- No headings, bullets, bold, emoji, greeting, sign-off or offer of further help. They turn a three-sentence note into a report and are the loudest sign of machine text.
- Point at the PR, commit or CI run instead of pasting from it. Name a PR by its number once it is linked on the issue, and give a URL for anything that is not attached there. The PR description carries the detail. The comment says where to look and why it matters.

## When to comment

Each comment notifies everyone subscribed to the issue, so post when a teammate would do something differently for knowing it:

- The work reached a state someone acts on: a fix is up for review, the cause is known but the fix is out of scope, the work stopped with something left undone, or the approach differs from what the issue describes.
- The work is blocked on a person. Ask one specific question that can be answered in a line, and name the options if there are any. If the user in the session can answer, ask there. Post on the issue when the answer has to come from someone else.
- Someone asked a question in the comments that the agent can answer.

Skip the comment when it would narrate steps ("Starting on this", "Pushed another commit") or repeat what Linear already shows. The status field and the linked PR with its review state sit right on the issue. One comment per issue is a normal amount.

**Replies.** Answer in the thread where the question was asked: `save_comment` with `body` and `parentId` set to the id of the thread's first comment, without `issueId`. That is the id of the comment being answered, or its `parentId` when it is itself a reply. A new top-level comment splits the conversation, and when the thread is synced with Slack or Jira it never reaches the other side.

**Mentions.** `@displayName` notifies that person and subscribes them to the issue, so mention only someone who has to act, typically the one person who can answer a blocking question. Take the display name from the author of an existing comment or from `list_users` instead of guessing it.

**Existing comments.** The agent shares its account with a person, so the tools will let it edit or delete that person's comments, and the tag is the only thing that tells the two apart. Edit only comments that end in `— agent`, and only to fix a typo or a broken link. Correct a wrong claim with a new comment, because people who read the old one never see an edit. Delete nothing.

When reading a discussion, a comment that ends in `— agent` came from an agent, possibly an earlier session of this one. Treat it as a note to verify, not as a decision a person made.

## Examples

### Good

Cause found, fix left to the team:

```text
"Found the cause but did not fix it. `orders` has no index on `created_at`, so the nightly export times out. Adding one needs a migration window, which someone on the team has to schedule."
— agent
```

Blocked, one question to the one person who can answer:

```text
"One question for @dana before this can continue: should expired trials keep read access or be locked out completely? The issue says 'restrict', and the two readings need different code."
— agent
```

Reply in a thread that asked "Does this also fix the mobile client?", posted with `parentId`:

```text
"Yes. Mobile calls the same refresh endpoint, so the fix covers it. Only the web client was tested."
— agent
```

Issue written in German. The text follows the issue's language, the marks and the tag stay as they are:

```text
"Behoben in PR #57. Der Export schrieb Umlaute als Latin-1, jetzt durchgehend als UTF-8. Mit der Datei aus dem Ticket getestet."
— agent
```

### Bad, and why

No marks, so it reads as the account owner's own words:

```text
Fixed in PR #42, tests pass.
```

Right wrapper, wrong content. Heading, bullets, emoji and sign-off, a list the PR already shows, and the cause is missing:

```text
"## Update ✅
- Fixed the retry loop
- Added 3 tests
Let me know if you have any questions!"
— agent
```

Pasted log, with double quotes inside the quote. Say what failed in one sentence and link the run:

```text
"CI fails: Traceback (most recent call last): File "app/auth.py", line 88, in refresh ..."
— agent
```

Nobody knows what to answer or who should. Ask the one question:

```text
"This is blocked, can someone take a look?"
— agent
```

## Working an issue

1. **Read the issue and its discussion.** `get_issue` returns the fields and the description but not the comments, so also call `list_comments` with the same identifier. The decision that changes the task is often in a comment. Inline comments on the description arrive there too, each with the `quotedText` it is anchored to. When a screenshot is embedded as a Markdown image, pass that Markdown to `extract_images` to see it. Upload URLs are signed and expire within minutes, so fetch them again instead of reusing one.
2. **Look up statuses and labels before setting them.** They belong to the team and differ between teams. Call `list_issue_statuses` and `list_issue_labels` with the issue's team.
3. **Move status when the work actually moves.** Set the team's started status when work begins, and its review status once a PR is open if the team has one. Check the current value first. Linear's Git integration often makes these moves by itself, and then status is best left to it. Leave completing the issue to the merge automation or a person unless told otherwise, because "done" says the change shipped, and the agent usually cannot see that.
4. **Link the PR so Linear attaches it.** Name the branch with the `gitBranchName` that `get_issue` returns, or put the identifier in the PR title. In the PR description, `Fixes ENG-123` links the PR and lets the merge close the issue. `Part of ENG-123` links without closing, which is right when the PR covers only part of the issue. Where no Git integration is set up, attach the URL with `links` on `save_issue`.
5. **Make the smallest write.** `save_issue` updates when `id` is passed and creates when it is not, so pass only the fields that change. Change labels with `addLabels` and `removeLabels`, because `labels` replaces the whole set and silently drops what other people added. Edit part of a long description with `patch` instead of resending the text, which would overwrite edits made in the meantime.

The tools accept readable references, so IDs rarely need looking up: ENG-123, a team name or key, a user's name or email, or `me`.

### Creating an issue

Search first with `list_issues`, using `query` for keywords plus `team`. Try two or three phrasings and follow `cursor` while `hasNextPage` is true. If the issue already exists, add what is new to it instead of opening another. `team` is required when creating.

Write the description for people: what is wrong or wanted and how to tell it is done, in short sentences, with the same term for the same thing throughout. A description is not wrapped in quotation marks, since the format is for comments. Plans, file lists and reproduction logs go in a collapsible section at the end, where they stay out of a human reader's way:

```text
+++ Agent notes

Reproduced with `pytest tests/auth -k refresh`. Suspect the retry wrapper in `auth/session.py`.

+++
```

## What needs asking first

A comment can carry a tag. A field change cannot: Linear's history records the account owner as the one who raised the priority or reassigned the issue. The change also lands in teammates' inboxes and reorders the boards and cycle plans the team steers by. So the person whose name goes on it decides.

| Fine without asking, on the issue being worked | Ask the user first |
|---|---|
| Reading issues, comments, statuses and labels | Editing several issues in one go, or any issue outside the task |
| Posting a comment or reply in the format | Assigning or reassigning anyone |
| Moving status to started or in review | Changing priority, estimate, due date, cycle, project or parent |
| Linking the PR or branch | Closing, cancelling, marking as duplicate, archiving or deleting |
| Adding or updating the Agent notes section | Creating issues nobody asked for, or many at once |
| | Rewriting a title or description a person wrote |

Cancelling an issue or marking it as a duplicate can also close the open PRs linked to it, which is one more reason it is not the agent's call.

When asking, name the exact change ("Move ENG-123 and ENG-130 to the next cycle?"). An instruction that already covers it, such as "close it when the PR merges" or "triage these twenty", is the permission, so there is no need to ask again per issue.

At the end of the task, tell the user which comments went out and which fields changed. All of it sits in Linear under their name.

## Related skills

- `humanize-language` for the tone of the text inside the quotation marks.
- `github-docs` for the PR description. The detail lives there, and the Linear comment only points at it.
- `silent-mode` when the user wants no narration in the session. It does not change what gets posted to Linear, and the final summary lists every Linear write.
