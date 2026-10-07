# Results

Two runs of the seven scenarios in `evals.json`. Run 1 tested version 2.0. Run 2 tested version 2.1,
which fixes what run 1 found. Each cell is one run, so read the numbers as a direction and not as a
measurement.

## Contents
- Summary
- Scores
- What the runs showed
- Plan and apply, end to end
- Description routing test
- Caveats
- Reproduce

## Summary

- The skill helps on every model, and Haiku gained the most between runs.
- The biggest failure was invented content: figures, anecdotes, advice and claims nobody supplied.
  Sonnet and Opus fixed it after version 2.1. Haiku did not.
- Scripts missed their length in every run 1 output. After the fix they land within 15 percent.
- Dashes and semicolons were never the problem. Every output was clean on both, with or without the skill.
- Use Sonnet or Opus to write under Jed's name. Haiku is fine for running the checker and for audits.

## Scores

Lines of the rubric met, out of 41. The baseline is Sonnet with no skill.

| | Baseline | Sonnet | Haiku | Opus |
|---|---|---|---|---|
| Run 1 (v2.0) | 27 | 36 | 28 | 38 |
| Run 2 (v2.1) | | 40 | 36 | 41 |

By scenario, with the number of rubric lines in brackets:

| Scenario | Baseline | Sonnet 1 | Sonnet 2 | Haiku 1 | Haiku 2 | Opus 1 | Opus 2 |
|---|---|---|---|---|---|---|---|
| LinkedIn post (6) | 3 | 5 | 5 | 5 | 5 | 5 | 6 |
| Customer answer (8) | 4 | 7 | 8 | 6 | 6 | 8 | 8 |
| Three slides (7) | 6 | 7 | 7 | 4 | 6 | 7 | 7 |
| Speaker script (7) | 6 | 5 | 7 | 5 | 6 | 6 | 7 |
| Polish my draft (5) | 4 | 5 | 5 | 3 | 5 | 5 | 5 |
| Code comment (4) | 1 | 4 | 4 | 3 | 4 | 4 | 4 |
| Audit only (4) | 3 | 3 | 4 | 2 | 4 | 3 | 4 |

Two measured numbers, from `score.py`:

| | Baseline | Sonnet 1 to 2 | Haiku 1 to 2 | Opus 1 to 2 |
|---|---|---|---|---|
| Script length (target 90 seconds) | 81 | 73 to 90 | 58 to 89 | 79 to 82 |
| Scenarios with nothing invented (of 4) | 2 | 2 to 4 | 0 to 0 | 2 to 4 |

## What the runs showed

**1. Invented content was the top failure.** The baseline invented a four-step checklist, "about an
hour" and "four in the afternoon". The skill in run 1 still produced "twelve thousand", "send two
requests of 20 and one of 10" and "one team I worked with". Rules alone were not enough, because the
model fills gaps without noticing. What changed in 2.1: a workflow step that lists the facts first, a
placeholder rule, a checker flag for any number not in the facts (`--facts-text`), and new patterns
for narrated testing ("we've tested") and invented anecdotes.

**2. Script length missed in every run 1 output**, and the skill outputs were shorter than the
baseline. Models guessed their own word count. What changed: `--target-seconds` counts only the
spoken words and says how many words the target needs. Run 2 scripts landed at 90, 89 and 82 seconds.

**3. Audit output was ungrouped.** The skill said to report findings but not how. Run 2 outputs group
by P0, P1 and P2.

**4. Polish changed the tone on Haiku.** It capitalised the opener and cut "!!" to "!". The mode now
says to keep casing and "!!" in casual messages. Run 2 kept both.

**5. Why-comments.** Haiku wrote `# log returns from close price`, which says what. The code
reference now has a delete-the-comment test. Run 2 wrote a why.

**6. A sample was copied.** Haiku opened a post with the sample's first line and reused its second.
`samples.md` now warns against it. Run 2 still did it, so smaller models may need the samples left
out of the first draft. Not fixed.

**7. Haiku still invents.** In run 2 it wrote "a spreadsheet and a few prompts", "in every request
we've tested" and a burnout story. The facts flag catches numbers only. It cannot catch an anecdote.
Hence the model advice in the summary.

**8. Placeholders are the cost of honesty.** Sonnet and Opus left bracketed placeholders in slides
and the script instead of making content up. That is the intended behaviour, but it means more
back and forth. The LinkedIn post from Sonnet 2 is thin for the same reason.

## Plan and apply, end to end

Separate from the writing evals above, the plan-first restyle was run end to end by fresh Sonnet agents on
throwaway projects, and each result was checked by hand afterwards. Three runs, one project each.

| Run | What it tested | Result |
|---|---|---|
| Style, Markdown and text | Plan, tick three boxes, apply | Only the ticked items changed. Project rules and a legal file were respected |
| Style, a mixed project | Word, PowerPoint, HTML, a notebook, Markdown and Python in one plan | 11 of 12 applied. The twelfth kept a placeholder, so the editor refused it. Word and PowerPoint formatting intact |
| Rename, from a bare session | Only the bootstrap prompt, then plan, tick five, apply through the installed commands | The plan held back a customer quote, a package name and four ambiguous items. Apply changed only the five ticked ones |

What these runs found and fixed: the editor and the plan numbered HTML and notebook locations
differently, code edits failed when the Before text included a `#` or quotes, a NEEDS FACT item would have
written its placeholder, a stale "Nothing has been changed yet" line was left in the plan, and a session tried
`git stash` on the project. The bare session could clone the repo but could not run the cloned scripts, so it
built its plan by hand and said so.

Not tested: a session that opens Word or PowerPoint through computer use, a Codex session, Claude.ai, and a
chat with no shell. The playbook for those is written from how the tools work, and unproven.

## Description routing test

A Haiku agent saw the skill's description next to seven other skills' descriptions and picked which to
load for 19 requests (`trigger-queries.json`). All 19 were right: 10 of 10 writing requests loaded
the skill, and 9 of 9 unrelated ones did not. The spreadsheet and PDF requests went to their own
skills. This is one weak router on a small set, so add a query whenever the skill loads when it
shouldn't or stays quiet when it should.

## Caveats

- One run per cell. Differences of one or two lines are noise.
- Scored by one reader (me, Claude), against a rubric I wrote. The same model family wrote the
  outputs and scored them.
- The rubric changed after run 1. I added a line for invented content, tightened the script length
  line and the audit grouping line, and then rescored run 1 against the new rubric. That makes run 1
  look slightly worse than it would have under the original, and it is the main reason the gap
  between runs is real but not large. The rubric in `evals.json` is the revised one.
- The test agents did not have the session-start hook, so whether the skill loads on its own in a
  real session is only covered by the routing test.
- The outputs used placeholder facts about a workshop and a talk. Real tasks have richer facts and
  would suffer less from the thin outputs.
- The raw outputs are in `runs/` so anyone can score them again.

## Reproduce

```bash
python3 evals/score.py evals/runs/run-1/baseline evals/runs/run-2/sonnet
```

That prints the measured columns. For the rubric lines, read each output against `evals.json`. To
run it again, follow `README.md` in this folder.
