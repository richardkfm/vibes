---
name: humanize-language
description: Rewrite text so it reads like a person wrote it — strip AI tells, formulaic structure, hedging, and marketing sheen while keeping the meaning intact. Use whenever the user asks to humanize, naturalize, de-AI, or "make this sound less like ChatGPT," asks why their text sounds robotic or generic, or wants any draft (email, blog post, docs, README, LinkedIn post, cover letter) to sound more natural, warmer, or more like them. Also apply it to your own writing when the user asks for prose a human will actually read.
---

# Humanize Language

AI-generated text has a recognizable accent. Readers pick up on it within a
sentence or two, and once they do, they trust the text less and skim harder.
The goal of this skill is not to "fool detectors" — it's to produce writing
that a specific person plausibly wrote, with a point of view, natural rhythm,
and nothing that reads like filler.

## The core move

Don't polish sentence by sentence. First ask: **what is this text actually
trying to say, and to whom?** Most AI-sounding text fails because it was
generated without a stance — it covers a topic instead of saying something
about it. Identify the one or two things the author actually means, then
rewrite around those. A rewrite that keeps every original sentence but swaps
words is still going to sound generated.

## Tells to remove

Work through these — they're roughly ordered by how loudly they scream "AI".

**Structural tells**
- The essay skeleton: intro that announces the topic, three parallel body
  points, conclusion that restates the intro. Humans wander a little; let
  the strongest point come first and cut the summary paragraph entirely.
- Bullet lists where prose belongs. Bullets are for genuinely enumerable
  things (steps, options, specs). If each bullet is a full sentence making
  an argument, merge them into a paragraph.
- The rule of three ("fast, reliable, and scalable"). One triad is fine;
  a triad in every paragraph is a fingerprint. Vary it: sometimes one
  adjective, sometimes two, sometimes a specific example instead.
- Headers on 400-word documents. Short pieces don't need navigation.

**Phrase-level tells** — delete or replace on sight:
- "It's important to note that", "It's worth mentioning" → just say the thing
- "delve", "tapestry", "landscape", "realm", "navigate (a challenge)",
  "unlock", "leverage", "robust", "seamless", "elevate", "foster",
  "crucial", "pivotal", "myriad", "plethora"
- "In today's fast-paced world", "In the ever-evolving landscape of X" →
  delete the whole sentence; it says nothing
- "Whether you're a beginner or an expert..." → pick the actual audience
- "In conclusion", "Overall", "Ultimately" as paragraph openers
- "not only X but also Y" more than once per document
- Empty intensifiers: "truly", "incredibly", "seamlessly", "effortlessly"

**Rhythm tells**
- Uniform sentence length. Human prose alternates: a long sentence that
  builds a thought, then a short one. Like that. Read the draft aloud (or
  simulate it) — if every sentence takes the same breath, break some and
  fuse others.
- Em-dash overuse. One or two per page is a human's dose.
- Every paragraph being 3–4 sentences. Let one be a single sentence when
  it's earned.

**Stance tells**
- Hedge stacking: "may potentially", "it could be argued that", "some might
  say". One hedge is honest; two is evasion. Commit to claims the author
  can stand behind and cut the rest.
- Both-sidesing everything. A human writer has opinions. If the text
  weighs pros and cons and concludes "it depends," push for what the
  author actually recommends.
- Praise inflation in feedback or reviews ("Great question!", "This is a
  fantastic start"). Keep warmth, cut ceremony.

## Add what AI leaves out

Removing tells gets you to neutral. To get to *human*, add the things
generated text rarely has:

- **Specifics over categories.** "Tools like Slack and Notion" → name the
  actual tool the author uses. "Significantly faster" → the number, if
  known. If you don't know the specifics, ask the user rather than
  inventing them — invented details are worse than vague ones.
- **A first-person moment**, where the format allows it: what the author
  tried, noticed, got wrong. One concrete anecdote does more than three
  paragraphs of balanced analysis.
- **Mild imperfection of form.** Starting a sentence with "And" or "But",
  a sentence fragment for emphasis, a parenthetical aside (like this one).
  Don't manufacture typos or slang — that's a costume, not a voice.
- **The author's register.** Match how this person actually talks. A
  founder's update, a support email, and a research summary should not
  share a voice. If you have samples of the user's own writing in the
  conversation, imitate their vocabulary and sentence habits.

## Process

1. Read the whole draft first. Write one sentence to yourself: what is this
   text for, who reads it, what should they do or feel after.
2. Cut everything that doesn't serve that sentence — usually 10–30% of the
   draft goes, mostly openings, transitions, and summaries.
3. Fix structure (order of points, bullets-vs-prose) before wording.
4. Then do the phrase- and rhythm-level pass from the lists above.
5. Read it back in the author's voice. If any sentence would make you
   cringe to say aloud to the intended reader, rewrite or cut it.

Preserve meaning strictly: don't add claims, change facts, or shift the
level of commitment ("we will" vs "we hope to") while rewriting. If the
original is ambiguous on a point that matters, flag it instead of guessing.

## Output

Return the rewritten text, then a short note (2–4 lines, not a table) on
the biggest changes and why — e.g. "cut the intro paragraph, it restated
the title; merged the bullet list into prose; replaced 'leverage' twice."
If the user gave length constraints or a platform (LinkedIn, docs, email),
respect its conventions: length, formality, and whether formatting like
headers is normal there.

**Example, before:**
> In today's fast-paced digital landscape, effective communication is
> crucial. It's important to note that our new tool not only streamlines
> workflows but also fosters collaboration, enabling teams to unlock their
> full potential.

**After:**
> Our new tool cuts the busywork out of handoffs — the review queue that
> used to take a day now clears in an hour. Teams spend that time actually
> talking to each other.

(The "after" assumes a real detail from the user. Without one, ask —
that's the difference between humanized and merely de-AI'd.)
