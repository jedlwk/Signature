#!/usr/bin/env python3
"""Start every session with a short reminder to use the jed-writing-style skill.

A skill only loads when Claude decides it is relevant. This reminder makes that decision
automatic for anything written under Jed's name. It adds one short paragraph of context,
touches no files and makes no network calls.
"""
import json

REMINDER = (
    "Writing rule for this session: anything written under Jed's name (code comments, commit messages, "
    "READMEs, docs, slides, scripts, posts, messages, assignments) follows the jed-writing-style skill. "
    "Load it before drafting. Core rules: warm and plain, point first, no em or en dashes, under one comma "
    "per sentence, no semicolons, no LLM words or tidy groups of three, never invent facts. Run the "
    "skill's scripts/ai_check.py on finished drafts. Local project rules (CLAUDE.md, rubrics, repo "
    "conventions) win where they differ."
)

print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": REMINDER}}))
