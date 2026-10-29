#!/usr/bin/env python3
"""Record what Claude writes in prose files, then pair it with what the writer commits.

Usage:
    python3 capture.py enable [--exclude GLOB ...] [--numbers-only]
    python3 capture.py disable
    python3 capture.py status
    python3 capture.py snapshot              (the PostToolUse hook. Reads the hook's JSON on stdin)
    python3 capture.py pair [--repo DIR] [--quiet] [--budget SECONDS]
    python3 capture.py report [--json] [--passages N]

It is off until `enable`. Everything stays in ~/.claude/signature/ (or SIGNATURE_HOME): drafts/ holds Claude's
versions waiting for a commit, and edits.jsonl holds each draft paired with the committed version. Nothing is
sent anywhere.

Only passages Claude wrote count. If Claude edits one paragraph of a file, changes to the rest of it are the
writer's own work, not edits to Claude's draft.

Exit codes: always 0 for snapshot, so a hook can never block a session. Otherwise 0 done, 2 could not run.
"""
import fnmatch
import hashlib
import json
import os
import sys
import time
from pathlib import Path

__version__ = "1.0.0"

DATA = Path(os.environ.get("SIGNATURE_HOME") or Path.home() / ".claude" / "signature")
CONFIG = DATA / "capture.json"
DRAFTS = DATA / "drafts"
EDITS = DATA / "edits.jsonl"

# A commit this long after Claude's draft is more likely new content than a fix to Claude's style.
WINDOW_DAYS = 14
# Pairs older than this are dropped, so the log holds a season of writing, not a whole history.
KEEP_DAYS = 90
# Claude's edits to one file in one session, this close together, are one draft.
SAME_DRAFT_SECONDS = 30 * 60
# A Claude passage shorter than this (a one-word swap) can't say whose paragraph it sits in.
MIN_PASSAGE_CHARS = 20
# Bigger files are generated or data. Same cap as plan_scan.py.
MAX_BYTES = 300_000
# Prose Claude writes with its file tools. Word, PowerPoint and notebooks change through other routes, and
# HTML is usually a generated page, not writing.
PROSE_EXT = {".md", ".markdown", ".txt", ".rst", ".adoc"}
# Files that exist for agents or tools, not readers.
SKIP_NAMES = {"claude.md", "agents.md", "gemini.md", "memory.md", "style_plan.md"}
IGNORE_FILE = ".signatureignore"
DEFAULTS = {"enabled": False, "exclude": [], "numbers_only": False, "window_days": WINDOW_DAYS, "keep_days": KEEP_DAYS}
DAY = 86400


# ---------------------------------------------------------------------------
# Settings and small file helpers
# ---------------------------------------------------------------------------

def load_config():
    try:
        data = json.loads(CONFIG.read_text())
    except (OSError, ValueError):
        data = {}
    return dict(DEFAULTS, **(data if isinstance(data, dict) else {}))


