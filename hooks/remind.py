#!/usr/bin/env python3
"""Start every session with a short reminder to use the jed-writing-style skill.

A skill only loads when Claude decides it is relevant. This reminder makes that decision
automatic for anything written under the writer's name. The text comes from the active profile's
"reminder", so each writer's own rules are the ones repeated. It adds one short paragraph of
context, touches no files and makes no network calls.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "jed-writing-style" / "scripts"))

try:
    import ai_check
    reminder = ai_check.PROFILE.reminder
except Exception:  # a broken install must never block a session from starting
    reminder = ("Writing rule for this session: anything written under the user's name follows the "
                "jed-writing-style skill. Load it before drafting, and run its scripts/ai_check.py on finished drafts.")

if reminder:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": reminder}}))
