#!/usr/bin/env python3
"""The checker must give the same answers after a refactor.

cases.json holds frozen inputs: the test fixtures, the skill's docs as of 2.8.0, and 91 texts from the
voice test (13 of Jed's passages, 39 Claude drafts written with the skill, 39 without). expected.json holds
what the checker said about each one under every register, with Jed's profile. A change that moves any
score, flag, message or voice row fails here.

After a change that is meant to move the output, rewrite the expectations and read the diff:
    python3 tests/test_golden.py --write
"""
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "tests" / "fixtures" / "golden"
sys.path.insert(0, str(ROOT / "skills" / "jed-writing-style" / "scripts"))
os.environ.setdefault("SIGNATURE_PROFILE", "jed")

import ai_check  # noqa: E402

PROSE = ["general", "doc", "customer", "course", "peer", "post", "message", "script", "slides"]


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def outcome(case, register):
    text, suffix = case["text"], case.get("suffix", "")
    r = ai_check.analyse(text, register, suffix, facts=case.get("facts"))
    r["windows"] = ai_check.window_scores(text, register, suffix)
    r["worst_window"] = max([w["score"] for w in r["windows"]] or [0])
    r["gate"] = ai_check.gate(r)
    r["voice"] = ai_check.voice_check(text, register, ai_check.voice_profile())
    return r


def snapshot():
    cases = json.loads((GOLDEN / "cases.json").read_text())
    out = {}
    for case in cases:
        registers = ["code"] if case.get("suffix") in ai_check.CODE_EXT else PROSE
        for register in registers:
            r = outcome(case, register)
            # the case's own register is kept in full so a failure shows what moved. The rest as a hash.
            out["%s|%s" % (case["name"], register)] = r if register == case["register"] else digest(r)
        if case["register"] != "code":
            out["%s|fix" % case["name"]] = ai_check.fix_text(case["text"])
    rows, suggestion = ai_check.measure_folder(ai_check.SAMPLES_PATH)
    out["baseline"] = {"rows": [[n, digest(r)] for n, r in rows], "suggestion": suggestion}
    out["voice_profile"] = ai_check.voice_profile()
    out["registers"] = {k: list(v) for k, v in ai_check.REGISTERS.items()}
    out["register_help"] = ai_check.REGISTER_HELP
    return json.loads(json.dumps(out))


class Golden(unittest.TestCase):
    maxDiff = 4000

    def test_same_answers_as_recorded(self):
        expected = json.loads((GOLDEN / "expected.json").read_text())
        got = snapshot()
        self.assertEqual(sorted(got), sorted(expected))
        for key in expected:
            with self.subTest(key):
                self.assertEqual(got[key], expected[key])


if __name__ == "__main__":
    if "--write" in sys.argv:
        (GOLDEN / "expected.json").write_text(json.dumps(snapshot(), indent=1, sort_keys=True) + "\n")
        print("wrote", GOLDEN / "expected.json")
    else:
        unittest.main()