def save_private(path, text):
    """Write a file only this user can read, without leaving half a file behind."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf8") as f:
        f.write(text)
    os.replace(tmp, path)


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf8"))
    except (OSError, ValueError):
        return None


def repo_root(path):
    for folder in Path(path).parents:
        if (folder / ".git").exists():
            return folder
    return None


def ignored(root, rel):
    try:
        lines = (root / IGNORE_FILE).read_text().splitlines()
    except OSError:
        return False
    text = rel.as_posix()
    for pat in (l.strip().rstrip("/") for l in lines):
        if pat and not pat.startswith("#") and (fnmatch.fnmatch(text, pat) or fnmatch.fnmatch(text, pat + "/*")
                                               or any(fnmatch.fnmatch(part, pat) for part in rel.parts)):
            return True
    return False


# ---------------------------------------------------------------------------
# Snapshot: the hook. Keep it fast and quiet.
# ---------------------------------------------------------------------------

def snapshot(payload, now=None):
    """Save Claude's version of a prose file after Write, Edit or MultiEdit. Returns the draft, or None."""
    cfg = load_config()
    tool, given = payload.get("tool_name"), payload.get("tool_input") or {}
    if not cfg["enabled"] or tool not in ("Write", "Edit", "MultiEdit") or not given.get("file_path"):
        return None
    path = Path(given["file_path"])
    if not path.is_absolute():
        path = Path(payload.get("cwd") or os.getcwd()) / path
    path = Path(os.path.realpath(path))
    if path.suffix.lower() not in PROSE_EXT or path.name.lower() in SKIP_NAMES:
        return None
    if any(fnmatch.fnmatch(str(path), pat) for pat in cfg["exclude"]):
        return None
    root = repo_root(path)
    if root and ignored(root, path.relative_to(root)):
        return None
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        content = path.read_text(encoding="utf8")
    except (OSError, UnicodeDecodeError):
        return None

    if tool == "Write":
        written = [content]
    elif tool == "Edit":
        written = [given.get("new_string", "")]
    else:
        written = [e.get("new_string", "") for e in given.get("edits", [])]
    written = [w for w in written if w.strip()]
    now = now or time.time()
    session = payload.get("session_id", "")
    key = hashlib.sha1(str(path).encode()).hexdigest()[:16]
    current = DRAFTS / (key + ".json")
    old = read_json(current)
    if old and old.get("session") == session and now - old.get("time", 0) < SAME_DRAFT_SECONDS:
        if tool != "Write":
            written = old["written"] + written
    elif old:
        # a new draft of the same file. The old one keeps the time between the two to be paired.
        os.replace(current, DRAFTS / ("%s-%d.json" % (key, int(old["time"]))))
    draft = {"key": key, "path": str(path), "repo": str(root) if root else None,
             "rel": path.relative_to(root).as_posix() if root else None, "session": session, "tool": tool,
             "time": now, "content": content, "written": written}
    save_private(current, json.dumps(draft))
    return draft


# ---------------------------------------------------------------------------
# Pair: compare each draft with the version committed after it
# ---------------------------------------------------------------------------

def norm(text):
    return " ".join(text.split())


def paragraphs(text):
    """Prose paragraphs, with fenced code left out."""
    out, block, fenced = [], [], False
    for line in text.splitlines() + [""]:
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.strip():
            block.append(line)
        elif block:
            out.append(norm(" ".join(block)))
            block = []
    return out


def compare(draft, final):
    """Split the change into passages Claude wrote that were kept, edited or cut. Text Claude didn't write is
    counted but not compared."""
    from difflib import SequenceMatcher
    written = [norm(w) for w in draft["written"]]

    def claudes(p):
        return any(p in w or (len(w) >= MIN_PASSAGE_CHARS and w in p) for w in written)

    before, after = paragraphs(draft["content"]), paragraphs(final)
    counts = {"kept": 0, "edited": 0, "cut": 0, "added": 0, "outside": 0}
    passages, mine_before, mine_after = [], [], []
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        old, new = before[i1:i2], after[j1:j2]
        if tag == "insert":
            counts["added"] += 1
            continue
        if not any(claudes(p) for p in old):
            counts["outside"] += 1 if tag != "equal" else 0
            continue
        if tag == "equal":
            counts["kept"] += sum(1 for p in old if claudes(p))
            old = new = [p for p in old if claudes(p)]
        else:
            counts["edited" if tag == "replace" else "cut"] += 1
            passages.append({"before": "\n\n".join(old), "after": "\n\n".join(new)})
        mine_before += old
        mine_after += new
    words_before, words_after = " ".join(mine_before).split(), " ".join(mine_after).split()
    ratio = 1 - SequenceMatcher(None, words_before, words_after, autojunk=False).ratio() if words_before else None
    return counts, passages, "\n\n".join(mine_before), "\n\n".join(mine_after), len(words_before), ratio


def git(repo, *args):
    import subprocess
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def tell_counts(text, register):
    if not text.strip():
        return {}
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ai_check
    counts = {}
    for f in ai_check.analyse(text, register)["findings"]:
        counts[f["label"]] = counts.get(f["label"], 0) + 1
    return counts


def guess_register(rel):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import plan_scan
    return plan_scan.infer_register(rel, Path(rel).suffix.lower())


def load_records():
    records = {}
    try:
        for line in EDITS.read_text(encoding="utf8").splitlines():
            try:
                r = json.loads(line)
                records[r["id"]] = r
            except (ValueError, KeyError):
                continue
    except OSError:
        pass
    return records


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M", time.localtime(t))


