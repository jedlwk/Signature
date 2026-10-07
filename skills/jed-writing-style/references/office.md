# Word and PowerPoint: what to do in any session

How to change and check `.docx` and `.pptx` files, whatever this session can and can't do. Most sessions
can't open Word or PowerPoint, so this page tells you what to do instead, and what to hand to Jed.

## Contents
- Know what you have
- The ladder
- The rules for every session
- Checking a change
- Sessions that can open Word or PowerPoint
- Sessions with no shell
- What to tell Jed

## Know what you have

Run these once at the start and write down the answers. They decide which rung of the ladder you are on.

```bash
python3 --version
python3 -c "import docx, pptx; print('python-docx and python-pptx are installed')"
which soffice libreoffice
git rev-parse --is-inside-work-tree
```

Also ask yourself: can this session run commands, read and write files, and see the screen? A desktop
session with computer use can open apps. A chat window with no tools can only talk.

## The ladder

Start at the top and use everything you have. Each rung adds a check. None of them replaces the editor.

| You have | Do this |
|---|---|
| **A shell and Python 3** (the minimum) | Make every change with `scripts/apply_edits.py`. Check it with `scripts/verify_office.py`. |
| **python-docx or python-pptx** | Nothing extra. `verify_office.py` opens the file with them on its own. |
| **LibreOffice** (`soffice`) | Add `--render DIR` to `verify_office.py`. It converts the file to PDF, compares page counts and writes PNGs of the pages. Look at the PNGs of the changed slides. |
| **Computer use** (the Claude desktop app) | After the script has edited the file, open a copy in Word or PowerPoint and look. See the next sections. |
| **No shell, no files** (a chat window) | Give Jed a find and replace table to apply by hand. See "Sessions with no shell". |

## The rules for every session

- **Edit with `apply_edits.py` and nothing else.** It changes only the text inside the file's XML, so
  formatting, images and layout stay as they were.
- **Never save a Word or PowerPoint file with python-docx or python-pptx.** They rewrite the whole
  package and can drop things they don't know about. Use them to read, never to write.
- **Never unzip, edit with sed and zip again.** A wrong zip order or compression setting can make the file
  unopenable. The editor keeps those exactly.
- **Work on a copy if you are unsure.** Copy the file, run the editor on the copy, check it, then replace
  the original.
- **If the editor says unsupported, stop and tell Jed.** Don't improvise with another tool.
- **You can't promise it looks right.** Say what you checked and what you couldn't.

## Checking a change

Run this after every edit, once per changed file. In a git repo use `--git`. Outside git, compare with the
backup the editor made.

```bash
python3 scripts/verify_office.py deck.pptx --git
python3 scripts/verify_office.py deck.pptx --against .signature-backup/<timestamp>/deck.pptx
```

Read the result like this.

| Line | If it fails or warns |
|---|---|
| `intact` fails | Restore the original at once and tell Jed. The file would not open. |
| `text only` fails | More than text changed. Restore the original and tell Jed. |
| `paragraphs` fails | A paragraph was added or lost. Restore the original and tell Jed. |
| `growth` warns | The text on a slide grew a lot and may run out of its box. Name those slides to Jed, or shorten the After text. |
| `render` warns | The page count changed. Look at the PNGs, and tell Jed which pages moved. |
| `opens` fails | Restore the original and tell Jed. |

Add `--render out/` when LibreOffice is installed. Then look at the PNGs yourself with the image viewer
you have, starting with the slides in the growth warning. You are checking for text cut off, text
spilling out of a box, and a layout that has visibly moved.

## Sessions that can open Word or PowerPoint

This applies to a desktop session with computer use. Read the computer-use skill first, and ask Jed before
you open any app.

1. Make the edit with `apply_edits.py` and check it with `verify_office.py`. Do that before opening anything.
2. Open a **copy** of the changed file in Word or PowerPoint, never the only copy.
3. If a repair prompt appears, stop. Close it, restore the original, and tell Jed.
4. Look at each changed slide or page. Check for text running out of its box, a font that looks different,
   and a layout that moved.
5. For a Word file, use Review, Compare, Compare... with the original to see the changes in place.
6. Close without saving. Don't fix anything by hand in the app. If something looks wrong, change the After
   text and run the editor again.
7. Report what you saw, and name any slide you didn't look at.

## Sessions with no shell

You can't run the editor, so Jed will apply the changes. Give them one table per file, in the order they
appear, with the exact words.

| # | Where | Find | Replace with |
|---|---|---|---|
| 1 | Slide 3, paragraph 2 | the exact Before text | the exact After text |

Tell Jed how to apply each one:

- **Word:** Home, Replace (Ctrl+H, or Cmd+Shift+H on a Mac). Paste into Find what and Replace with. Use
  Replace, not Replace All, unless the table says all. Check each one.
- **PowerPoint:** Home, Replace (Ctrl+H). The same steps. Check the speaker notes by hand, because Replace
  may not reach them.
- Find and replace normally keeps the formatting of the text it replaces, and finds text that is split across
  formatting changes. Check the first few.
- Text inside a text box or a shape may not be found. If it isn't, edit it by hand.

For a chat that can see pasted text, you can still write the whole plan. Ask Jed to paste the file's text,
and number each paragraph yourself.

## What to tell Jed

End every Word or PowerPoint job with these lines, filled in. Don't skip the ones you couldn't do.

```text
Changed: <files and how many paragraphs>
Checked: intact, text only, paragraph count, opens in <library or not installed>
Rendered: <page count before and after, or "not possible, LibreOffice is not installed">
Looked at: <slides or pages you saw, or "nothing, I can't open Word or PowerPoint here">
Please check: open <file> once, confirm there is no repair prompt, and look at <slides in the growth warning>.
Undo: <git checkout path, or the backup folder>
```
