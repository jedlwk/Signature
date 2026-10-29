# Changelog

## 2.10.0

Edit capture. My edits to what Claude writes become the evidence the guide learns from, with no extra steps.

- **New `scripts/capture.py`.** A hook saves Claude's version of each prose file it writes. Pairing then
  compares it with the latest commit within 14 days and records which of Claude's passages were kept,
  edited or cut. Only passages Claude wrote count.
- **Off until `capture.py enable`.** Everything stays in `~/.claude/signature/`, readable only by me. Pairs
  are kept 90 days. `--exclude`, `.signatureignore` and `--numbers-only` keep sensitive text out.
- **`capture.py report`** shows the share of Claude's words I changed each week, the tells I removed and the
  words I cut and added most.
- **`/signature:learn --from-git`** reads those pairs and proposes rules that repeat, with counts.
- **Wiring.** The plugin runs the hook after Write and Edit and pairs at session start.
  `install.sh --capture` adds the same hooks to `settings.json` for an install without the plugin, and
  keeps a copy of the file first.
- [docs/capture.md](docs/capture.md) explains it.

## 2.9.0

The voice moves into a profile, so the engine works for anyone. Nothing changes for me.

- **`profiles/jed/`** holds my rules (the quick card, moved out of `SKILL.md`), `voice.md`, `samples.md`,
  `examples.md` and a `profile.json` with the checker's settings: which habits to flag, comma limits,
  where exclamation marks are fine, my extra banned words and the checker's wording.
- **The engine's defaults are neutral.** Without a profile it flags general AI tells only. Dashes,
  semicolons, curly quotes and emojis are each one setting in `profile.json`.
- **`profiles/starter/`** is a blank profile to copy. [docs/profiles.md](docs/profiles.md) explains it.
- **Choosing one.** `--profile`, then `SIGNATURE_PROFILE`, then `~/.claude/signature/profile/`, then the
  bundled default, which is mine for now. `--which-profile` prints the one in use.
- **The session reminder** comes from the profile, and so does the name in `plan_scan.py`.
- **A snapshot test** records what the checker says about 116 texts under every register. It was committed
  before the refactor, and every answer is still the same.

## 2.8.0

Three fixes from testing the checker on Jed's own writing. Claude wrote 39 drafts as Jed from the same briefs as
13 of Jed's real passages. Every draft passed the gate, and 3 of Jed's passages did not.

- **A `peer` register.** Replies to classmates now have their own register, with exclamation marks allowed. The
  `course` register gave Jed's own "Hi [name]!!" reply a FIX.
- **Averages wait for four sentences.** Under four, one long sentence sets the whole average, and two of Jed's
  three-sentence paragraphs failed on it. The per-sentence checks still run. Now 12 of the 13 pass. The last has
  a sentence with three commas, which Jed's own rule still flags.
- **`--baseline` with no folder** measures `references/samples.md`. The suggestion is not saved by default, and it
  shouldn't be yet. On Jed's samples it tightens the limits enough that Jed's LinkedIn post fails.
- **Spread in `--voice`.** A new row compares how much sentence lengths vary. Jed's pieces spread 5.2 to 8.1 words.
  The drafts spread 3.5 to 5.3, because they dropped Jed's longer sentences. The row flags 7 of 9 drafts and none
  of Jed's pieces. It was set on that same test, so read it as a nudge.
- The comma advice now shows the actual limit, not always "under 1".

## 2.7.0

Three improvements from studying Emulate and Pangram.

- **One verdict.** `ai_check.py --gate` prints PASS, REVIEW or FIX against the threshold table, so the bar is
  enforced by a command and not only written down.
- **Distance from Jed.** `--voice` compares a draft with the quoted samples in `references/samples.md` and
  reports where it drifts: sentence length, short sentences, commas, first person and exclamation marks.
  Emulate sells voice matching. This does it locally and measurably, for personal writing.
- **A private history.** `--log` records each final check as numbers and tell names, never the text. `--history`
  shows the trend and the tells that keep coming back, which feeds `/signature:learn`. Emulate keeps draft
  history on its servers. This stays on the machine.
- New eval scenario for rewriting without losing the author's own numbers, quotes and examples.

## 2.6.0

A stated threshold for all of Jed's writing, informed by how Pangram works.

- New `references/detectors.md`: what Pangram does and where it is weak, what to take from it, and one
  threshold table. Checker score under 1 overall and under 3 in every passage. If Pangram is used, 95% human
  or more, with 90% to 95% as review.