def pair(repo=None, now=None, budget=None):
    """Pair waiting drafts with later commits. Returns (paired, waiting, closed)."""
    cfg = load_config()
    now, started = now or time.time(), time.time()
    window = cfg["window_days"] * DAY
    groups = {}
    for path in DRAFTS.glob("*.json") if DRAFTS.is_dir() else []:
        d = read_json(path)
        if d:
            groups.setdefault(d["key"], []).append((d["time"], path, d))
    records = load_records()
    paired = waiting = closed = 0
    for key, drafts in groups.items():
        drafts.sort(key=lambda x: x[0])
        for n, (t, path, d) in enumerate(drafts):
            if budget and time.time() - started > budget:
                break
            end = min(t + window, drafts[n + 1][0] if n + 1 < len(drafts) else float("inf"))
            if not d["repo"]:  # outside git there is nothing to pair with, so it only waits to expire
                if now > end:
                    path.unlink()
                    closed += 1
                continue
            if repo and d["repo"] != str(repo):
                continue
            log = git(d["repo"], "log", "-n", "50", "--format=%H %ct %B%x00", "--", d["rel"])
            hits = []
            for entry in (log or "").split("\x00"):
                parts = entry.strip().split(" ", 2)
                # commit times are whole seconds, so a commit in the same second as the draft still counts
                if len(parts) >= 2 and parts[1].isdigit() and int(t) <= int(parts[1]) <= end:
                    hits.append((int(parts[1]), parts[0], parts[2] if len(parts) > 2 else ""))
            if hits:
                when, commit, message = max(hits)
                final = git(d["repo"], "show", "%s:%s" % (commit, d["rel"])) or ""
                counts, passages, mine_before, mine_after, words, ratio = compare(d, final)
                register = guess_register(d["rel"])
                record = dict({"id": "%s-%d" % (key, int(t)), "repo": Path(d["repo"]).name, "path": d["rel"],
                               "drafted": iso(t), "final": iso(when), "final_time": when, "commit": commit[:7],
                               "claude_commit": "co-authored-by: claude" in message.lower(),
                               "status": "closed" if now > end else "open", "register": register,
                               "words": words, "edit_ratio": None if ratio is None else round(ratio, 3)}, **counts)
                record["tells_before"] = tell_counts(mine_before, register)
                record["tells_after"] = tell_counts(mine_after, register)
                if not cfg["numbers_only"]:
                    record["passages"] = passages
                records[record["id"]] = record
                paired += 1
            else:
                waiting += 1
            if now > end:
                path.unlink()
                closed += 1
    keep = now - cfg["keep_days"] * DAY
    kept = [r for r in records.values() if r.get("final_time", now) >= keep]
    if kept or EDITS.exists():
        save_private(EDITS, "".join(json.dumps(r) + "\n" for r in sorted(kept, key=lambda r: r["final_time"])))
    return paired, waiting, closed


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def word_changes(passages):
    from difflib import SequenceMatcher
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ai_check
    removed, added = {}, {}
    for p in passages:
        a = [w.lower() for w in ai_check.WORD.findall(p["before"])]
        b = [w.lower() for w in ai_check.WORD.findall(p["after"])]
        for tag, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            for w in a[i1:i2] if tag in ("delete", "replace") else []:
                if w not in ai_check.STOPWORDS:
                    removed[w] = removed.get(w, 0) + 1
            for w in b[j1:j2] if tag in ("insert", "replace") else []:
                if w not in ai_check.STOPWORDS:
                    added[w] = added.get(w, 0) + 1
    top = lambda d: sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    return top(removed), top(added)


def summarise(records):
    rs = [r for r in records if r.get("edit_ratio") is not None]
    weeks = {}
    for r in rs:
        week = time.strftime("%G-W%V", time.localtime(r["final_time"]))
        w = weeks.setdefault(week, {"drafts": 0, "words": 0, "edited_words": 0.0})
        w["drafts"] += 1
        w["words"] += r["words"]
        w["edited_words"] += r["edit_ratio"] * r["words"]
    removed_tells = {}
    for r in rs:
        for label, n in r.get("tells_before", {}).items():
            gone = n - r.get("tells_after", {}).get(label, 0)
            if gone > 0:
                removed_tells[label] = removed_tells.get(label, 0) + gone
    passages = [p for r in rs for p in r.get("passages", [])]
    removed, added = word_changes(passages)
    return {"drafts": len(rs),
            "kept_as_is": sum(1 for r in rs if not r["edited"] and not r["cut"]),
            "claude_commits": sum(1 for r in rs if r.get("claude_commit")),
            "weeks": [{"week": k, "drafts": v["drafts"], "edit_ratio": round(v["edited_words"] / max(v["words"], 1), 3)}
                      for k, v in sorted(weeks.items())],
            "tells_removed": sorted(removed_tells.items(), key=lambda kv: -kv[1])[:8],
            "words_removed": removed, "words_added": added}


