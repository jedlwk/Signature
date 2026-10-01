#!/usr/bin/env python3
"""Flag the AI tells Jed keeps asking to remove.

Usage:
    python3 ai_check.py draft.md
    python3 ai_check.py slides.pptx --register slides
    python3 ai_check.py script.md --register script
    python3 ai_check.py app.py            (source files: checks comments and docstrings only)
    git log -1 --format=%B | python3 ai_check.py - --register code
    pbpaste | python3 ai_check.py -

This is a style linter, not an AI detector like GPTZero. It counts the patterns Jed has struck out
in past drafts and gives a rough score. A clean result means "nothing obvious", not "human".
"""
import argparse
import re
import statistics
import sys
import zipfile
from pathlib import Path

# Words and phrases that read as generated. Lowercase, matched on word boundaries.
BANNED = [
    "delve", "delves", "delving", "leverage", "leverages", "leveraging", "robust", "seamless",
    "seamlessly", "crucial", "pivotal", "comprehensive", "landscape", "transformative", "transform your",
    "unlock", "unlocks", "unlocking", "empower", "empowers", "empowering", "elevate", "elevates",
    "harness", "harnessing", "tapestry", "testament", "moreover", "furthermore", "additionally",
    "multifaceted", "holistic", "synergy", "cutting-edge", "game-changer", "game changer",
    "revolutionize", "revolutionise", "streamline", "streamlines", "paradigm shift", "navigate the",
    "in today's", "fast-paced", "ever-evolving", "only ever", "it's worth noting", "it is worth noting",
    "worth noting", "let's dive", "dive into", "deep dive", "here's the thing", "the key takeaway",
    "in conclusion", "in summary", "to sum up", "ultimately,", "at its core", "rest assured",
    "a journey", "embark", "realm", "foster", "fosters", "underscore", "underscores", "showcase",
    "showcases", "meticulous", "meticulously", "intricate", "nuanced", "mechanism", "psychosocial",
    "utilize", "utilise", "utilizes", "utilises", "facilitate", "facilitates", "boasts", "vibrant",
    "enhance", "enhances", "enhancing", "garner", "garnered", "bolster", "bolstered", "bolstering",
    "interplay", "align with", "aligns with", "orchestrate", "orchestrates", "nestled", "breathtaking",
    "groundbreaking", "indelible", "ever-changing", "unwavering", "commitment to excellence",
]

# (label, regex, advice). Patterns are case-insensitive.
PATTERNS = [
    ("counted preamble",
     r"\b(one|two|three|four|five|a few|several)\s+(things?|details?|rules?|points?|cautions?|traps?|"
     r"ways?|reasons?|steps?|moves?|parts?|lessons?)\b[^.\n]{0,40}:",
     "Announces the shape of what follows. Just say the things."),
    ("not X but Y",
     r"\bnot\s+(just|only|merely)?\s*[^.,;\n]{1,40},?\s+but\b|\bisn't\s+[^.,;\n]{1,30},\s+it's\b|"
     r"\bis not\s+[^.,;\n]{1,30},\s+it is\b",
     "Fine once per piece if it is the actual point. Otherwise rephrase."),
    ("discovery voice",
     r"\bwe\s+(tried|ran|saw|tested|deployed|found that|checked|noticed)\b",
     "Jed is supposed to know the product. State the behaviour as fact."),
    ("open loop",
     r"\b(come back to you|get back to you|circle back|revert once|checking with the|will follow up|"
     r"happy to (come back|revert|follow up))\b",
     "Never leave something outstanding on us in a deliverable. Handle it offline."),
    ("throat-clearing",
     r"\b(worth reading before|before we (begin|start)|let me (explain|walk)|first things first|"
     r"it goes without saying|needless to say|simply put|the short answer is)\b",
     "Cut everything before the first fact."),
    ("hollow praise",
     r"\b(great (point|question|post)|really highlights|beautifully (put|said)|love this)\b",
     "Get to something specific from their post instead."),
    ("copula avoidance",
     r"\b(serves as|serve as|stands as|stand as|acts as a|functions as a|represents a (significant|major|key))\b",
     "Just say 'is'."),
    ("-ing rider",
     r",\s+(highlighting|underscoring|emphasizing|emphasising|showcasing|reflecting|demonstrating|"
     r"symbolizing|symbolising|signaling|signalling|cementing|solidifying|contributing to|paving the way)\b",
     "A tacked-on judgement. Cut it, or give the reason in its own sentence."),
    ("inflated significance",
     r"\b(pivotal (moment|role|hub)|marks? a (shift|turning point|new era)|plays? a (vital|key|crucial|pivotal) role|"
     r"stands? as a testament|a testament to|the broader (landscape|trend)|indelible mark)\b",
     "Say what actually happened."),
    ("vague authority",
     r"\b(experts (say|agree|argue|note)|studies (show|suggest)|research shows|many (believe|argue)|"
     r"some (critics|observers) (say|argue|note)|industry reports|observers have)\b",
     "Name the source or drop the claim."),
    ("stacked hedge",
     r"\b(could potentially|may potentially|might potentially|may possibly|could possibly|"
     r"it might be worth considering|arguably perhaps)\b",
     "One hedge at most, only where evidence is weak."),
    ("chatbot residue",
     r"\b(i hope this helps|great question|let's (explore|dive|take a look|unpack)|certainly!|absolutely!|"
     r"as of my (knowledge|training)|feel free to reach out|happy to help)",
     "Never in a deliverable."),
    ("challenge-outlook closer",
     r"\b(despite (these|its|the) challenges|the future (looks|remains) (bright|promising)|"
     r"only time will tell|remains to be seen)\b",
     "Formula ending. Delete it."),
    ("wordy phrase",
     r"\b(in order to|due to the fact that|at this point in time|in the event that|for the purpose of|"
     r"a wide (range|array|variety) of)\b",
     "Use the short version: to, because, now, if, for, many."),
    ("slogan closer",
     r"\b(the future is|the rest is history|and that makes all the difference|one step at a time|"
     r"from [a-z]+ to [a-z]+\.)",
     "Brochure line. End on the fact or the next step."),
]

