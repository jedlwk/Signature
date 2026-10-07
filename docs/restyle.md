# Restyle a project

How to bring a whole project into Jed's writing style without losing control. Two steps with a hard stop
between them: a plan that changes nothing, then an apply step that does only what was approved.

## Contents
- The flow
- Other jobs, not only style
- What it covers
- Choosing what to leave out
- The scanner
- The editor
- Approving and applying
- Limits
- Undoing

## The flow

In any project:

1. Run `/signature:plan`. Claude scans the project, reads its style rules, and writes `STYLE_PLAN.md`.
   Nothing else changes. It stops and waits.
2. Read the plan. Tick the changes you want, edit any After text you'd word differently, and answer
   anything listed under "Needs your input".
3. Run `/signature:apply`. Claude applies only the approved changes, checks the result, and reports.

Without the plugin, the same steps are `/restyle`, `/restyle-apply` and `/restyle-verify`. They are personal
commands that work in every project. `./install.sh --claude` puts them in `~/.claude/commands`, or copy
`docs/personal-commands/*.md` there yourself. They expect the skill at `~/.claude/skills/jed-writing-style`.
[docs/anywhere.md](anywhere.md) covers every other kind of session.

Ask for specific files by naming them: `/signature:plan docs/ README.md`. Add `--code` to include comments
and docstrings in source files, or `--strings` to include user-facing text inside code as well.

## Other jobs, not only style

The plan, the approval and the editor work for any change across a project. Say the job in plain words
after the command.

```text
/signature:plan rename Acme to Zenith
/signature:plan change 40 users to 55
/signature:plan anonymise the client names
/signature:plan cut every slide to two lines
```

For a rename or a fact, the scanner's `--find` option lists every place the text appears, in every file type,
with the unit number the editor needs. The plan then lists each place for you to tick. With no job stated, the
job is your writing style.

## What it covers

Every kind of writing in a project that can be edited safely. It needs no other skill or library.

| File type | What is read and edited |
|---|---|
| `.md` `.markdown` `.txt` `.rst` `.adoc` | The whole text |
| `.docx` | Body, headers, footers, footnotes and endnotes. Only the text changes |
| `.pptx` | Every slide in display order, and the speaker notes. Only the text changes |
| `.html` `.htm` | Visible text. Never tags, attributes, scripts or styles |
| `.ipynb` | Markdown cells |
| Source files, with `--code` | Comments and docstrings |
| Source files, with `--strings` | Comments, plus quoted strings that read like sentences, such as error messages and UI copy |

Listed in the plan with the reason, but not edited: `.pdf` (edit the file it was made from), `.xlsx`, and
the old `.doc` and `.ppt` formats (save as `.docx` or `.pptx` first). A slide that is a picture has no
editable text, and the plan says how many there are.

It skips, and says why:

- Agent and tool files: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `MEMORY.md`, `STYLE_PLAN.md`, licences and lockfiles.
- Folders like `node_modules`, virtualenvs, build output and anything hidden.
- Text that probably isn't Jed's: sample data, fixtures, transcripts, handouts, readings, syllabi,
  archives and backups. Add `--all` to include them.
- Files over 20,000 words, which are usually logs or data dumps.
- Files that say they were generated.

Inside a git repo the scanner uses `git ls-files`, so `.gitignore` is respected.

## Choosing what to leave out

Put patterns in a `.signatureignore` file in the project root, one per line. Lines starting with `#`
are comments. A pattern without a slash matches a name at any depth.

```text
# text someone else wrote
vendor-docs
legacy/*
CHANGELOG.md
```

Or pass `--exclude "legacy/*"` on one run. It can be repeated.

## The scanner

You don't have to run it by hand, because the plan command does. To see what it finds, run this from the
project folder:

```bash
python3 skills/jed-writing-style/scripts/plan_scan.py
```

| Option | What it does |
|---|---|
| `paths` | Scan only these files or folders. |
| `--code` | Also read comments and docstrings in source files. |
| `--strings` | Also read user-facing strings in source files. Implies `--code`. |
| `--exclude GLOB` | Skip matching paths. Repeatable. |
| `--find TEXT` | List every place the text appears, in every file type, instead of scoring style. |
| `--regex` | With `--find`, treat the text as a regular expression. |
| `--ignore-case` | With `--find`, ignore upper and lower case. |
| `--all` | Don't skip files that look like samples or third-party text. |
| `--top N` | Rows in the table. Default 25. |
| `--max-findings N` | Findings kept per file. Default 20. |
| `--json` | The full result, which is what the plan is written from. |

It prints a folder table first, so you can spot a folder that isn't yours, then the worst files with
their scores. Every finding carries a `where` label (such as "Slide 3, paragraph 2") and a `unit`
number the editor can use. It only reads. It never changes a file.

## The editor

`apply_edits.py` makes the approved changes. Claude writes the approved items to an `edits.json` file and
runs it, so no file is ever edited by hand.

