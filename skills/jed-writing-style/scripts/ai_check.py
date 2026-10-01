#!/usr/bin/env python3
"""Flag the AI tells Jed keeps asking to remove.

Usage:
    python3 ai_check.py draft.md
    python3 ai_check.py deck.pptx --register slides
    python3 ai_check.py script.md --register script
    python3 ai_check.py app.py                 (source files: comments and docstrings only)
    pbpaste | python3 ai_check.py - --register post
    python3 ai_check.py draft.md --json        (machine-readable output)
    python3 ai_check.py --list-registers

Skip a passage with <!-- signature:ignore-start --> ... <!-- signature:ignore-end -->, or skip one
line by adding <!-- signature:ignore-line --> at the end of it. Docs use this to quote the tells they ban.

Exit codes: 0 clean or a few tells, 1 fix before sending, 2 could not read the input.

This is a style linter, not an AI detector like GPTZero. It counts patterns Jed has struck out in
past drafts and gives a rough score. A clean result means "nothing obvious", not "human".
"""
import argparse
import json
import re
import statistics
import sys
import zipfile
from collections import namedtuple
from pathlib import Path

__version__ = "2.0.0"

# ---------------------------------------------------------------------------
# Thresholds. Each value has a reason so nobody has to guess what it means.
# ---------------------------------------------------------------------------

# Score is weighted tells per 100 words. Under 1 is about one minor tell in a page.
CLEAN_BELOW = 1.0
# At 3 or more the text has several strong tells in a page, which Jed always sends back.
FIX_AT = 3.0
# Each rhythm problem (too long, too uniform) adds half a tell-per-100-words to the score.
RHYTHM_PENALTY = 0.5
# Jed's approved customer doc averages 13 words a sentence. Above 18 reads stiff.
DEFAULT_MEAN_CAP = 18
# A spoken sentence longer than this is hard to say in one breath.
SCRIPT_MEAN_CAP = 14
SCRIPT_LONG_CAP = 25
# In the approved customer doc, seven of 188 sentences exceed 30 words.
DEFAULT_LONG_CAP = 30
# A hand-written page has varied lengths. A standard deviation under 4 means every sentence is alike.
MIN_STDEV = 4.0
# Fewer than six sentences is too small a sample to judge rhythm.
MIN_SENTENCES_FOR_RHYTHM = 6
# Jed asked twice for fewer commas. His approved doc sits at 0.73 per sentence.
MAX_COMMAS_PER_SENTENCE = 1.0
# A sentence with three or more commas is the one to split.
HEAVY_COMMAS = 3
# But a list of short items ("naming, comment density, idiom, formatter") is not a chain of clauses.
# If the typical comma-separated piece is this many words or fewer, treat the sentence as a list.
LIST_ITEM_WORDS = 3
# A slide box holds two lines. Two lines of slide text is about this many words.
SLIDE_LINE_CAP = 25
# Short sentences (under this many words) should be about a third of a document.
SHORT_WORDS = 8

IGNORE_RE = re.compile(r"<!--\s*signature:ignore-start\s*-->.*?<!--\s*signature:ignore-end\s*-->", re.S)
IGNORE_LINE_RE = re.compile(r"^.*signature:ignore-line.*$", re.M)

Register = namedtuple("Register", "rhythm variation mean_cap long_cap short_floor exclaim_ok commas semicolons")

REGISTERS = {
    "general": Register(True, True, DEFAULT_MEAN_CAP, DEFAULT_LONG_CAP, 0.05, True, True, True),
    "doc": Register(True, True, DEFAULT_MEAN_CAP, DEFAULT_LONG_CAP, 0.20, False, True, True),
    "customer": Register(True, True, DEFAULT_MEAN_CAP, DEFAULT_LONG_CAP, 0.20, False, True, True),
    "course": Register(True, True, DEFAULT_MEAN_CAP, DEFAULT_LONG_CAP, 0.05, False, True, True),
    "post": Register(True, True, DEFAULT_MEAN_CAP, DEFAULT_LONG_CAP, 0.05, True, True, True),
    "message": Register(True, True, DEFAULT_MEAN_CAP, DEFAULT_LONG_CAP, 0.05, True, True, True),
    "script": Register(True, False, SCRIPT_MEAN_CAP, SCRIPT_LONG_CAP, 0.0, True, True, True),
    "slides": Register(False, False, None, None, 0.0, True, False, True),
    "code": Register(False, False, None, None, 0.0, False, False, False),
}