# Extra tells per material. Checked only in that register.
REGISTER_PATTERNS = {
    "code": [
        ("narrating comment",
         r"\b(this (function|method|class|code|script|module|file) (is used to|will|handles|is responsible)|"
         r"(here|now) we (loop|iterate|call|check|define))",
         "Comments explain why, not what. Cut it or say why."),
        ("commit filler",
         r"\b(enhanced?|improved? (the )?overall|various (fixes|improvements)|minor tweaks|refactor(ed)? for clarity)\b",
         "Say what actually changed."),
        ("emoji", "[\U0001F300-\U0001FAFF\u2705\u2728\u26A1]", "No emojis in code, logs or commits."),
    ],
    "script": [
        ("unspeakable",
         r"\([^)]*\)|\b(e\.g\.|i\.e\.|etc\.|vs\.)|\s&\s|\b\w+/\w+\b",
         "Can't be said out loud. Write it the way you'd say it."),
    ],
}

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".c", ".cpp", ".h", ".cs", ".rs",
            ".sh", ".zsh", ".bash", ".rb", ".swift", ".kt", ".css", ".scss", ".sql", ".r"}

TRIPLE = re.compile(r"\b[\w'-]+(?:\s+[\w'-]+){0,4},\s+[\w'-]+(?:\s+[\w'-]+){0,4},?\s+and\s+[\w'-]+", re.I)
DASH = re.compile(r"[\u2014\u2013]|\s-{1,2}\s|\w--\w")
CURLY = re.compile(r"[\u201c\u201d\u2018\u2019]")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2705\u2728\u26A1\u2B50\u27A1\u2192]")


def read_text(path):
    if path == "-":
        return sys.stdin.read()
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in (".docx", ".pptx"):
        with zipfile.ZipFile(p) as z:
            if suffix == ".docx":
                names = ["word/document.xml"]
                para_tag = r"</w:p>"
                text_tag = r"<w:t[^>]*>(.*?)</w:t>"
            else:
                names = sorted(n for n in z.namelist() if re.match(r"ppt/(slides|notesSlides)/\w+\d+\.xml$", n))
                para_tag = r"</a:p>"
                text_tag = r"<a:t>(.*?)</a:t>"
            chunks = []
            for n in names:
                xml = z.read(n).decode("utf8")
                for para in re.split(para_tag, xml):
                    line = "".join(re.findall(text_tag, para, re.S))
                    if line.strip():
                        chunks.append(line)
            return "\n".join(chunks)
    return p.read_text(encoding="utf8", errors="replace")


def extract_comments(src, suffix):
    """Pull comments and docstrings out of source code. Rough, but good enough for a style pass."""
    out = []
    if suffix == ".py":
        out += re.findall(r'''(?:"""|\'\'\')(.*?)(?:"""|\'\'\')''', src, re.S)
    out += re.findall(r"/\*(.*?)\*/", src, re.S)
    hash_langs = {".py", ".sh", ".zsh", ".bash", ".rb", ".r"}
    marker = r"#(?![!{\[])" if suffix in hash_langs else r"(?<![:\w])//"
    if suffix == ".sql":
        marker = r"--"
    for m in re.finditer(marker + r"\s?(.*)$", src, re.M):
        out.append(m.group(1))
    # comments are often fragments, so end each one as a sentence
    return "\n\n".join(c.strip().rstrip(".") + "." for c in out if c.strip())


