---
description: Polish text in Jed's voice with minimal changes, then check it
argument-hint: <file or text> [register]
---

Polish mode. Polish this with the jed-writing-style skill: $ARGUMENTS

1. Load the jed-writing-style skill if it isn't loaded, then open the reference for this material.
2. Change as little as the rules require. Keep Jed's words, warmth and structure. Fix spelling,
   clear mistakes and the tells in the AI-tells reference.
3. Do not add facts, praise, sign-offs or new points. Do not formalise a casual message.
4. Run `${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style/scripts/ai_check.py` on the result with the
   right register. Fix what it flags and run it once more.
5. Show the polished text first. Then, in one or two lines, list what you changed and why. If the
   file is on disk, edit it in place only if Jed asked for that.