REGISTER_HELP = {
    "general": "anything else. Shared checks only.",
    "doc": "READMEs, reports, one-pagers. Exclamation marks flagged.",
    "customer": "customer docs and Q&A. Adds open-loop and discovery-voice checks.",
    "course": "course papers and discussion posts. Exclamation marks flagged.",
    "post": "LinkedIn and Medium. Exclamation marks allowed.",
    "message": "teammate messages and emails. Exclamation marks allowed.",
    "script": "speaker and video scripts. Short spoken sentences, nothing unsayable.",
    "slides": "decks (.pptx works). Flags any line over %d words." % SLIDE_LINE_CAP,
    "code": "source files and commit messages. Comments and docstrings only.",
}

# ---------------------------------------------------------------------------
# Word and pattern lists
# ---------------------------------------------------------------------------

BANNED_WORDS = [
    "delve", "delves", "delving", "leverage", "leverages", "leveraging", "robust", "seamless", "seamlessly",
    "crucial", "pivotal", "comprehensive", "landscape", "transformative", "unlock", "unlocks", "unlocking",
    "empower", "empowers", "empowering", "elevate", "elevates", "harness", "harnessing", "tapestry",
    "testament", "moreover", "furthermore", "additionally", "multifaceted", "holistic", "synergy",
    "cutting-edge", "game-changer", "game changer", "revolutionize", "revolutionise", "streamline",
    "streamlines", "paradigm shift", "ever-evolving", "only ever", "embark", "realm", "foster", "fosters",
    "underscore", "underscores", "showcase", "showcases", "meticulous", "meticulously", "intricate",
    "nuanced", "mechanism", "psychosocial", "utilize", "utilise", "utilizes", "utilises", "facilitate",
    "facilitates", "boasts", "vibrant", "enhance", "enhances", "enhancing", "garner", "garnered", "bolster",
    "bolstered", "bolstering", "interplay", "align with", "aligns with", "orchestrate", "orchestrates",
    "nestled", "breathtaking", "groundbreaking", "indelible", "ever-changing", "unwavering",
    "commitment to excellence", "navigate the", "in today's", "fast-paced", "deep dive", "dive into",
    "rest assured", "a journey", "thrilled", "excited to announce",
]

Pattern = namedtuple("Pattern", "tier label regex advice weight only")


def P(tier, label, regex, advice, weight, only=None):
    return Pattern(tier, label, re.compile(regex, re.I), advice, weight, only)