def strip_markup(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)          # code blocks
    text = re.sub(r"`[^`]*`", " ", text)                          # inline code
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)      # front matter
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)         # links
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"^\s*\|?[-:| ]+\|?\s*$", "", text, flags=re.M)  # table rules
    text = re.sub(r"^\s*(#+|>|[-*+]|\d+\.)\s+", "", text, flags=re.M)
    text = re.sub(r"[*_]{1,3}", "", text)
    return text


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}|\n(?=[A-Z])", text)
    return [s.strip() for s in parts if len(re.findall(r"[A-Za-z']+", s)) >= 2]


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="file to check, or - for stdin")
    ap.add_argument("--register", default="general",
                    choices=["general", "code", "doc", "customer", "course", "slides", "script", "post",
                             "message"],
                    help="which material this is. Source files default to code.")
    ap.add_argument("--quiet", action="store_true", help="print only the summary line")
    args = ap.parse_args()

    raw = read_text(args.file)
    suffix = Path(args.file).suffix.lower() if args.file != "-" else ""
    if suffix in CODE_EXT:
        raw = extract_comments(raw, suffix)
        if args.register == "general":
            args.register = "code"
    reg = args.register
    text = strip_markup(raw)
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    n_words = max(len(words), 1)
    sents = sentences(text)
    lens = [len(re.findall(r"[A-Za-z][A-Za-z'-]*", s)) for s in sents] or [0]

    findings = []  # (label, line, snippet, advice)

    for m in DASH.finditer(text):
        findings.append(("dash", line_of(text, m.start()), text[max(0, m.start() - 30):m.end() + 30],
                         "Use a full stop, comma, colon or brackets."))

    low = text.lower()
    for w in BANNED:
        for m in re.finditer(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", low):
            findings.append(("banned word", line_of(text, m.start()), text[max(0, m.start() - 25):m.end() + 25],
                             "'%s' reads as generated. Say it plainly." % w))

    for label, pat, advice in PATTERNS:
        for m in re.finditer(pat, text, re.I):
            findings.append((label, line_of(text, m.start()), m.group(0), advice))

    # Punctuation mechanics
    if reg not in ("code", "slides"):
        for sent in sents:
            n_commas = sent.count(",")
            if n_commas >= 3 and "|" not in sent:  # table rows are lists, not sentences
                findings.append(("comma-heavy sentence", line_of(text, max(text.find(sent[:30]), 0)),
                                 sent[:90], "%d commas. Split it into two sentences." % n_commas))
    if reg != "code":
        for m in re.finditer(r";", text):
            findings.append(("semicolon", line_of(text, m.start()), text[max(0, m.start() - 30):m.end() + 20],
                             "Use a full stop."))
    if suffix not in (".docx", ".pptx"):
        n_curly = len(CURLY.findall(text))
        if n_curly:
            findings.append(("curly quotes", 0, "%d found" % n_curly, "Use straight quotes in plain text."))
    if reg not in ("post", "message", "code"):  # code has its own emoji check
        for m in EMOJI.finditer(text):
            findings.append(("emoji", line_of(text, m.start()), text[max(0, m.start() - 20):m.end() + 20],
                             "No emojis here."))

    # Three or more sentences in a row starting with the same word
    firsts = [(re.findall(r"[A-Za-z']+", x) or [""])[0].lower() for x in sents]
    run = 1
    for i in range(1, len(firsts)):
        run = run + 1 if firsts[i] and firsts[i] == firsts[i - 1] else 1
        if run == 3:
            findings.append(("same opener x3", line_of(text, max(text.find(sents[i][:30]), 0)),
                             sents[i][:60], "Fine if it's deliberate repetition. Otherwise vary the openings."))

    for label, pat, advice in REGISTER_PATTERNS.get(reg, []):
        for m in re.finditer(pat, text, re.I):
            findings.append((label, line_of(text, m.start()), m.group(0), advice))

    if reg == "slides":
        for i, line in enumerate(text.splitlines(), 1):
            n = len(re.findall(r"[A-Za-z][A-Za-z'-]*", line))
            if n > 25:
                findings.append(("wordy slide text", i, line[:70],
                                 "%d words in one line. Two lines per box at most." % n))

    triples = list(TRIPLE.finditer(text))
    for m in triples:
        findings.append(("group of three?", line_of(text, m.start()), m.group(0),
                         "Check it isn't a tidy parallel triple. Uneven, natural lists are fine."))

    exclaims = text.count("!")
    if reg in ("code", "doc", "customer", "course") and exclaims:
        findings.append(("exclamation", 0, "%d found" % exclaims, "None in this register."))

    # Rhythm
    mean = statistics.mean(lens)
    median = statistics.median(lens)
    stdev = statistics.pstdev(lens) if len(lens) > 1 else 0.0
    short = sum(1 for l in lens if l < 8) / len(lens)
    long_ = sum(1 for l in lens if l > 30)
    commas = text.count(",") / max(len(sents), 1)

    rhythm = []
    if reg in ("code", "slides"):
        pass  # fragments are normal here, so rhythm checks would just be noise
    elif reg == "script":
        if mean > 14:
            rhythm.append("Mean sentence length %.0f words. Spoken lines want about 10." % mean)
        over = sum(1 for l in lens if l > 25)
        if over:
            rhythm.append("%d sentences over 25 words. Too long to say in one breath." % over)
    elif mean > 18:
        rhythm.append("Mean sentence length %.0f words. Aim for 12 to 15." % mean)
    if reg in ("code", "slides", "script"):
        pass
    elif len(lens) >= 6 and stdev < 4:
        rhythm.append("Sentence lengths barely vary (stdev %.1f). Mix short lines with longer ones." % stdev)
    short_floor = 0.2 if reg in ("doc", "customer") else 0.05
    if reg not in ("code", "slides", "script") and len(lens) >= 6 and short < short_floor:
        rhythm.append("Only %.0f%% of sentences are under 8 words. Mix in some short ones." % (short * 100))
    if reg not in ("code", "slides", "script") and long_ > max(1, len(lens) // 12):
        rhythm.append("%d sentences over 30 words. Split them." % long_)
    if reg not in ("code", "slides") and commas > 1.0:
        rhythm.append("%.2f commas per sentence. Aim for under 1." % commas)

    # Score: tells per 100 words, weighted. Rhythm issues add a little.
    weights = {"dash": 2, "banned word": 2, "counted preamble": 3, "not X but Y": 1, "discovery voice": 2,
               "open loop": 3, "throat-clearing": 3, "hollow praise": 2, "slogan closer": 2,
               "group of three?": 0, "exclamation": 1, "narrating comment": 2, "commit filler": 2,
               "emoji": 1, "unspeakable": 1, "wordy slide text": 2, "copula avoidance": 2, "-ing rider": 2,
               "inflated significance": 3, "vague authority": 2, "stacked hedge": 2, "chatbot residue": 3,
               "challenge-outlook closer": 3, "wordy phrase": 1, "comma-heavy sentence": 1, "semicolon": 1,
               "curly quotes": 0.5, "same opener x3": 0.5}
    not_x = sum(1 for f in findings if f[0] == "not X but Y")
    if reg == "code":
        weights["dash"] = 1  # a quick "x - y" in a comment is minor, a dash in prose is not
    weighted = sum(weights.get(f[0], 1) for f in findings) - (1 if not_x == 1 else 0)
    score = weighted * 100.0 / n_words + len(rhythm) * 0.5
    verdict = "clean" if score < 1 else "a few tells" if score < 3 else "reads AI, fix before sending"

    if not args.quiet:
        order = ["dash", "comma-heavy sentence", "semicolon", "curly quotes", "banned word", "chatbot residue",
                 "inflated significance", "copula avoidance", "-ing rider", "vague authority", "stacked hedge",
                 "challenge-outlook closer", "wordy phrase", "same opener x3", "counted preamble", "throat-clearing", "open loop", "discovery voice",
                 "slogan closer", "hollow praise", "narrating comment", "commit filler", "emoji",
                 "unspeakable", "wordy slide text", "not X but Y", "exclamation", "group of three?"]
        findings.sort(key=lambda f: (order.index(f[0]) if f[0] in order else 99, f[1]))
        current = None
        for label, line, snip, advice in findings:
            if label != current:
                print("\n## %s  (%s)" % (label, advice))
                current = label
            snip = " ".join(snip.split())
            print("  line %s: ...%s..." % (line if line else "-", snip))
        if not_x == 1:
            print("  (one 'not X but Y' is allowed if it is the actual point)")
        if rhythm:
            print("\n## rhythm")
            for r in rhythm:
                print("  " + r)
        print()

    counts = {}
    for f in findings:
        counts[f[0]] = counts.get(f[0], 0) + 1
    print("[%s] " % reg, end="")
    print("AI check: %s (score %.1f). %d words, %d sentences, mean %.1f / median %.0f words, "
          "%.0f%% under 8, %d over 30, %.2f commas per sentence, %d dashes, %d banned words, %d other tells."
          % (verdict, score, n_words, len(sents), mean, median, short * 100, long_, commas,
             counts.get("dash", 0), counts.get("banned word", 0),
             sum(v for k, v in counts.items() if k not in ("dash", "banned word", "group of three?"))))
    return 0 if score < 3 else 1


if __name__ == "__main__":
    sys.exit(main())
