# Restyle a project

How to bring a whole project into Jed's writing style without losing control. Two steps with a hard stop
between them: a plan that changes nothing, then an apply step that does only what was approved.

## Contents
- The flow
- What gets scanned
- Choosing what to leave out
- The scanner
- Approving and applying
- Undoing

## The flow

In any project:

1. Run `/signature:plan`. Claude scans the project, reads its style rules, and writes `STYLE_PLAN.md`.
   Nothing else changes. It stops and waits.
2. Read the plan. Tick the changes you want, edit any After text you'd word differently, and answer
   anything listed under "Needs your input".
3. Run `/signature:apply`. Claude applies only the approved changes, checks the result, and reports.

Without the plugin, the same two steps are `/restyle` and `/restyle-apply`. They are personal commands that
work in every project. Install them with:

```bash
cp docs/personal-commands/*.md ~/.claude/commands/
```

They expect the skill at `~/.claude/skills/jed-writing-style`.

Ask for specific files by naming them: `/signature:plan docs/ README.md`. Add `--code` to include comments
and docstrings in source files. Without it, code is left alone.

## What gets scanned

Prose files: `.md`, `.markdown`, `.txt`, `.rst`, `.docx` and `.pptx`. Inside a git repo the scanner uses
`git ls-files`, so `.gitignore` is respected. Elsewhere it walks the folder.

It skips, and says why:

- Agent and tool files: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `MEMORY.md`, licences and lockfiles.
- Folders like `node_modules`, virtualenvs, build output and anything hidden.
- Text that probably isn't Jed's: sample data, fixtures, transcripts, handouts, readings, syllabi,
  archives and backups. Add `--all` to include them.
- Files over 20,000 words, which are usually logs or data dumps.
- Files that say they were generated.

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
| `--exclude GLOB` | Skip matching paths. Repeatable. |
| `--all` | Don't skip files that look like samples or third-party text. |
| `--top N` | Rows in the table. Default 25. |
| `--max-findings N` | Findings kept per file. Default 20. |
| `--json` | The full result, which is what the plan is written from. |

It prints a folder table first, so you can spot a folder that isn't yours, then the worst files with
their scores. It only reads. It never changes a file.

## Approving and applying

You approve by ticking boxes in `STYLE_PLAN.md`, or by telling Claude: "apply all", "apply file 1",
"apply 1.1 to 1.4", "apply all P0". Nothing is applied that you didn't approve, and "all" is never assumed.

Each change is an exact replacement of the Before text. If a file moved on since the plan was written
and the text no longer matches, that change is skipped and reported. Word and PowerPoint files need the
docx or pptx skill to be edited. If it isn't available, you get paste-ready text instead.

## Undoing

In a git repo, apply refuses to touch a file with uncommitted work, so `git diff` shows exactly what
changed and `git checkout` undoes it. Outside git, the originals are copied to `.signature-backup/`
before anything is edited.
