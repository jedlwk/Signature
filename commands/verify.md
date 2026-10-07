---
description: Check a changed Word or PowerPoint file in place of opening it, and say what a person should still look at
argument-hint: <file.docx or file.pptx> [--render DIR]
---

Verify mode. Check this file with the jed-writing-style skill: $ARGUMENTS

Load the jed-writing-style skill and follow `references/office.md`.

1. Work out what this session has: Python version, python-docx and python-pptx, LibreOffice, git. That decides
   how far you can check.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style/scripts/verify_office.py <file> --git`. Outside git, use `--against` with the original.
   Add `--render <folder>` if LibreOffice is installed, and look at the PNGs it writes.
3. Read each line as `references/office.md` says. If it is intact, text only, paragraph count or opens fails,
   restore the original from git or the backup and tell Jed. Don't touch any other file.
4. End with the report lines from `references/office.md`, including what you could not check.
