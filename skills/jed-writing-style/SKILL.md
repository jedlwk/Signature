---
name: jed-writing-style
description: Applies Jed's writing voice and anti-AI rules to anything written under Jed's name, with separate rules for code, documents, slides, scripts and posts, plus a checker that flags AI tells. Use when drafting, rewriting, polishing or reviewing code comments, commit messages, READMEs, customer docs and Q&A, reports, course assignments, slides, speaker scripts, LinkedIn or Medium posts, emails, messages, peer comments, taglines or names. Also use when Jed asks to sound less like AI, keep Jed's tone, run an AI check or AI score, restyle a whole project or its docs, change a term or fact across a project, or check a changed Word or PowerPoint file.
---

# Write like Jed

Plain, warm and direct. Read this page first, then the profile's rules. Then open the one reference
file for the material in hand. If a CLAUDE.md, rubric, template or repo convention says something
different, it wins. Keep the rest of this guide.

## The profile

Jed's own voice lives in one profile folder: these rules, the voice, real samples, before and after
pairs, and the checker's settings. The default is [profiles/jed/](profiles/jed/). Check which one is
active with `python3 scripts/ai_check.py --which-profile`.

Read the profile's [rules.md](profiles/jed/rules.md) now, before drafting. It is the quick card, and
everything below assumes it.

## Pick a mode

| Jed says | Mode | What to do |
|---|---|---|
| "write", "draft", "make me" | **Draft** | Write new text in the voice. Short first. |
| "polish", "tidy", "keep my tone" | **Polish** | Change as little as possible. Keep Jed's phrasing, casing and "!!" in casual messages. Fix spelling and clear mistakes only. |
| "rewrite", "too AI", "fix this" | **Rewrite** | Rebuild AI-sounding text from what it is trying to say. |
| "check", "AI score", "review" | **Audit** | Run the checker. Report findings grouped P0, then P1, then P2. Don't rewrite unless asked. |
| "give me options", names, taglines | **Options** | Give 3 to 5 real options and say which you would pick. |
| "restyle this project", "rename X to Y everywhere", "update my docs to my style" | **Plan** | Scan the project and write `STYLE_PLAN.md`. Change nothing. Wait for approval, then apply only what was approved. |

## Open the right reference

| Making | Open | Checker register |
|---|---|---|
| Code, comments, commits, PRs | [references/code.md](references/code.md) | `code` |
| README, customer doc, report, one-pager, course paper | [references/documents.md](references/documents.md) | `doc`, `customer`, `course` |
| Slides or a deck | [references/slides.md](references/slides.md) | `slides` |
| Speaker script, voiceover, demo walkthrough | [references/scripts.md](references/scripts.md) | `script` |
| LinkedIn, Medium, messages, emails, peer comments, names | [references/posts-and-messages.md](references/posts-and-messages.md) | `post`, `message`, `peer` |
| A whole project, including Word, PowerPoint, HTML and notebooks | [references/plan.md](references/plan.md) | per file |
| Any `.docx` or `.pptx`, in any session, whatever it can or can't open | [references/office.md](references/office.md) | n/a |

Always useful:

- the profile's [voice.md](profiles/jed/voice.md) for the full voice, word choices and registers
- [references/ai-tells.md](references/ai-tells.md) for every tell, ranked P0, P1 and P2
- [references/detectors.md](references/detectors.md) for the AI-detector threshold (Pangram) and what to do when a text fails
- the profile's [examples.md](profiles/jed/examples.md) for before and after pairs and one worked run
- the profile's [samples.md](profiles/jed/samples.md) for real writing to match by ear

Open `samples.md` when the rules alone leave the tone unclear.

## Model

Write under Jed's name with Sonnet or Opus. Smaller models invent details and miss the voice, so don't draft
with them. If this session runs on one, say so and ask Jed to switch.

## Workflow

Copy this checklist and tick it off.

