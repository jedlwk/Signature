# The checker

`ai_check.py` is a style linter. It scans a draft for the patterns that make writing read as machine
made, and gives a score. This page covers every option.

## Contents
- Running it
- Registers
- Options
- Reading the output
- Skipping a passage
- What it is not

## Running it

In Claude Code, the easy way is the command `/signature:check <file or text>`. It runs the checker
and reports the findings.

To run the script yourself, you need Python 3 and nothing else. From a clone of this repo:

```bash
python3 skills/jed-writing-style/scripts/ai_check.py draft.md --register doc
```

After a plugin install there is no clone. The script sits in the plugin cache, under
`~/.claude/plugins/cache/signature/`. Use `/signature:check` instead, or point Python at that path.

More examples:

```bash
python3 skills/jed-writing-style/scripts/ai_check.py deck.pptx --register slides
```

```bash
python3 skills/jed-writing-style/scripts/ai_check.py app.py
```

```bash
pbpaste | python3 skills/jed-writing-style/scripts/ai_check.py - --register post
```

It reads `.md`, `.txt`, `.docx`, `.pptx` and source files (comments and docstrings only), or text on
stdin when the file is `-`.

## Registers

A register is the type of material. It changes what the checker looks for, because a slide, a script
and a customer doc each have different rules. Pass it with `--register`. Without one, the checker
uses `general`, or `code` for source files.

| Register | Use for | What changes |
|---|---|---|
| `code` | Source files, commit messages | Reads comments and docstrings only. Flags narrating comments, emojis and commit filler. No rhythm checks. |
| `doc` | READMEs, reports, one-pagers | Full rhythm checks. Any exclamation mark is flagged. |
| `customer` | Customer docs and Q&A | Everything in `doc`, plus open loops ("we will come back to you") and narrated testing ("we've tested"). | <!-- signature:ignore-line -->
| `course` | Course papers, discussion posts | Full rhythm checks. Any exclamation mark is flagged. |
| `peer` | Replies to classmates, peer comments | Like `course`, but exclamation marks are allowed, as in "Hi [name]!!". |
| `slides` | Decks (`.pptx` works) | Flags any line over 25 words. No sentence rhythm checks. |
| `script` | Speaker and video scripts | Wants about 10 words a sentence and none over 25. Flags brackets, "e.g." and "&". Measures spoken length. |
| `post` | LinkedIn and Medium | Exclamation marks allowed. |
| `message` | Teammate messages and emails | Exclamation marks allowed. |
| `general` | Anything else | The shared checks only. |

`--list-registers` prints this list.

## Options

**Check numbers against the facts.** Invented figures were the most common failure in testing.

```bash
python3 skills/jed-writing-style/scripts/ai_check.py post.md --register post --facts-text "30 HR leaders, no code"
```

`--facts-text` (or `--facts FILE`) flags any number in the draft that is not in the facts. Spelled-out
numbers match, so "ten thousand" equals 10,000. Numbers up to 10 are ignored. It cannot catch an
invented anecdote, so read the draft too.

**Check a script's length.**

```bash
python3 skills/jed-writing-style/scripts/ai_check.py script.md --register script --target-seconds 90
```

It counts only the spoken words, not `[Slide 1]` labels or the length line. It assumes 140 words a
minute, and says how many words the target needs. Within 15 percent counts as a hit.

**Apply safe fixes.**

```bash
python3 skills/jed-writing-style/scripts/ai_check.py draft.md --fix
```

`--fix` prints the text with mechanical fixes only: curly quotes, "in order to", "due to the fact <!-- signature:ignore-line -->
that", "utilise" and a few more. It leaves code, links and ignored passages alone. It never touches <!-- signature:ignore-line -->
dashes or word choices, because the right replacement depends on the sentence. Add `--in-place` to
write the file back. It refuses code, `.docx` and `.pptx` files.

**Calibrate on your own writing.**