PATTERNS = [
    P("P0", "counted preamble",
      r"\b(one|two|three|four|five|a few|several)\s+(things?|details?|rules?|points?|cautions?|traps?|ways?|"
      r"reasons?|steps?|moves?|parts?|lessons?)\b[^.\n]{0,40}:",
      "Announces the shape of what follows. Just say the things.", 3),
    P("P0", "throat-clearing",
      r"\b(worth reading before|before we (begin|start)|let me (explain|walk)|first things first|"
      r"it goes without saying|needless to say|simply put|the short answer is|it'?s worth noting|"
      r"it is worth noting|worth noting|here'?s the thing|the key takeaway|in conclusion|in summary|to sum up)\b",
      "Cut everything before the first fact.", 3),
    P("P0", "chatbot residue",
      r"\b(i hope this helps|great question|let's (explore|dive|take a look|unpack)|certainly!|absolutely!|"
      r"as of my (knowledge|training)|feel free to reach out|happy to help)",
      "Never in a deliverable.", 3),
    P("P0", "open loop",
      r"\b(come back to you|get back to you|circle back|revert once|checking with the|will follow up|"
      r"happy to (come back|revert|follow up))\b",
      "Never leave something outstanding on us in a customer doc. Handle it offline.", 3,
      only=("customer", "doc")),
    P("P0", "inflated significance",
      r"\b(pivotal (moment|role|hub)|marks? a (shift|turning point|new era)|plays? a (vital|key|crucial|pivotal) "
      r"role|stands? as a testament|a testament to|the broader (landscape|trend)|indelible mark)\b",
      "Say what actually happened.", 3),
    P("P0", "challenge-outlook closer",
      r"\b(despite (these|its|the) challenges|the future (looks|remains) (bright|promising)|"
      r"only time will tell|remains to be seen)\b",
      "Formula ending. Delete it.", 3),
    P("P1", "discovery voice",
      r"\bwe\s+(tried|ran|saw|tested|deployed|found that|checked|noticed)\b",
      "Jed is supposed to know the product. State the behaviour as fact.", 2, only=("customer", "doc")),
    P("P1", "copula avoidance",
      r"\b(serves as|serve as|stands as|stand as|acts as a|functions as a|represents a (significant|major|key))\b",
      "Just say 'is'.", 2),
    P("P1", "-ing rider",
      r",\s+(highlighting|underscoring|emphasizing|emphasising|showcasing|reflecting|demonstrating|symbolizing|"
      r"symbolising|signaling|signalling|cementing|solidifying|contributing to|paving the way)\b",
      "A tacked-on judgement. Cut it, or give the reason in its own sentence.", 2),
    P("P1", "vague authority",
      r"\b(experts (say|agree|argue|note)|studies (show|suggest)|research shows|many (believe|argue)|"
      r"some (critics|observers) (say|argue|note)|industry reports|observers have)\b",
      "Name the source or drop the claim.", 2),
    P("P1", "stacked hedge",
      r"\b(could potentially|may potentially|might potentially|may possibly|could possibly|"
      r"it might be worth considering|arguably perhaps)\b",
      "One hedge at most, only where the evidence is weak.", 2),
    P("P1", "hollow praise",
      r"\b(great (point|question|post)|really highlights|beautifully (put|said)|love this)\b",
      "Get to something specific from their post instead.", 2),
    P("P1", "slogan closer",
      r"\b(the future is|the rest is history|and that makes all the difference|one step at a time)\b",
      "Brochure line. End on the fact or the next step.", 2),
    P("P2", "not X but Y",
      r"\bnot\s+(just|only|merely)?\s*[^.,;\n]{1,40},?\s+but\b|\bisn't\s+[^.,;\n]{1,30},\s+it's\b|"
      r"\bis not\s+[^.,;\n]{1,30},\s+it is\b",
      "Fine once per piece if it is the actual point. Otherwise rephrase.", 1),
    P("P2", "wordy phrase",
      r"\b(in order to|due to the fact that|at this point in time|in the event that|for the purpose of|"
      r"a wide (range|array|variety) of)\b",
      "Use the short version: to, because, now, if, for, many.", 1),
    # Register-only patterns
    P("P1", "narrating comment",
      r"\b(this (function|method|class|code|script|module|file) (is used to|will|handles|is responsible)|"
      r"(here|now) we (loop|iterate|call|check|define))",
      "Comments explain why, not what. Cut it or say why.", 2, only=("code",)),
    P("P1", "commit filler",
      r"\b(enhanced?|improved? (the )?overall|various (fixes|improvements)|minor tweaks|refactor(ed)? for clarity)\b",
      "Say what actually changed.", 2, only=("code",)),
    P("P1", "unspeakable",
      r"\([^)]*\)|\b(e\.g\.|i\.e\.|etc\.|vs\.)|\s&\s|\b\w+/\w+\b",
      "Can't be said out loud. Write it the way you'd say it.", 1, only=("script",)),
]

DASH = re.compile(r"[—–]|\s-{1,2}\s|\w--\w")
CURLY = re.compile(r"[“”‘’]")
EMOJI = re.compile("[\U0001F300-\U0001FAFF✅✨⚡⭐➡→]")
TRIPLE = re.compile(r"\b[\w'-]+(?:\s+[\w'-]+){0,4},\s+[\w'-]+(?:\s+[\w'-]+){0,4},?\s+and\s+[\w'-]+", re.I)

TIER_ORDER = {"P0": 0, "P1": 1, "P2": 2}
TIER_NOTE = {"P0": "fix always", "P1": "fix unless deliberate", "P2": "use judgement"}

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".c", ".cpp", ".h", ".cs", ".rs", ".sh",
            ".zsh", ".bash", ".rb", ".swift", ".kt", ".css", ".scss", ".sql", ".r"}

