# Signature

[![test](https://github.com/jedlwk/Signature/actions/workflows/test.yml/badge.svg)](https://github.com/jedlwk/Signature/actions/workflows/test.yml) <!-- signature:ignore-line -->
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) <!-- signature:ignore-line -->

Signature is my writing voice (Jed Lee, [@jedlwk](https://github.com/jedlwk)), packaged as a Claude
Code plugin. Every session starts knowing how I write, so I stop typing "make it sound less AI" and
"check the AI score".

It bundles:

- **A style guide** split by material: code, documents, slides, scripts and posts.
- **A checker** that flags AI tells, the habits that make text read as machine written. Examples are
  dashes used as punctuation, words like "seamless", and tidy lists of three. <!-- signature:ignore-line -->
- **A session-start hook**, a small script Claude Code runs when a session opens. Mine adds one
  paragraph reminding Claude to use the guide.

Want your own version? See [Make it yours](#make-it-yours).

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

## Install

In Claude Code, add the marketplace and install the plugin:

```text
/plugin marketplace add jedlwk/Signature
```

```text
/plugin install signature@signature
```

Then start a new session. The plugin applies in every project.

**From a local copy.** Clone the repo, then run `/plugin marketplace add ./Signature` from the folder that holds it.

**Skill only, no hook.** Copy `skills/jed-writing-style` into `~/.claude/skills/`.

**Other tools** that can't load a plugin: paste the short version in [docs/paste-prompt.md](docs/paste-prompt.md).

## Use it

You mostly don't have to. The skill loads when you ask Claude to write or review anything under my
name. It also loads on phrases like "AI check" or "keep my tone".

You can also call it on purpose:

| Command | What it does |
|---|---|
| `/signature:check <file or text>` | Runs the checker and reports findings, grouped by priority. No rewrite. |
| `/signature:polish <file or text>` | Polishes with minimal changes, then checks. |
| `/signature:learn` | Compares what Claude wrote with what I changed it to, and proposes a rule or an example. Asks before writing. |
| `/signature:plan` | Scans the project and writes `STYLE_PLAN.md`, a plan to bring it into my style. Changes nothing. |
| `/signature:apply` | Applies only the changes I approved in that plan. |
| `/signature:verify` | Checks a changed Word or PowerPoint file in place of opening it. |

**Restyle a whole project.** Run `/signature:plan` in any project. It writes `STYLE_PLAN.md` and stops.
I tick the changes I want, then run `/signature:apply`. It reads and edits Word, PowerPoint, HTML,
notebooks, Markdown and text files, plus code comments and user-facing strings on request. Word and
PowerPoint keep their formatting, because only the text changes. It also handles other jobs, such as
`/signature:plan rename Acme to Zenith`. See [docs/restyle.md](docs/restyle.md).

**Use it in any session.** `./install.sh --all` sets it up for Claude Code, the desktop app and Codex. A
session with nothing installed can fetch it with one pasted prompt, and a chat with no shell gets a find
and replace table. See [docs/anywhere.md](docs/anywhere.md).

`/signature:learn` keeps a private log of my corrections in `~/.claude/signature/` on my machine. It is
never committed, and anything confidential is replaced with a placeholder first.

Claude picks one of six modes from what you say:

| You say | Mode | What happens |
|---|---|---|
| "write", "draft" | Draft | New text in my voice, short first |
| "polish", "keep my tone" | Polish | Minimal edits, my phrasing stays |
| "rewrite", "too AI" | Rewrite | Rebuilt from what the text is trying to say |
| "check", "AI score" | Audit | Findings only, no rewrite |
| names, taglines | Options | Three to five real options and a pick |
| "restyle this project" | Plan | Writes `STYLE_PLAN.md`, then waits for approval |

A folder's own CLAUDE.md, a rubric, a template or a repo convention beats this guide where they differ.

## Why a plugin and not a prompt

A prompt in a chat helps once. This stays on every time.

- **It loads itself.** The skill triggers on anything under my name, and the hook makes sure it does.
- **It is split by material.** A comment, a customer doc, a slide and a script each want a different
  voice. One long prompt can't do all four.
- **It checks its own work.** A script scans the draft and the skill fixes what it finds.
- **It stays small.** A short front page loads first. Detail loads only when needed.

## What changes by material

| Material | Reader | Voice |
|---|---|---|
| Code | The next developer | Clarity first, comments say why |
| Documents | Someone reading carefully | Answer first, steady, no exclamation marks |
| Slides | Someone glancing up | One message per slide, two lines per box |
| Scripts | Someone listening | Short spoken lines, contractions, about 140 words a minute |
| Posts and messages | A peer | Warm, personal, opens on a real question |

The shared rules apply everywhere. Point first, plain words, under one comma per sentence. No dashes
as punctuation, no semicolons, no invented facts.

## The checker

`/signature:check` runs it for you. To run it yourself, from a clone of the repo:

```bash
python3 skills/jed-writing-style/scripts/ai_check.py draft.md --register doc
```

A register is the type of material (`doc`, `script`, `slides`, `post` and so on). It needs only
Python 3. It can also check numbers against the facts you gave it and measure a script's spoken
length. It can apply safe fixes too, and calibrate on your own writing. Every option is in
[docs/checker.md](docs/checker.md).

It is a style linter, not an AI detector like GPTZero. A clean score means nothing obvious is left.

## How well it works

I ran seven writing tasks with and without the skill, on Haiku, Sonnet and Opus, fixed what failed,
and ran them again. On a 41 line rubric, plain Sonnet met 27 lines. With the skill, Sonnet went from
36 to 40, Haiku from 28 to 36 and Opus from 38 to 41. The biggest wins were not inventing facts,
hitting a script's length, and keeping my tone when polishing.

Two honest limits. Haiku still invents details, so use Sonnet or Opus to write under my name. And these
are single runs scored by one reader, so treat the numbers as a direction. Results, caveats and raw
outputs are in [evals/RESULTS.md](evals/RESULTS.md).

## What is in the repo

```text
signature/
├── skills/jed-writing-style/
│   ├── SKILL.md               front page: quick card, modes, workflow
│   ├── references/            voice, tells, code, documents, slides, scripts, posts,
│   │                          examples, samples, plan, office
│   └── scripts/               ai_check, plan_scan, apply_edits, verify_office, formats
├── commands/                  /signature:check, polish, learn, plan, apply, verify
├── .claude-plugin/  hooks/    the plugin manifest, the session-start reminder
├── docs/                      checker, restyle, anywhere, develop, paste-prompt
├── evals/  tests/             scenarios and results, unit tests and fixtures
├── install.sh                 sets it up for Claude Code, Codex and any project
└── .github/  CHANGELOG.md  LICENSE  README.md
```

## Develop

Run the tests with `python3 -m unittest discover -s tests -v`. Releases, changing the voice and what the
tests cover are in [docs/develop.md](docs/develop.md).

## Make it yours

Fork the repo, then replace `references/voice.md` and `references/samples.md` with your own rules and
writing. Adjust the mechanics in `SKILL.md`, rename the skill, and run the tests. The checker and the
structure work for anyone. The voice is mine, so it will sound off on someone else's work until you do.

## Where it came from

The voice comes from my own writing and from corrections I made again and again: four earlier style
guides built from project history, a Medium post, a LinkedIn post and my code conventions. The
structure and many of the tells come from
[Anthropic's skill authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
[Wikipedia's Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
[blader/humanizer](https://github.com/blader/humanizer),
[conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) and
[haidrrrry/humanize-ai-writing](https://github.com/haidrrrry/humanize-ai-writing). I left out the rules
that clash with how I write. They are listed in `ai-tells.md`.

## Limits

- The evidence for scripts, slides, emails and commit messages is thinner than for documents and posts.
  Those parts are marked as likely in the references.
- The checker finds patterns. It can't judge a flourish at the end of a paragraph, so endings get read by hand.
- The facts check catches invented numbers. It cannot catch an invented anecdote, so read the draft.
- Haiku still invents content. Use Sonnet or Opus to draft, and Haiku only for the checker and audits.