- `ai_check.py` scores text of 250 words or more in windows of about 120 words and lists hot spots. A hot
  spot makes the exit code 1.
- New optional `scripts/pangram_check.py`. It needs `--send`, a `PANGRAM_API_KEY` in the environment and
  `pangram-sdk`, and refuses text under 50 words. It has not been run against the live service.
- Says plainly that humanizers and synonym swaps are not the fix, and that a course's AI policy comes first.

## 2.5.0

Rewrites keep what Jed wrote, and Sonnet is the minimum model.

- New `ai_check.py --compare OLD NEW`. It scores both versions, lists the tells removed and added, and
  lists every number, quote, code span and name from the old text that the new one lost. It exits 1 if
  something was lost.
- New rule in `SKILL.md`: when rewriting Jed's own text, keep the examples, quotes, numbers and names Jed
  wrote. The workflow checklist runs `--compare` after every rewrite.
- New Model section in `SKILL.md`: write with Sonnet or Opus. Smaller models are no longer a target.

## 2.4.0

Works in any session, and handles Word and PowerPoint when a session can't open them.

- New playbook, `references/office.md`. It tells a session what to do with `.docx` and `.pptx` files based on
  what it has: a shell, python-docx and python-pptx, LibreOffice, computer use in the desktop app, or only
  a chat window. It ends with the lines to report, including what could not be checked.
- New `scripts/verify_office.py`, a check that stands in for opening the file. It tests that the file is intact,
  that only text changed, that the paragraph count is the same, lists each changed paragraph, and warns when
  slide text grew enough to overflow. With LibreOffice installed, `--render` compares page counts and writes
  PNGs. New command `/signature:verify` and personal command `/restyle-verify`.
- The editor flags an edit that makes slide text much longer.
- The restyle now takes any job, such as renaming a term or updating a fact, with the same plan, approval
  and editor. `plan_scan.py --find` lists every place a text appears in every file type.
- New `install.sh`. `--all` installs the skill and commands for Claude Code, copies the skill for Codex, and adds
  a short note to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, so any session knows to use Signature.
  `--project` does the same for one project, and `--uninstall` removes everything.
- New `docs/anywhere.md`: how each kind of session gets Signature, a bootstrap prompt for a session with
  nothing installed, and what to do in a chat with no shell.
- Tested end to end from a bare session that only had the bootstrap prompt. It cloned the repo and wrote a
  good plan, but could not run the cloned scripts, so the plan says what to do when scripts can't run, and
  `docs/anywhere.md` is honest that the bootstrap is a way to start and `./install.sh` is the reliable route.
- A Before text in a plan is words, never markup (an HTML `<title>` tag in a Before text would not match).
- Sessions must not stash, reset or check out Jed's files to see an original. They use `git show HEAD:<path>`.

## 2.3.0

The restyle can now edit everything, not only plan it.

- New editor, `scripts/apply_edits.py`. It makes the approved changes in Markdown, text, Word, PowerPoint,
  HTML, notebooks and source files, with no library and no other skill.
- Word and PowerPoint files are edited by changing only the text inside the XML. Fonts, layout, images,
  comments and compression stay byte for byte as they were. Checked on real decks and documents, and
  opened with python-docx and python-pptx afterwards.
- Exact replacements only. A change that isn't found, or is found twice with no `where`, is skipped and
  reported, never guessed. A Word or PowerPoint file is written only if it still parses and every After
  text reads back.
- Git safety is enforced by the script, not by instructions. A file with uncommitted changes is skipped
  unless `--backup` or `--allow-dirty` is given.
- Code edits must sit inside a comment, a docstring or a sentence-like string, and a Python file must
  still compile. A notebook is edited only if saving it wouldn't reformat it.
- New format layer, `scripts/formats.py`. Slides come in display order with their speaker notes. Every
  unit has a number and a label such as "Slide 3, paragraph 2".
- The scanner reads `.html`, `.ipynb` and `.adoc`, gives each finding a `where` and a `unit`, notes
  slides that are pictures, lists formats it can't edit (such as `.pdf`) with the reason, and takes
  `--strings` to include user-facing text inside code.
- `docs/restyle.md` covers the formats, the editor, its guarantees and its limits.
- 48 new tests, all standard library, so CI needs no Office libraries.

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
