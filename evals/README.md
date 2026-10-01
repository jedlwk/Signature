# Evals

Scenarios for checking that the skill actually changes what Claude writes. Anthropic's guide says to
build evaluations first and to test with real tasks, so these come before any new rule.

## How to run one

1. Open a fresh Claude Code session without the plugin. Paste the `query`. Save the output as the
   baseline.
2. Install the plugin and open a fresh session. Paste the same `query`. Save that output.
3. Score both outputs against `expected_behavior`, one line at a time. Count how many each one meets.
4. Run `ai_check.py` on both outputs with the register named in the scenario. The skill's output
   should score lower.

The skill is working when the second output meets more lines than the first, and the gap is
visible without squinting. If a line still fails with the skill on, that is the next thing to fix.

## Adding a scenario

Add one when Jed corrects something twice. Write the query that triggered it, then the lines Jed
would check. Keep each line observable, so two people would score it the same way.

## Models

Anthropic recommends testing on every model you plan to use. Run the scenarios on Haiku, Sonnet
and Opus. Haiku needs enough guidance, and Opus should not be over-explained.
