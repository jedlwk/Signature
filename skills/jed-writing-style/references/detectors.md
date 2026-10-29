# AI detectors and Jed's threshold

Signature's checker is a style linter. A detector such as Pangram is a different thing, and this page says
how the two fit together and what bar Jed's writing should clear.

## Contents
- What Pangram does
- What to take from it
- The threshold
- Checking with Pangram
- When a text fails
- Limits

## What Pangram does

Pangram is a trained classifier. It reads text in windows of about 500 tokens and labels each stretch
human, AI-assisted or AI-generated. For a whole document it reports the share of each. Its own rule: the text is
human if at least 90% of it is human, AI if at least 80% is AI, and mixed otherwise. It needs 50 words or more.

- It does not use perplexity or burstiness, and it does not compare against a database.
- It trains on human writing paired with AI text on the same topic, then adds the human texts it got wrong
  (hard-negative mining), which is why plain human prose rarely trips it.
- Its published false positive rate is about 1 in 24,000. An independent University of Chicago study agreed
  that false positives were close to zero on medium and long texts, and that humanizer tools did not fool it.
  An Epoch AI test found it missed about 10% of AI text written to imitate particular authors. Most of the
  numbers are from the vendor, so treat them as a direction.
- Its stated weak spots: short text, terse bullets, formulaic text, and the same passage scoring differently
  alone than inside a longer document.

## What to take from it

1. **Read in windows.** One AI-sounding passage can hide inside a clean document. `ai_check.py` now scores
   runs of about 120 words and lists any that score 3 or more as hot spots.
2. **Three labels, not two.** Text Claude drafted and Jed lightly edited is the AI-assisted case. The fix is
   to rewrite it from the facts in Jed's voice, not to swap words.
3. **Substance beats surface.** A detector reads how text was produced, so synonym swaps and humanizer tools
   change little. Don't use them. What works is what the skill already does: Jed's facts, Jed's examples,
   short plain sentences.

## The threshold

For anything written under Jed's name:

| Check | Pass | Review | Fix |
|---|---|---|---|
| `ai_check.py` score, whole text | under 1 | 1 to 3 | 3 or more |
| `ai_check.py` score, worst window | under 3 | | 3 or more |
| Pangram, human share (optional) | 95% or more | 90% to 95% | under 90% |
| Pangram, any window labelled AI | none | | any |

Why these numbers. 90% is Pangram's own line for calling a text human, so 95% leaves room above it. A score
under 1 is the checker's clean band. Anything public (posts, Medium, a
README, a portfolio) should clear every row. Internal notes and messages need only the checker rows.

Short text under 50 words can't go to Pangram, so the checker alone decides.

The checker rows are enforced by one command: `python3 scripts/ai_check.py FILE --register post --gate`.
It prints PASS, REVIEW or FIX. For a post, message, peer reply or course text add `--voice` as well, to see whether
the draft still sounds like Jed's samples and not only whether it avoids tells.

## Checking with Pangram

The free plan allows 20 text checks a day at pangram.com. Paste the finished text there and read the human
share and the highlighted passages. Or run the optional script, which needs `pip install pangram-sdk` and
a `PANGRAM_API_KEY` in the environment:

```bash
python3 scripts/pangram_check.py post.md --send
```

Pangram keeps scan history on its servers. Never send customer, client, H2O-internal or sensitive text, and
never put the API key in a file or a chat. `--send` is required so the text never leaves by accident. The
script has not been run against the live service, so check its first result by hand against the website.

## When a text fails

- Find the passage, not the word. Rewrite it from the facts Jed gave, in plain sentences, then run the checker.
- Put back Jed's own examples, numbers and views if a rewrite lost them (`ai_check.py --compare`).
- If Jed's own, unassisted writing fails, say so and stop. Don't distort good writing to please a detector.
  Pangram's authors note it can't tell people who write like an LLM from an LLM.
- One more pass, then hand it to Jed.

## Limits

- Detectors are statistical. A pass is not proof of anything, and a fail on Jed's own writing is possible.
- Signature helps Jed write in Jed's voice. It is not a way to hide AI authorship where it is not allowed.
  Course work and workplace policies come first. If a course bans AI-drafted text, don't use Claude to draft
  it, whatever a detector says.
