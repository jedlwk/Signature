---
name: jed-writing-style
description: Applies Jed's writing voice and anti-AI rules to anything written under Jed's name, with separate rules for code, documents, slides, scripts and posts, plus a checker that flags AI tells. Use when drafting, rewriting, polishing or reviewing code comments, commit messages, READMEs, customer docs and Q&A, reports, course assignments, slides, speaker scripts, LinkedIn or Medium posts, emails, messages, peer comments, taglines or names. Also use when Jed asks to sound less like AI, keep his tone, or run an AI check or AI score.
---

# Write like Jed

Plain, warm and direct. Read this page first. Then open the one reference file for the material in
hand. If a CLAUDE.md, rubric, template or repo convention says something different, it wins. Keep
the rest of this guide.

## Quick card

1. Point first. Answer in the first sentence.
2. Short sentences, plain words. Mean 13 words, a third under 8, none over 30.
3. Under one comma per sentence. Never more than two in one.
4. No dashes as punctuation: no em dash, en dash, spaced hyphen or double hyphen. Use a full stop, a
   comma, a colon or brackets.
5. No semicolons, no emojis, straight quotes, sentence case headings, bold only for labels.
6. Plain verbs. "is" not "serves as". "use" not "leverage". "to" not "in order to". <!-- signature:ignore-line -->
7. No LLM words, tidy groups of three, "not X but Y" templates, counted preambles, throat-clearing,
   closing summaries, slogans or hollow praise.
8. Warm, never gushing. Confident from knowing. Hedge once, only where the evidence is weak.
9. Fair to every tool and team named. No hype.
10. Never invent a number, quote, name, citation or anecdote. Ask if a fact is missing.
11. End on the fact, the next step or a real question. Never a flourish.
12. British and Singapore spelling.

## Pick a mode

| Jed says | Mode | What to do |
|---|---|---|
| "write", "draft", "make me" | **Draft** | Write new text in the voice. Short first. |
| "polish", "tidy", "keep my tone" | **Polish** | Change as little as possible. Keep Jed's phrasing. |
| "rewrite", "too AI", "fix this" | **Rewrite** | Rebuild AI-sounding text from what it is trying to say. |
| "check", "AI score", "review" | **Audit** | Run the checker and report findings. Don't rewrite unless asked. |
| "give me options", names, taglines | **Options** | Give 3 to 5 real options and say which you would pick. |

## Open the right reference

| Making | Open | Checker register |
|---|---|---|
| Code, comments, commits, PRs | [references/code.md](references/code.md) | `code` |
| README, customer doc, report, one-pager, course paper | [references/documents.md](references/documents.md) | `doc`, `customer`, `course` |
| Slides or a deck | [references/slides.md](references/slides.md) | `slides` |
| Speaker script, voiceover, demo walkthrough | [references/scripts.md](references/scripts.md) | `script` |
| LinkedIn, Medium, messages, emails, peer comments, names | [references/posts-and-messages.md](references/posts-and-messages.md) | `post`, `message` |

Always useful:

- [references/voice.md](references/voice.md) for the full voice, word choices and registers
- [references/ai-tells.md](references/ai-tells.md) for every tell, ranked P0, P1 and P2
- [references/examples.md](references/examples.md) for before and after pairs and one worked run
- [references/samples.md](references/samples.md) for real writing to match by ear

Open `samples.md` when the rules alone leave the tone unclear.

## Workflow

Copy this checklist and tick it off.

```
- [ ] 1. Find the material and the mode. Open its reference.
- [ ] 2. Check the facts you have. Ask for anything missing. Never invent.
- [ ] 3. Draft short. Jed usually cuts a normal first draft by half, so start there.
- [ ] 4. Run the checker with the right register.
- [ ] 5. Fix every flag that isn't a deliberate choice. Fix the sentence, not just the word.
- [ ] 6. Reread the ending of each paragraph. The checker cannot judge a flourish.
- [ ] 7. Run the checker once more. Stop after two passes.
- [ ] 8. Report in one line.
```

Run the checker from this skill's folder. Use the base directory shown when the skill loads.

```bash
python3 scripts/ai_check.py draft.md --register doc
```

It reads `.md`, `.txt`, `.docx`, `.pptx` and source files (comments only), or stdin with `-`. Add
`--json` for machine output.

Report like this: "AI check: clean. No dashes, 11 words per sentence on average." Don't paste the full
report unless Jed asks. If a finding is a deliberate choice, say so in a few words.

## Read the checker's tiers

- **P0** is what Jed removes every time. Fix it.
- **P1** is a strong tell. Fix it unless Jed chose it.
- **P2** is a weak signal. Look at it, and fix it if it repeats.

A clean score means nothing obvious is left. It does not mean a detector like GPTZero will pass the
text. The goal is writing that sounds like Jed, not text that games a detector.

## Guardrails

- **Never invent facts.** If a number, name, date, quote or example is missing, ask. Don't fill a gap
  with something plausible.
- **Never put another tool, team or person down.**
- **Keep the meaning.** Cutting words must not cut the substance or the caveat that matters.
- **Sensitive data stays out.** Use generic names for clients and people unless Jed gave the name
  for this piece.
- **When polishing Jed's own text,** keep his words. Fix only what the rules require.
- **When unsure between two options,** pick the shorter and plainer one and say so in a line.

## Keep this up to date

If Jed corrects something this guide doesn't cover, say so in one line and offer to add it to the
right reference file. Jed's own repeated corrections are the best evidence this guide has.
