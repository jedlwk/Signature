# Signature

My writing voice, packaged as a Claude Code plugin. Every session starts knowing how I write, so I
stop typing "make it sound less AI" and "check the AI score".

It has three parts: a style guide split by material (code, documents, slides, scripts, posts), a
checker that flags the AI tells I keep removing, and a short reminder at the start of each session.

## What it does

<!-- signature:ignore-start -->

**Before** (the usual first draft):

> I am thrilled to share that we hosted an incredible workshop last week — a truly transformative
> experience that showcased the robust potential of AI in the workplace. Moreover, attendees left
> empowered to leverage these tools seamlessly.

**After** (with Signature, using only the facts I gave it):

> Last week I ran a workshop for 30 people from HR. None of them had written code. By lunch they had
> built a small tool that screens CVs. What surprised me was how fast they got to the real question:
> who checks its work?

<!-- signature:ignore-end -->

The first one could be about any workshop. The second one could only be about this one.

## Why a plugin and not a prompt

A prompt in a chat helps once. This stays on every time.

- **It loads itself.** The skill triggers on anything written under my name, and a session-start
  reminder makes sure it does.
- **It is split by material.** Code comments, a customer doc, a slide and a speaker script each want
  a different voice. One long prompt can't do all four.
- **It checks its own work.** A script scans the draft and the skill fixes what it finds, so I don't
  have to spot the tells myself.
- **It stays small.** Only a short front page loads at first. Detail loads when it is needed.

## Install

In Claude Code:

```bash
/plugin marketplace add jedlwk/Signature
```

```bash
/plugin install signature@signature
```

Then start a new session. The plugin applies in every project.

To install from a local copy of this repo, use the folder path in the first command instead.

To use only the skill, without the hook, copy `skills/jed-writing-style` into `~/.claude/skills/`.

For tools that can't load a plugin, paste the short version from [docs/paste-prompt.md](docs/paste-prompt.md).

## How it triggers

- The skill's description matches drafting, rewriting, polishing or reviewing anything under my name.
- Phrases like "AI check", "AI score", "sound less AI" and "keep my tone" load it.
- A session-start hook adds one short paragraph reminding Claude to use it. It touches no files and
  makes no network calls. Delete the `hooks` folder if you don't want it.
- A folder's own CLAUDE.md, a rubric, a template or a repo convention beats this guide where they differ.

## Modes

| I say | Mode | What happens |
|---|---|---|
| "write", "draft" | Draft | New text in my voice, short first |
| "polish", "keep my tone" | Polish | Minimal edits, my phrasing stays |
| "rewrite", "too AI" | Rewrite | Rebuilt from what the text is trying to say |
| "check", "AI score" | Audit | Findings only, no rewrite |
| names, taglines | Options | Three to five real options and a pick |

## What changes by material

| Material | Reader | Voice | Checker register |
|---|---|---|---|
| Code | The next developer | Clarity first, comments say why | `code` |
| Documents | Someone reading carefully | Answer first, steady, no exclamation marks | `doc`, `customer`, `course` |
| Slides | Someone glancing up | One message per slide, two lines per box | `slides` |
| Scripts | Someone listening | Short spoken lines, contractions, about 140 words a minute | `script` |
| Posts and messages | A peer | Warm, personal, opens on a real question | `post`, `message` |

The shared rules apply everywhere: point first, plain words, under one comma per sentence, no
dashes as punctuation, no semicolons, no invented facts.

## The checker

```bash
python3 skills/jed-writing-style/scripts/ai_check.py draft.md --register doc
```

```bash
python3 skills/jed-writing-style/scripts/ai_check.py deck.pptx --register slides
```

```bash
python3 skills/jed-writing-style/scripts/ai_check.py app.py
```

```bash
pbpaste | python3 skills/jed-writing-style/scripts/ai_check.py - --register post
```

It needs only Python 3. It reads `.md`, `.txt`, `.docx`, `.pptx` and source files (comments and
docstrings only).

**Findings are ranked:**