```bash
python3 skills/jed-writing-style/scripts/apply_edits.py edits.json --dry-run
```

```bash
python3 skills/jed-writing-style/scripts/apply_edits.py edits.json
```

| Option | What it does |
|---|---|
| `--dry-run` | Report what would change. Write nothing. |
| `--backup DIR` | Copy each original into DIR before changing it. |
| `--allow-dirty` | Edit files that have uncommitted changes in git. |
| `--root DIR` | The project folder. Edits may not leave it. Default: the current folder. |
| `--units FILE` | List a file's units with their numbers and labels, then exit. |
| `--json` | Print the report as JSON. |

Each edit has an `id`, a `file`, the `before` text and the `after` text. Two optional fields narrow it:
`where` (a unit number, a line, or a label such as "Slide 3") and `all` (replace every match).

```json
{"edits": [
  {"id": "1.1", "file": "README.md", "before": "In order to start", "after": "To start"},
  {"id": "2.3", "file": "deck.pptx", "before": "seamless", "after": "smooth", "where": "Slide 3"},
  {"id": "3.1", "file": "docs/old.md", "before": "serves as", "after": "is", "all": true}
]}
```

What it guarantees:

- **Exact replacements only.** The Before text must be found exactly. A change that isn't found, or is found
  more than once with no `where` or `all`, is skipped and reported. It never guesses a nearby match.
- **Word and PowerPoint keep everything but the text.** The editor changes only the text inside the
  document's XML. It is never re-saved by a library, so fonts, layout, images, comments, theme and
  compression all stay as they were. New text goes into the first run it touches, so it takes that run's
  formatting.
- **A Word or PowerPoint file is written only if it still parses.** Each changed part is checked as XML,
  the new file is read back, and every After text must be found in it. Otherwise the original stays.
- **Code stays code.** In a source file, a change must sit inside a comment, a docstring or (with
  `--strings`) a sentence-like string. A Python file must still compile afterwards.
- **Gaps stay gaps.** An After text that still has a `[bracketed placeholder]` (a NEEDS FACT item) is skipped
  until someone fills it in, so a placeholder is never written into a deck or a document.
- **Git can always undo it.** In a git repo, a file with uncommitted changes, or one git doesn't know yet,
  is skipped. Pass `--backup DIR` to keep a copy and edit it anyway, or `--allow-dirty`.
- **A skipped change never stops the others.** Each ends as `applied`, `not_found`, `ambiguous`,
  `unsupported` or `error`, with the reason.

## Checking Word and PowerPoint files

I can't open Word or PowerPoint in most sessions, so `verify_office.py` checks a changed file in their place.
`/signature:verify <file>` runs it.

```bash
python3 skills/jed-writing-style/scripts/verify_office.py deck.pptx --git
```

It needs no libraries. It checks that the file is intact (the zip, every XML part, every internal link), that only
text changed, that the paragraph count is the same, and lists every changed paragraph before and after. It warns
when text on a slide grew enough to overflow its box. If python-docx or python-pptx is installed it opens the file
with them. If LibreOffice is installed, `--render DIR` converts the file to PDF, compares page counts, and writes
PNGs a session can look at.

`references/office.md` is the playbook a session follows. It says what to do on each rung: a shell, the
libraries, LibreOffice, computer use in the desktop app (open a copy, look, close without saving) or a chat
with no shell (a find and replace table for Jed to apply by hand). It ends with the lines to report: what was
checked, what was looked at, and what Jed should check.

## Approving and applying

You approve by ticking boxes in `STYLE_PLAN.md`, or by telling Claude: "apply all", "apply file 1",
"apply 1.1 to 1.4", "apply all P0". Nothing is applied that you didn't approve, and "all" is never assumed.

## Limits

- **Tested without Word or PowerPoint.** Edited files are checked byte by byte, parsed as XML, and opened with
  python-docx and python-pptx, but not opened in Word or PowerPoint themselves. `verify_office.py` and the playbook
  narrow the risk, and they don't remove it. Open a changed file once and look before you rely on it.
- **No tracked changes.** Edits are made directly. The plan is the review, and git or the backup is the undo.
- **One paragraph at a time.** In Word and PowerPoint, a change can't span two paragraphs, a tab or a line
  break. Longer edits are split in the plan.
- **Text in charts, SmartArt, images and some text boxes can't be reached.** If a deck is mostly pictures,
  the plan says so.
- **Notebooks are edited only if saving them wouldn't reformat them.** Otherwise they are skipped with that
  reason.
- **HTML text with entities** (such as `&amp;`) must be edited as it appears in the source.

## Undoing

In a git repo, the editor refuses to touch a file with uncommitted work, so `git diff` shows exactly what
changed and `git checkout` undoes it. Outside git, the originals are copied to `.signature-backup/`
before anything is edited.