```bash
python3 skills/jed-writing-style/scripts/ai_check.py --baseline ~/my-writing --save
```

`--baseline` measures a folder of writing you wrote yourself and suggests thresholds for sentence
length and commas. With no folder, it measures the quoted pieces in `references/samples.md`. Read the
suggestion before you save it. Three short pieces is a small base, and on Jed's samples it suggests
limits tighter than the defaults that Jed's own LinkedIn post then fails. `--save` keeps them in
`~/.claude/signature/calibration.json`, and later checks use them. They stay on your machine. Only measure your own writing, because text a model wrote would teach
the checker the model's habits. `--no-calibration` ignores a saved file, and `--calibration FILE` uses
a different one.

**Output formats.** `--quiet` prints only the summary line. `--json` prints everything as JSON.

**Compare a rewrite with the original.**

```bash
python3 skills/jed-writing-style/scripts/ai_check.py --compare old.md new.md
```

It prints both scores, the tells removed and added, and everything that was in the old text and is gone
from the new: numbers, quoted words, `code` spans and names in the middle of a sentence. Each lost item
is a question, not a verdict. Cut on purpose is fine. It exits 1 if anything was lost or the new score is
still in the fix range.

**Hot spots.** For text of 250 words or more, the checker also scores runs of about 120 words and lists any
that score 3 or more, because one machine-sounding passage can hide in a clean document. A hot spot makes
the exit code 1 even when the whole text is under 3. Details and the full threshold table are in
`skills/jed-writing-style/references/detectors.md`.

**An optional external check.** `scripts/pangram_check.py FILE --send` asks Pangram how it scores the text and
applies the 95% and 90% human-share rule. It sends the text off this computer, so it needs `--send`, a
`PANGRAM_API_KEY` in the environment and `pip install pangram-sdk`. Never use it on confidential text.

**One verdict.** `--gate` prints PASS, REVIEW or FIX against the threshold table in
`references/detectors.md`. FIX means a score of 3 or more, a passage of 3 or more, an invented number or a missed
script length. REVIEW means a score from 1 to 3 or a P0 tell. It exits 1 only on FIX.

**Distance from Jed.** `--voice` compares a draft with the quoted writing in `references/samples.md`: words per
sentence, short sentences, commas, and for posts, messages, peer replies and course text, how often it says "I"
and how many exclamation marks it uses. From six sentences on, it also checks how much sentence lengths vary.
Claude's imitations of Jed came out flatter than Jed, because they dropped the longer sentences. It re-measures
whenever a sample is added. About 500 words is a small base, so read it as a nudge. Documents and slides legitimately differ from a post, so it skips them.

**A private history.** `--log` adds a line to `~/.claude/signature/history.jsonl` with the date, register,
scores and tell names. It never stores the text. `--history` shows whether scores are moving down and which
tells keep coming back, which is what `/signature:learn` should turn into a rule.

## Reading the output

Findings are ranked:

- **P0** is what Jed removes every time: dashes, counted preambles, throat-clearing, chatbot residue,
  open loops, inflated significance.
- **P1** is a strong tell: LLM words, "serves as", "-ing" riders, vague authority, semicolons, <!-- signature:ignore-line -->
  invented numbers.
- **P2** is a weak signal: tidy groups of three, "not X but Y", wordy phrases.

The score is weighted tells per 100 words. Under 1 is clean, 1 to 3 is a few tells, and 3 or more means
fix it before sending. The exit code is 0 for clean or a few tells, 1 for fix it, and 2 when the file
could not be read.

Every threshold in the script has a comment saying why it has that value.

## Skipping a passage

Wrap it in `<!-- signature:ignore-start -->` and `<!-- signature:ignore-end -->`, or end one line with
`<!-- signature:ignore-line -->`. The docs in this repo use this to quote the tells they ban.

## What it is not

It is not an AI detector like GPTZero. A clean score means nothing obvious is left. The goal is
writing that sounds like the author, not text that games a detector.