- **P0** is what I remove every time: dashes, counted preambles, throat-clearing, chatbot residue,
  open loops, inflated significance.
- **P1** is a strong tell: LLM words, "serves as", "-ing" riders, vague authority, semicolons.
- **P2** is a weak signal: tidy groups of three, "not X but Y", wordy phrases.

**Output.** A score in tells per 100 words. Under 1 is clean. 3 or more means fix it before
sending. Exit code 0 is fine, 1 means fix it, 2 means the file could not be read. Add `--json` for
machine output and `--list-registers` to see every register.

**Skipping a passage.** Wrap it in `<!-- signature:ignore-start -->` and `<!-- signature:ignore-end -->`,
or end a line with `<!-- signature:ignore-line -->`. The docs here use this to quote the tells they ban.

**What it is not.** It is a style linter, not an AI detector like GPTZero. A clean score means
nothing obvious is left. The goal is writing that sounds like me, not text that games a detector.

## What is in the repo

```
signature/
├── .claude-plugin/
│   ├── plugin.json            plugin manifest
│   └── marketplace.json       lets /plugin marketplace add find it
├── skills/jed-writing-style/
│   ├── SKILL.md               front page: quick card, modes, workflow
│   ├── references/            loaded only when needed
│   │   ├── voice.md           the voice, word choices, registers
│   │   ├── ai-tells.md        every tell, ranked P0, P1, P2
│   │   ├── code.md
│   │   ├── documents.md
│   │   ├── slides.md
│   │   ├── scripts.md
│   │   ├── posts-and-messages.md
│   │   ├── examples.md        before and after, plus one worked run
│   │   └── samples.md         real writing to match by ear
│   └── scripts/ai_check.py    the checker
├── hooks/                     session-start reminder
├── evals/                     scenarios to compare with and without the skill
├── tests/                     unit tests and fixtures
├── docs/paste-prompt.md       short version for other tools
├── CHANGELOG.md
└── README.md
```

## Develop

Run the tests from the repo root:

```bash
python3 -m unittest discover -s tests -v
```

They cover the checker, check that approved writing of mine stays clean and AI-flavoured text gets
flagged, and check that the skill's own docs pass the checker. They also check the skill against
Anthropic's authoring rules: the frontmatter, the length of `SKILL.md`, and references one level deep.

To change the voice, edit the matching file in `references/`. Keep `SKILL.md` short. Then bump
`version` in `.claude-plugin/plugin.json`, add a line to the changelog, and run:

```bash
/plugin marketplace update signature
```

When I correct the same thing twice, it goes into the guide. The [evals](evals/README.md) show whether
the change helped.

## Make it yours

The voice lives in `references/voice.md` and `references/samples.md`. Replace those two files with
your own rules and writing, adjust the mechanics in `SKILL.md`, and rename the skill. The checker
and the structure work for anyone.

## Where it came from

The voice comes from my own writing and from years of corrections: four earlier style guides built
from project history, a Medium post, a LinkedIn post and my code conventions. The structure follows
what others do well.

- [Anthropic's skill authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):
  a short front page, detail in reference files one level deep, evals first, scripts that handle errors.
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing):
  the catalogue behind most of the tells.
- [blader/humanizer](https://github.com/blader/humanizer): staging versus stating, and a draft,
  critique and final loop.
- [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing): severity
  tiers, ignore markers, a tested checker.
- [haidrrrry/humanize-ai-writing](https://github.com/haidrrrry/humanize-ai-writing): a system prompt
  for tools without plugins.
- The common advice on em dashes: give the model what to write instead, not just a ban.

I left out a few of their rules because they clash with how I write. "actually" and "key" are mine.
Rhetorical questions and deliberate repetition stay when I choose them.

## Limits

- The evidence for scripts, slides, emails and commit messages is thinner than for documents and
  posts. Those parts are marked as likely in the references.
- The checker finds patterns. It cannot judge a flourish at the end of a paragraph, so the skill
  rereads endings by hand.
- The voice is mine. It will sound off on someone else's work unless the two files above are replaced.