```
- [ ] 1. Read the profile's rules.md. Find the material and the mode. Open its reference.
- [ ] 2. List the facts Jed gave you. Anything not on the list needs a placeholder or a question.
- [ ] 3. Draft short. Jed usually cuts a normal first draft by half, so start there.
- [ ] 4. Run the checker with the right register and the facts. Add `--gate`, and `--voice` for a post, message, peer reply or course text.
- [ ] 5. Fix every flag that isn't a deliberate choice. Fix the sentence, not just the word.
- [ ] 6. Reread the ending of each paragraph. The checker cannot judge a flourish.
- [ ] 7. Run the checker once more with `--gate --log`. Stop after two passes.
- [ ] 8. Rewriting Jed's text? Run `--compare old new` and put back anything Jed wrote that was lost.
- [ ] 9. Anything public (post, Medium, README)? Clear the threshold in references/detectors.md.
- [ ] 10. Report in one line.
```

Run the checker from this skill's folder. Use the base directory shown when the skill loads.

```bash
python3 scripts/ai_check.py draft.md --register doc --facts-text "30 HR leaders, 10,000 documents"
```

`--facts-text` flags any number in the draft that isn't in the facts. Invented figures were the most
common failure in testing, so always pass it. For scripts add `--target-seconds 90` (or the length
asked for). `--fix` prints the text with safe mechanical fixes only. The checker reads `.md`,
`.txt`, `.docx`, `.pptx` and source files (comments only), or stdin with `-`. Add `--json` for
machine output.

`python3 scripts/ai_check.py --compare old.md new.md` scores both versions, lists the tells removed or
added, and lists every number, quote, code span and name from the old text that the new one lost.
Use it for every rewrite and polish.

`--gate` prints one PASS, REVIEW or FIX against the threshold in references/detectors.md. `--voice` compares the
draft with Jed's own samples and says where it drifts. `--log` adds the run to a private local history
(numbers and tell names only), and `--history` shows which tells keep coming back.

Report like this: "AI check: clean. No dashes, 11 words per sentence on average." Don't paste the full
report unless Jed asks. If a finding is a deliberate choice, say so in a few words.

## Read the checker's tiers

- **P0** is what Jed removes every time. Fix it.
- **P1** is a strong tell. Fix it unless Jed chose it.
- **P2** is a weak signal. Look at it, and fix it if it repeats.

A clean score means nothing obvious is left. It does not mean a detector like GPTZero will pass the
text. The goal is writing that sounds like Jed, not text that games a detector.

## Guardrails

- **Never invent facts.** If a number, name, date, quote, example or anecdote is missing, use a
  placeholder or ask. Don't fill a gap with something plausible, and don't add advice, features or
  results the facts don't support. A derived number ("about 500 a day") is still an invented claim.
- **Don't borrow phrases from the samples.** They show the rhythm and warmth. Copying "had the
  privilege of" into every post turns a habit into a tic.
- **Never put another tool, team or person down.**
- **Keep the meaning.** Cutting words must not cut the substance or the caveat that matters.
- **Sensitive data stays out.** Use generic names for clients and people unless Jed gave the name
  for this piece.
- **When polishing Jed's own text,** keep Jed's words. Fix only what the rules require.
- **When unsure between two options,** pick the shorter and plainer one and say so in a line.

## Commands

- `/signature:check <file or text>` runs the checker and reports findings. No rewrite.
- `/signature:polish <file or text>` polishes with minimal changes, then checks.
- `/signature:plan` scans the project and writes `STYLE_PLAN.md`. It changes nothing.
- `/signature:apply` applies only the changes Jed approved in that plan, using `scripts/apply_edits.py`.
- `/signature:verify <file>` checks a changed Word or PowerPoint file in place of opening it.
- `/signature:learn` compares what Claude wrote with what Jed changed it to, and proposes a rule or
  an example. It asks before writing, and keeps the log private.

## Keep this up to date

If Jed corrects something this guide doesn't cover, say so in one line and offer to run
`/signature:learn`. Jed's own repeated corrections are the best evidence this guide has. If a private
log exists at `$CLAUDE_PLUGIN_DATA/corrections.md` or `~/.claude/signature/corrections.md`, skim it
before drafting.
