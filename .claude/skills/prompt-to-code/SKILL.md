---
name: prompt-to-code
description: Transform a system prompt (agent instructions, persona, GPT/assistant config) into working code — a runnable app or agent where deterministic rules become real code and only genuine judgment stays in the prompt. Use whenever the user has a system prompt, custom GPT, assistant config, or a long block of LLM instructions and wants to "turn it into code," build an app/agent/bot from it, productionize it, make it reliable, or asks why their giant prompt keeps getting ignored — even if they don't use the word "code."
---

# Prompt to Code

A long system prompt is a program written in the least reliable programming
language there is. Every rule in it ("always respond in JSON", "never exceed
500 words", "if the user asks about billing, collect their account ID
first") is executed probabilistically, costs tokens on every call, and
degrades as the prompt grows. The fix is to treat the prompt as a spec and
migrate it into code: everything checkable becomes code that *cannot* be
ignored, and the prompt shrinks to the part that genuinely needs a model —
judgment, tone, open-ended language work.

The result is a runnable project: an agent loop or pipeline with real tool
definitions, schemas, and validation, plus a much smaller prompt.

## Step 1: Parse the prompt into components

Read the whole prompt and sort every line into one of these buckets. This
inventory drives everything after it — share it with the user as a short
table before writing code, since it doubles as a review of what their
prompt actually contains (most authors are surprised).

| Bucket | Looks like | Becomes |
|---|---|---|
| **Identity/tone** | "You are a friendly support agent…" | Stays in the (small) prompt |
| **Hard output rules** | "Respond only in JSON with fields x, y" | Schema + structured output + validation |
| **Workflow/sequence** | "First ask A, then check B, then do C" | Code orchestration: states, steps, branches |
| **Conditional routing** | "If billing question → X, if bug → Y" | Classifier step or explicit router in code |
| **Tool descriptions** | "You can search the KB / look up orders" | Real tool definitions with typed params |
| **Constraints/guards** | "Never reveal internal notes", "max 500 words" | Validators/filters on input and output |
| **Reference data** | Pasted FAQ, policy text, price lists | Data files or retrieval — out of the prompt |
| **Examples** | Sample dialogues, few-shot pairs | Test cases (and a few kept as few-shot if needed) |

Flag contradictions and dead rules while sorting — prompts accreted over
months usually have both, and code forces a decision the prompt let them
dodge.

## Step 2: Decide what stays prompt vs. becomes code

The dividing line: **could a function check it?** If yes, make it code.

- "Always include a disclaimer" → code appends it. Done, 100% reliable.
- "Keep answers under 500 words" → validate length, retry or truncate.
- "Ask for the account ID before discussing billing" → a state machine or
  a required tool parameter, not a hope.
- "Be warm but professional" → stays in the prompt; that's real model work.

Every rule moved to code is a rule the model can no longer break *and* a
line removed from the prompt — reliability and cost improve together. A
good migration typically cuts the prompt by 60–90%. What remains: identity,
tone, the current step's focused instructions, and judgment calls.

Prefer many small prompts over one giant one: if the workflow has distinct
stages (classify → gather info → resolve → summarize), give each stage its
own short prompt invoked by code, instead of one prompt juggling every
stage at once. Per-stage prompts are individually testable and don't leak
instructions across stages.

## Step 3: Build it

Default stack unless the user says otherwise: **Python + the Anthropic
SDK** (or the Claude Agent SDK for tool-heavy agents; TypeScript if the
project is already TS). Load the `claude-api` skill if available for
current model IDs and API patterns. Structure:

```
project/
├── prompts/          # small per-stage prompts (versioned text files)
├── schemas.py        # Pydantic models for every structured output
├── tools.py          # real tool implementations + typed definitions
├── guards.py         # input/output validators from the constraints bucket
├── pipeline.py       # the orchestration the workflow bucket described
├── data/             # reference data extracted from the prompt
└── tests/            # examples bucket → assertions
```

Key implementation moves:

- **Structured outputs**: define a schema for anything the prompt described
  in prose ("respond with a summary, a category, and a confidence score"),
  request it via tool-use/structured output, and validate with Pydantic.
  Parsing free text with regex means the migration isn't finished.
- **Tools over descriptions**: where the prompt *described* capabilities,
  implement them as actual tools with typed parameters — the description
  in the prompt becomes the tool's `description` field, where it's
  delivered to the model at exactly the right moment.
- **Guards run on every call**: output validators retry once with the
  violation fed back ("response was 812 words, limit is 500 — shorten"),
  then fall back deterministically (truncate, refuse, escalate). Input
  guards handle the "if the user asks about X, don't engage" rules.
- **Keep prompts as files, not string literals** — they'll be edited by
  non-programmers and diffed in review.

## Step 4: Turn the examples into tests

The examples bucket is a free test suite. Each sample dialogue or few-shot
pair becomes a test: run the pipeline on the input, assert the checkable
parts (schema validity, routing choice, guard behavior, required fields) —
not exact wording. Add tests for every guard (does the length limit
actually trigger?) and every workflow branch. This is the payoff of the
whole migration: the prompt's promises become assertions that run in CI.

## Step 5: Report the migration

Tell the user what moved where, in a short summary: rules now enforced in
code (with file references), what remains in the prompt and why, prompt
size before → after, and any contradictions or ambiguities found in the
original that need their decision. The migration is also an audit — don't
silently resolve genuine ambiguities in a spec-level rule; ask.

## Smaller-scope variants

Not every request wants the full pipeline. Match the ceremony to the ask:

- **"Wrap this prompt in code"** (minimal): a clean script — prompt file,
  API call, schema validation, retries. No orchestration invented.
- **"Build an app from this GPT/assistant"**: full treatment above, plus
  whatever interface fits (CLI, FastAPI endpoint, simple web UI).
- **"Why does my prompt keep getting ignored?"**: run Step 1 as a
  diagnosis and report which rules are code-shaped (the ones failing are
  almost always these), with a migration recommendation — before writing
  any code. Rules stated in prompts compete for attention; rules in code
  don't compete at all.
