# Changelog

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