def plural(n, word):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def print_report(s, records, n_passages):
    if not s["drafts"]:
        print("No paired drafts yet. Capture is %s." % ("on" if load_config()["enabled"] else "off (run: capture.py enable)"))
        return
    print("%s paired. %d kept as Claude wrote them (%d of those committed by Claude)." % (
        plural(s["drafts"], "draft"), s["kept_as_is"], s["claude_commits"]))
    print("\nShare of Claude's words you changed, by week:")
    for w in s["weeks"]:
        print("  %s  %3.0f%%  (%s)" % (w["week"], w["edit_ratio"] * 100, plural(w["drafts"], "draft")))
    if s["tells_removed"]:
        print("\nTells you removed: " + ", ".join("%s %d" % kv for kv in s["tells_removed"]))
    if s["words_removed"]:
        print("Words you cut most: " + ", ".join("%s %d" % kv for kv in s["words_removed"]))
        print("Words you added most: " + ", ".join("%s %d" % kv for kv in s["words_added"]))
    if n_passages:
        recent = [(r, p) for r in sorted(records, key=lambda r: r["final_time"], reverse=True) for p in r.get("passages", [])]
        print("\nRecent changes (Claude, then yours):")
        for r, p in recent[:n_passages]:
            print("\n  [%s %s, %s]\n  - %s\n  + %s" % (r["repo"], r["path"], r["final"][:10], p["before"], p["after"] or "(cut)"))


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["snapshot"]:  # the hook's path: skip argparse, which is most of the start-up time
        try:
            snapshot(json.load(sys.stdin))
        except Exception:  # a hook must never get in the way of the session
            pass
        return 0
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["enable", "disable", "status", "snapshot", "pair", "report"])
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="with enable: never record paths like this")
    ap.add_argument("--numbers-only", action="store_true", help="with enable: keep counts, never the text")
    ap.add_argument("--repo", metavar="DIR", help="with pair: only drafts in this repo")
    ap.add_argument("--quiet", action="store_true", help="with pair: print nothing, and only pair the current folder's repo")
    ap.add_argument("--budget", type=float, metavar="SECONDS", help="with pair: stop after this long")
    ap.add_argument("--json", action="store_true", help="with report: print JSON")
    ap.add_argument("--passages", type=int, default=0, metavar="N", help="with report: also print the N most recent changes")
    ap.add_argument("--version", action="version", version="capture " + __version__)
    args = ap.parse_args(argv)

    if args.command == "snapshot":
        return main(["snapshot"])
    cfg = load_config()
    if args.command in ("enable", "disable"):
        cfg["enabled"] = args.command == "enable"
        if args.command == "enable":
            cfg["exclude"] = sorted(set(cfg["exclude"]) | set(args.exclude))
            cfg["numbers_only"] = cfg["numbers_only"] or args.numbers_only
        save_private(CONFIG, json.dumps(cfg, indent=2) + "\n")
        print("Capture is %s. Settings: %s" % ("on" if cfg["enabled"] else "off", CONFIG))
        return 0
    if args.command == "status":
        waiting = len(list(DRAFTS.glob("*.json"))) if DRAFTS.is_dir() else 0
        print("Capture is %s. %s still open for a commit, %s in %s." % (
            "on" if cfg["enabled"] else "off", plural(waiting, "draft"), plural(len(load_records()), "pair"), EDITS))
        if cfg["exclude"]:
            print("Never recorded: " + ", ".join(cfg["exclude"]))
        return 0
    if args.command == "pair":
        repo = args.repo
        if args.quiet and not repo:
            root = repo_root(Path.cwd() / "x")
            if not root:
                return 0
            repo = str(root)
        paired, waiting, closed = pair(repo=os.path.realpath(repo) if repo else None, budget=args.budget)
        if not args.quiet:
            print("%d paired, %d waiting for a commit, %d closed." % (paired, waiting, closed))
        return 0
    records = list(load_records().values())
    s = summarise(records)
    if args.json:
        print(json.dumps(s, indent=2))
    else:
        print_report(s, records, args.passages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