# Weighted tells per match, for labels that are not regex patterns.
BUILTIN = {
    "dash": ("P0", 2, "Use a full stop, comma, colon or brackets."),
    "banned word": ("P1", 2, "Say it plainly."),
    "semicolon": ("P1", 1, "Use a full stop."),
    "comma-heavy sentence": ("P1", 1, "Split it into two sentences."),
    "exclamation": ("P1", 1, "None in this register."),
    "emoji": ("P1", 1, "No emojis here."),
    "wordy slide text": ("P1", 2, "Two lines per box at most."),
    "group of three?": ("P2", 0, "Check it isn't a tidy parallel triple. Uneven, natural lists are fine."),
    "same opener x3": ("P2", 0.5, "Fine if it is deliberate repetition. Otherwise vary the openings."),
    "curly quotes": ("P2", 0.5, "Use straight quotes in plain text."),
}


# ---------------------------------------------------------------------------
# Reading input
# ---------------------------------------------------------------------------

def read_text(path):
    """Return the text of a file, docx, pptx or stdin. Raises OSError on a bad path."""
    if path == "-":
        return sys.stdin.read()
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix not in (".docx", ".pptx"):
        return p.read_text(encoding="utf8", errors="replace")
    with zipfile.ZipFile(p) as z:
        if suffix == ".docx":
            names, para, text_tag = ["word/document.xml"], r"</w:p>", r"<w:t[^>]*>(.*?)</w:t>"
        else:
            names = sorted(n for n in z.namelist() if re.match(r"ppt/(slides|notesSlides)/\w+\d+\.xml$", n))
            para, text_tag = r"</a:p>", r"<a:t>(.*?)</a:t>"
        lines = []
        for name in names:
            xml = z.read(name).decode("utf8")
            for chunk in re.split(para, xml):
                line = "".join(re.findall(text_tag, chunk, re.S))
                if line.strip():
                    lines.append(line)
        return "\n".join(lines)


def blank(match):
    """Replace a matched span with newlines only, so line numbers stay correct."""
    return "\n" * match.group(0).count("\n")


def extract_comments(src, suffix):
    """Keep only comments and docstrings. Everything else becomes spaces, newlines are kept."""
    spans = []
    if suffix == ".py":
        spans += [m.span(2) for m in re.finditer(r'("""|\'\'\')(.*?)\1', src, re.S)]
    spans += [m.span(1) for m in re.finditer(r"/\*(.*?)\*/", src, re.S)]
    if suffix in {".py", ".sh", ".zsh", ".bash", ".rb", ".r"}:
        line_marker = r"(?:^|\s)#(?![!{\[])\s?(.*)$"
    elif suffix == ".sql":
        line_marker = r"(?:^|\s)--\s?(.*)$"
    else:
        line_marker = r"(?<![:\w/])//\s?(.*)$"
    spans += [m.span(1) for m in re.finditer(line_marker, src, re.M)]
    keep = [" " if c != "\n" else "\n" for c in src]
    for start, end in spans:
        keep[start:end] = list(src[start:end])
    return "".join(keep)


def strip_markup(text):
    """Remove Markdown furniture so only prose is left. Newlines are kept for line numbers."""
    text = IGNORE_RE.sub(blank, text)
    text = IGNORE_LINE_RE.sub("", text)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    text = re.sub(r"```.*?```", blank, text, flags=re.S)
    text = re.sub(r"\A---\n.*?\n---\n", blank, text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"^[ \t]*\|?[-:| ]+\|?[ \t]*$", "", text, flags=re.M)
    text = re.sub(r"^[ \t]*(#+|>|[-*+]|\d+\.)[ \t]+", "", text, flags=re.M)
    return re.sub(r"[*_]{1,3}", "", text)


WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")


def is_list(sentence):
    """True for a run of short items such as 'naming, comment density, idiom, formatter'."""
    sizes = [len(WORD.findall(piece)) for piece in sentence.split(",")]
    return statistics.median(sizes) <= LIST_ITEM_WORDS


def sentences(text, by_line=False):
    """Split prose into sentences. Table rows are skipped. Code comments are split by line."""
    if by_line:
        parts = text.splitlines()
    else:
        parts = re.split(r"(?<=[.!?])\s+|\n{2,}|\n(?=[A-Z])", text)
    return [s.strip() for s in parts if len(WORD.findall(s)) >= 2 and "|" not in s]


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def snippet(text, start, end, pad=25):
    return " ".join(text[max(0, start - pad):end + pad].split())


