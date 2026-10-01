---
description: Run the Signature AI-tell checker on a file or pasted text and report what to fix
argument-hint: <file or text> [register]
---

Audit mode. Check this with the jed-writing-style skill: $ARGUMENTS

1. Load the jed-writing-style skill if it isn't loaded.
2. Decide the register from the material: `code`, `doc`, `customer`, `course`, `slides`, `script`,
   `post` or `message`. Use the one the user named. If none was named, infer it from the file type
   and content.
3. Run the checker. The script is at `${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style/scripts/ai_check.py`.
   Pass a file path, or `-` with the text on stdin.
4. Report in this shape, and keep it short:
   - the summary line from the checker
   - P0 findings first, then P1, then P2, each with the line and the fix
   - one line on anything the checker can't judge, such as a flourish at the end of a paragraph
5. Do not rewrite the text. Offer to fix it at the end.
