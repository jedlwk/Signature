# Changelog

## 2.2.0

Plan first, then change. A new way to bring a whole project into Jed's style without losing control.

- `/signature:plan` scans the project and writes `STYLE_PLAN.md`: every proposed change with the exact
  before, the after and the rule behind it. It changes nothing and waits for approval.
- `/signature:apply` applies only the changes Jed approved, checks them, and updates the plan. It refuses
  to touch files with uncommitted work in git, and backs files up when there is no git.
- New scanner, `scripts/plan_scan.py`. It respects `.gitignore`, skips agent files, sample data,
  transcripts, archives and logs, and ranks files worst first. `.signatureignore` and `--exclude`
  leave things out.
- New Plan mode in `SKILL.md` and a `references/plan.md` with the rules, the plan template and the
  apply steps. Local rules in a project's CLAUDE.md win.
- Personal commands `/restyle` and `/restyle-apply` for use without the plugin, in
  `docs/personal-commands/`.
- New docs: `docs/restyle.md` and `docs/develop.md`. The README keeps only a short Develop section.
- 23 new tests for the scanner and the wiring.

## 2.1.0

Driven by the first real eval run (7 scenarios, with and without the skill, on Haiku, Sonnet and Opus).
Results are in `evals/RESULTS.md`.

- **Invented facts** were the most common failure, so the checker now has `--facts` and `--facts-text`.
  Any number in the draft that is not in the facts is flagged, and spelled-out numbers are matched
  ("ten thousand" equals 10,000).
- **Script length** missed the target in every run, and the skill runs were shorter than the baseline.
  The checker now counts only spoken words and takes `--target-seconds`. It says how many words the
  target needs.
- **Audit mode** groups findings P0, P1, P2. **Polish mode** keeps casing and "!!" in casual messages.
- The code reference has a delete-the-comment test for what versus why.
- `samples.md` warns against copying phrases, after a run copied one verbatim.
- New slash commands: `/signature:check`, `/signature:polish`, `/signature:learn`.
- `/signature:learn` turns Jed's edits into proposed rules, with a private local log.
- Checker: `--fix` for safe mechanical fixes only (curly quotes, "in order to", and similar),
  `--baseline` to measure Jed's own writing and `--save` to keep calibrated thresholds, plus checks
  for a phrase repeated three times and for paragraphs that are all the same length.
- GitHub Actions: tests on every push, and a release workflow that attaches a zip of the skill.
- MIT license.
- README rewritten for a first-time reader: it says who it is for, defines its terms before using them, and
  stays under 200 lines. Every checker option moved to `docs/checker.md`.

## 2.0.0

Restructured to follow Anthropic's skill authoring guide and what the best writing skills do.

- `SKILL.md` is now a short front page: a quick card, five modes, a workflow checklist and a map to
  the reference files. It was a single 370 line file.
- Detail moved to `references/`, one file per topic, linked one level deep from `SKILL.md`: voice,
  AI tells, code, documents, slides, scripts, posts and messages, examples, samples.
- New `samples.md` of real writing to match by ear, and a worked run of the workflow in `examples.md`.
- The checker moved to `scripts/ai_check.py` and was rewritten:
  - findings ranked P0, P1 and P2
  - `--json` output and clear exit codes
  - `<!-- signature:ignore-start -->`, `<!-- signature:ignore-end -->` and `<!-- signature:ignore-line -->` markers
  - correct line numbers in Markdown and source files
  - every threshold has a stated reason
  - a list of short items no longer counts as a comma-heavy sentence
  - a friendly message when a file can't be read
- Added tests with human and AI fixtures, and seven eval scenarios.
- The docs run through their own checker as part of the tests.
- Description rewritten in the third person.
- The plugin is now called `signature`.

## 1.0.0

First version. One `SKILL.md`, one checker, and a session-start reminder hook.
