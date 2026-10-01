#!/usr/bin/env python3
"""Score the mechanical part of an eval run.

Usage:
    python3 evals/score.py DIR [DIR ...]

Each DIR holds one output per scenario, named <id>.md (for example linkedin-post.md). The script runs
the checker on each file with the right register and facts, and prints one row per file.

It only covers what a script can judge: dashes, semicolons, exclamation marks, numbers that are not in
the facts, and the spoken length of the script. The rest of evals.json (tone, structure, whether the
answer is honest) still needs a person to read the outputs.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "jed-writing-style" / "scripts"))

import ai_check  # noqa: E402

# Register and the facts each scenario was given. Keep in step with evals.json.
SCENARIOS = {
    "linkedin-post": ("post", "30 HR leaders"),
    "customer-answer": ("customer", "50 frames, 20 frames"),
    "three-slide-deck": ("slides", "5 minute talk, 10,000 documents"),
    "speaker-script": ("script", "5 minute talk, 10,000 documents, 90 seconds"),
    "polish-my-draft": ("message", None),
    "code-comment": ("code", None),
    "audit-only": ("general", None),
}
SCRIPT_TARGET_SECONDS = 90


def score(path, scenario):
    register, facts = SCENARIOS[scenario]
    suffix = ".py" if register == "code" else ""
    text = path.read_text(errors="replace")
    target = SCRIPT_TARGET_SECONDS if scenario == "speaker-script" else None
    result = ai_check.analyse(text, register, suffix, facts=facts, target_seconds=target)
    labels = [f["label"] for f in result["findings"]]
    return {
        "words": result["words"], "score": result["score"], "dashes": labels.count("dash"),
        "semicolons": labels.count("semicolon"), "excl": text.count("!"),
        "invented": labels.count("number not in facts"),
        "spoken_s": result["spoken_seconds"],
    }


def main(dirs):
    if not dirs:
        print(__doc__)
        return 2
    print("%-22s %-17s %5s %6s %5s %5s %5s %8s %8s" % ("run", "scenario", "words", "score", "dash", "semi", "excl", "invented", "spoken"))
    for d in dirs:
        folder = Path(d)
        for scenario in SCENARIOS:
            path = folder / (scenario + ".md")
            if not path.exists():
                print("%-22s %-17s (missing)" % (folder.name[:22], scenario))
                continue
            r = score(path, scenario)
            spoken = "%ds" % r["spoken_s"] if r["spoken_s"] is not None else ""
            print("%-22s %-17s %5d %6.1f %5d %5d %5d %8d %8s" % (
                folder.name[:22], scenario, r["words"], r["score"], r["dashes"], r["semicolons"], r["excl"], r["invented"], spoken))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
