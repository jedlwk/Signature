#!/usr/bin/env python3
"""Optional last check: ask Pangram how its detector scores a text, and apply Jed's threshold.

This sends the text to Pangram's servers, so it only runs with --send, and never on anything
confidential, customer-facing or internal. It needs `pip install pangram-sdk` and a PANGRAM_API_KEY
in the environment. The key is never read from or written to a file here.

Threshold (see references/detectors.md):
    fraction_human >= 0.95            pass
    0.90 to 0.95                      review the flagged windows
    below 0.90                        fail (Pangram itself would call it mixed or AI)
    any window labelled AI            listed whatever the total

Texts under 50 words can't be analysed by Pangram. Use ai_check.py for those.

Exit codes: 0 pass, 1 review or fail, 2 could not run.
"""
import argparse
import os
import sys
from pathlib import Path

__version__ = "1.0.0"

PASS_AT = 0.95
REVIEW_AT = 0.90
MIN_WORDS = 50


def gate(result):
    """Turn a Pangram result into (verdict, reasons). Works on the fields the SDK documents."""
    human = float(result.get("fraction_human", 0.0))
    ai = float(result.get("fraction_ai", 0.0))
    assisted = float(result.get("fraction_ai_assisted", 0.0))
    ai_windows = [w for w in result.get("windows", []) if "ai" in str(w.get("label", "")).lower()
                  and "human" not in str(w.get("label", "")).lower()]
    reasons = ["human %.0f%%, AI-assisted %.0f%%, AI %.0f%%" % (human * 100, assisted * 100, ai * 100)]
    if human >= PASS_AT:
        verdict = "pass"
    elif human >= REVIEW_AT:
        verdict = "review"
        reasons.append("between %.0f%% and %.0f%% human: read the flagged windows" % (REVIEW_AT * 100, PASS_AT * 100))
    else:
        verdict = "fail"
        reasons.append("under %.0f%% human, which Pangram's own rule calls mixed or AI" % (REVIEW_AT * 100))
    if ai_windows and verdict == "pass":
        verdict = "review"
    if ai_windows:
        reasons.append("%d window(s) labelled AI or AI-assisted" % len(ai_windows))
    return verdict, reasons


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="text, Markdown or .docx/.pptx file to check")
    ap.add_argument("--send", action="store_true", help="confirm the text may leave this computer")
    ap.add_argument("--version", action="version", version="pangram_check " + __version__)
    args = ap.parse_args(argv)

    if not args.send:
        print("pangram_check: this sends the text to Pangram. Re-run with --send if it is yours to send and is not "
              "confidential, customer or internal.", file=sys.stderr)
        return 2
    if not os.environ.get("PANGRAM_API_KEY"):
        print("pangram_check: set PANGRAM_API_KEY in your environment first.", file=sys.stderr)
        return 2
    try:
        from pangram import Pangram
    except ImportError:
        print("pangram_check: run `pip install pangram-sdk` first.", file=sys.stderr)
        return 2
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ai_check
    try:
        text = ai_check.strip_markup(ai_check.read_text(args.file))
    except Exception as e:
        print("pangram_check: cannot read %s: %s" % (args.file, e), file=sys.stderr)
        return 2
    if len(text.split()) < MIN_WORDS:
        print("pangram_check: Pangram needs at least %d words. Use ai_check.py for short text." % MIN_WORDS, file=sys.stderr)
        return 2
    result = Pangram().predict(text)
    verdict, reasons = gate(result)
    print("Pangram: %s. %s." % (verdict.upper(), ". ".join(reasons)))
    for w in result.get("windows", []):
        label = str(w.get("label", ""))
        if "human" not in label.lower():
            span = ""
            if "start_index" in w and "end_index" in w:
                span = ': "%s..."' % text[w["start_index"]:w["end_index"]][:80].replace("\n", " ")
            print("  %s (confidence %s)%s" % (label, w.get("confidence", "?"), span))
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