# ---------------------------------------------------------------------------
# Analysis (pure function, so tests can call it directly)
# ---------------------------------------------------------------------------

def analyse(raw, register="general", suffix=""):
    reg = REGISTERS[register]
    is_code = suffix in CODE_EXT
    if is_code:
        raw = extract_comments(raw, suffix)
        text = IGNORE_LINE_RE.sub("", IGNORE_RE.sub(blank, raw))
    else:
        text = strip_markup(raw)

    words = WORD.findall(text)
    n_words = max(len(words), 1)
    sents = sentences(text, by_line=is_code)
    lens = [len(WORD.findall(s)) for s in sents] or [0]
    findings = []

    def add(label, line, snip, advice=None, tier=None, weight=None):
        t, w, a = BUILTIN.get(label, (tier, weight, advice))
        findings.append({"tier": tier or t, "label": label, "line": line, "snippet": snip,
                         "advice": advice or a, "weight": w if weight is None else weight})

    for m in DASH.finditer(text):
        add("dash", line_of(text, m.start()), snippet(text, m.start(), m.end(), 30))
    if register == "code":
        for f in findings:
            f["weight"] = 1  # a quick "x - y" in a comment is minor. A dash in prose is not.

    low = text.lower()
    for w in BANNED_WORDS:
        for m in re.finditer(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low):
            add("banned word", line_of(text, m.start()), snippet(text, m.start(), m.end()),
                advice="'%s' reads as generated. Say it plainly." % w)

    for pat in PATTERNS:
        if pat.only and register not in pat.only:
            continue
        for m in pat.regex.finditer(text):
            add(pat.label, line_of(text, m.start()), " ".join(m.group(0).split()),
                advice=pat.advice, tier=pat.tier, weight=pat.weight)

    if reg.commas:
        for s in sents:
            n = s.count(",")
            if n >= HEAVY_COMMAS and not is_list(s):
                add("comma-heavy sentence", line_of(text, max(text.find(s[:30]), 0)), " ".join(s.split())[:90],
                    advice="%d commas. Split it into two sentences." % n)
    if reg.semicolons:
        for m in re.finditer(r";", text):
            add("semicolon", line_of(text, m.start()), snippet(text, m.start(), m.end(), 25))
    if suffix not in (".docx", ".pptx"):
        n_curly = len(CURLY.findall(text))
        if n_curly:
            add("curly quotes", 0, "%d found" % n_curly)
    if register not in ("post", "message"):
        for m in EMOJI.finditer(text):
            add("emoji", line_of(text, m.start()), snippet(text, m.start(), m.end(), 20))
    if not reg.exclaim_ok and text.count("!"):
        add("exclamation", 0, "%d found" % text.count("!"))

    if register == "slides":
        for i, line in enumerate(text.splitlines(), 1):
            n = len(WORD.findall(line))
            if n > SLIDE_LINE_CAP:
                add("wordy slide text", i, line.strip()[:70], advice="%d words in one line. Two lines per box at most." % n)

    if not is_code:
        for m in TRIPLE.finditer(text):
            add("group of three?", line_of(text, m.start()), " ".join(m.group(0).split()))
        firsts = [(WORD.findall(s) or [""])[0].lower() for s in sents]
        run = 1
        for i in range(1, len(firsts)):
            run = run + 1 if firsts[i] and firsts[i] == firsts[i - 1] else 1
            if run == 3:
                add("same opener x3", line_of(text, max(text.find(sents[i][:30]), 0)), sents[i][:60])

    # Rhythm
    mean = statistics.mean(lens)
    median = statistics.median(lens)
    stdev = statistics.pstdev(lens) if len(lens) > 1 else 0.0
    short = sum(1 for n in lens if n < SHORT_WORDS) / len(lens)
    n_long = sum(1 for n in lens if reg.long_cap and n > reg.long_cap)
    commas = text.count(",") / max(len(sents), 1)
    enough = len(lens) >= MIN_SENTENCES_FOR_RHYTHM

    rhythm = []
    if reg.rhythm:
        if mean > reg.mean_cap:
            rhythm.append("Mean sentence length %.0f words. Aim for %s." % (mean, "about 10" if register == "script" else "12 to 15"))
        if reg.variation and enough and stdev < MIN_STDEV:
            rhythm.append("Sentence lengths barely vary (stdev %.1f). Mix short lines with longer ones." % stdev)
        if reg.short_floor and enough and short < reg.short_floor:
            rhythm.append("Only %.0f%% of sentences are under %d words. Mix in some short ones." % (short * 100, SHORT_WORDS))
        if n_long > max(1, len(lens) // 12):
            rhythm.append("%d sentences over %d words. Split them." % (n_long, reg.long_cap))
    if reg.commas and commas > MAX_COMMAS_PER_SENTENCE:
        rhythm.append("%.2f commas per sentence. Aim for under 1." % commas)

    n_not_x = sum(1 for f in findings if f["label"] == "not X but Y")
    weighted = sum(f["weight"] for f in findings) - (1 if n_not_x == 1 else 0)
    score = weighted * 100.0 / n_words + len(rhythm) * RHYTHM_PENALTY
    verdict = "clean" if score < CLEAN_BELOW else "a few tells" if score < FIX_AT else "reads AI, fix before sending"

    counts = {}
    for f in findings:
        counts[f["label"]] = counts.get(f["label"], 0) + 1

    return {
        "register": register, "verdict": verdict, "score": round(score, 2), "words": n_words,
        "sentences": len(sents), "mean_words": round(mean, 1), "median_words": median,
        "short_share": round(short, 2), "over_long": n_long, "commas_per_sentence": round(commas, 2),
        "dashes": counts.get("dash", 0), "banned_words": counts.get("banned word", 0),
        "other_tells": sum(v for k, v in counts.items() if k not in ("dash", "banned word", "group of three?")),
        "findings": sorted(findings, key=lambda f: (TIER_ORDER[f["tier"]], f["label"], f["line"])),
        "rhythm": rhythm, "not_x_allowed": n_not_x == 1,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def summary_line(r):
    return ("[%s] AI check: %s (score %.1f). %d words, %d sentences, mean %.1f / median %.0f words, "
            "%.0f%% under %d, %d over %s, %.2f commas per sentence, %d dashes, %d banned words, %d other tells."
            % (r["register"], r["verdict"], r["score"], r["words"], r["sentences"], r["mean_words"],
               r["median_words"], r["short_share"] * 100, SHORT_WORDS, r["over_long"],
               REGISTERS[r["register"]].long_cap or "n/a", r["commas_per_sentence"], r["dashes"],
               r["banned_words"], r["other_tells"]))


def print_report(r):
    tier = label = None
    for f in r["findings"]:
        if f["tier"] != tier:
            tier = f["tier"]
            print("\n=== %s (%s)" % (tier, TIER_NOTE[tier]))
            label = None
        if f["label"] != label:
            label = f["label"]
            print("\n## %s  (%s)" % (label, f["advice"]))
        print("  line %s: ...%s..." % (f["line"] or "-", f["snippet"]))
    if r["not_x_allowed"]:
        print("\n  (one 'not X but Y' is allowed if it is the actual point)")
    if r["rhythm"]:
        print("\n=== rhythm")
        for line in r["rhythm"]:
            print("  " + line)
    print()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="file to check, or - for stdin")
    ap.add_argument("--register", default=None, choices=sorted(REGISTERS), help="material type (default: general, or code for source files)")
    ap.add_argument("--quiet", action="store_true", help="print only the summary line")
    ap.add_argument("--json", action="store_true", help="print the full result as JSON")
    ap.add_argument("--list-registers", action="store_true", help="list the registers and exit")
    ap.add_argument("--version", action="version", version="ai_check " + __version__)
    args = ap.parse_args(argv)

    if args.list_registers:
        for name in sorted(REGISTERS):
            print("%-9s %s" % (name, REGISTER_HELP[name]))
        return 0
    if not args.file:
        ap.error("give a file to check, or - to read stdin")

    try:
        raw = read_text(args.file)
    except (OSError, zipfile.BadZipFile) as e:
        print("ai_check: cannot read %s: %s" % (args.file, e), file=sys.stderr)
        return 2

    suffix = Path(args.file).suffix.lower() if args.file != "-" else ""
    register = args.register or ("code" if suffix in CODE_EXT else "general")
    result = analyse(raw, register, suffix)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if not args.quiet:
            print_report(result)
        print(summary_line(result))
    return 0 if result["score"] < FIX_AT else 1


if __name__ == "__main__":
    sys.exit(main())
