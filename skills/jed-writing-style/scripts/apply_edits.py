#!/usr/bin/env python3
"""Apply approved text edits to files of any supported type, safely.

This is the apply step of the plan-first restyle. It makes exact replacements and nothing else. It
needs no libraries. Word and PowerPoint files are edited by changing only the text inside the XML, so
fonts, layout, images, comments and everything else stay exactly as they were.

Usage:
    python3 apply_edits.py edits.json                   apply the edits
    python3 apply_edits.py edits.json --dry-run         report what would change, write nothing
    python3 apply_edits.py edits.json --backup DIR      copy each original into DIR before changing it
    python3 apply_edits.py edits.json --allow-dirty     edit files that have uncommitted changes in git
    python3 apply_edits.py --units deck.pptx            list a file's units with their numbers and labels
    python3 apply_edits.py edits.json --json            the report as JSON

edits.json:
    {"edits": [
      {"id": "1.1", "file": "README.md", "before": "In order to start", "after": "To start"},
      {"id": "2.3", "file": "deck.pptx", "before": "seamless", "after": "smooth", "where": "Slide 3"},
      {"id": "3.1", "file": "docs/old.md", "before": "serves as", "after": "is", "all": true}
    ]}

    where   narrows the search. A number is a line in text and source files, and a unit number in Word,
            PowerPoint, HTML and notebooks (the numbers plan_scan.py and --units print). Text such
            as "Slide 3" matches a unit label that starts with it.
    all     replace every match. Without it, a change must match exactly once or it is skipped.
    allow_placeholder
            set true to let an After text keep a [bracketed placeholder]. Otherwise it is skipped.

Each edit ends as one of: applied, not_found, ambiguous, unsupported, error. A skipped edit never stops
the others. A file is written only if every part of it still parses afterwards.

In a git repo, a file with uncommitted changes (or one git doesn't know yet) is skipped, because git
could not undo the edit. Pass --backup to keep a copy and edit it anyway, or --allow-dirty.

Exit codes: 0 every edit applied, 1 some were skipped, 2 bad input.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_check  # noqa: E402
import formats  # noqa: E402

__version__ = "1.1.0"

# A slide's text box does not grow with its text, so an edit that makes it much longer is flagged.
GROWTH_NOTE = 0.25


class Skip(Exception):
    """An edit that can't be applied. The status and detail go in the report."""

    def __init__(self, status, detail):
        super().__init__(detail)
        self.status, self.detail = status, detail


def git_state(root, path):
    """'clean' or 'dirty' for a file in a git repo, or None if root isn't a repo (or git is missing)."""
    try:
        out = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", str(path)],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return "dirty" if out.stdout.strip() else "clean"


def find_all(text, sub):
    found, i = [], text.find(sub)
    while i != -1:
        found.append(i)
        i = text.find(sub, i + len(sub))
    return found


def parse_where(where):
    if where is None or where == "":
        return None
    if isinstance(where, int) or (isinstance(where, str) and where.strip().isdigit()):
        return int(where)
    return str(where).strip().lower()


def pick(matches, where, replace_all, describe):
    """Narrow matches by `where`, then decide. matches are (position, number, label) tuples."""
    where = parse_where(where)
    if isinstance(where, int):
        matches = [m for m in matches if m[1] == where]
    elif isinstance(where, str):
        matches = [m for m in matches if m[2].lower() == where or m[2].lower().startswith(where)]
    if not matches:
        raise Skip("not_found", "the Before text was not found" + (" at that place" if where is not None else ""))
    if len(matches) > 1 and not replace_all:
        places = ", ".join(m[2] for m in matches[:6])
        raise Skip("ambiguous", "found %d times (%s). Add where, or set all" % (len(matches), places))
    return matches


# "[Speed figure.]" is a gap the plan left for Jed to fill. Two or more words inside brackets, and not a
# link or a citation, so "[1]" and "[text](url)" are fine.
PLACEHOLDER = re.compile(r"\[[^\]\n]*\s[^\]\n]*\](?![(\[])")
MARKER = re.compile(r"^(#|//|--|\*|/\*)\s?")


def unwrap(before, after):
    """Drop a comment marker or surrounding quotes that both texts share, so they match a comment or string body."""
    for _ in range(2):
        mb, ma = MARKER.match(before), MARKER.match(after)
        if mb and ma and mb.group(0) == ma.group(0):
            before, after = before[mb.end():], after[ma.end():]
        elif (len(before) > 1 and before[0] == before[-1] and before[0] in "\"'"
              and len(after) > 1 and after[0] == after[-1] == before[0]):
            before, after = before[1:-1], after[1:-1]
        else:
            break
    return before, after


def check_text(edit, suffix):
    if not edit.get("allow_placeholder") and PLACEHOLDER.search(edit["after"]) and not PLACEHOLDER.search(edit["before"]):
        raise Skip("unsupported", "After still has a placeholder (%s). Fill it in first, or set allow_placeholder"
                   % PLACEHOLDER.search(edit["after"]).group(0)[:40])
    if edit["before"] == edit["after"]:
        raise Skip("unsupported", "Before and After are the same")
    if not edit["before"].strip():
        raise Skip("unsupported", "Before is empty")
    if suffix in formats.OFFICE_EXT and ("\n" in edit["before"] or "\n" in edit["after"]):
        raise Skip("unsupported", "Word and PowerPoint edits work one paragraph at a time. Split it into one change per paragraph")


# ---------------------------------------------------------------------------
# Plain text and source files
# ---------------------------------------------------------------------------

def line_of(text, index):
    return text.count("\n", 0, index) + 1


def edit_text(text, suffix, edits):
    results = {}
    is_code = suffix in ai_check.CODE_EXT
    for e in edits:
        try:
            check_text(e, suffix)
            masked = ai_check.extract_comments(text, suffix, strings=True) if is_code else None
            candidates = [(e["before"], e["after"])]
            if is_code and unwrap(e["before"], e["after"]) != candidates[0]:
                candidates.append(unwrap(e["before"], e["after"]))  # the plan may include the # or the quotes
            matches, before, after = [], e["before"], e["after"]
            for before, after in candidates:
                for i in find_all(text, before):
                    if masked is not None and masked[i:i + len(before)] != before:
                        continue  # inside code, not a comment or a sentence-like string
                    matches.append((i, line_of(text, i), "line %d" % line_of(text, i)))
                if matches:
                    break
            if not matches and is_code and any(b in text for b, _ in candidates):
                raise Skip("unsupported", "that text is code, not a comment or a user-facing string")
            chosen = pick(matches, e.get("where"), e.get("all"), None)
            for i, _, _ in sorted(chosen, reverse=True):
                text = text[:i] + after + text[i + len(before):]
            results[e["id"]] = ("applied", len(chosen), "")
        except Skip as s:
            results[e["id"]] = (s.status, 0, s.detail)
    return text, results


def validate_source(path, text, suffix):
    if suffix == ".py":
        compile(text, str(path), "exec")
    elif suffix == ".json":
        json.loads(text)


# ---------------------------------------------------------------------------
# Word and PowerPoint
# ---------------------------------------------------------------------------

def ensure_preserve(xml, node):
    """Add xml:space="preserve" to a text node's tag, so leading and trailing spaces survive."""
    tag = xml[node.open_start:node.open_end]
    if "xml:space" in tag:
        return xml
    return xml[:node.open_start] + tag[:-1] + ' xml:space="preserve">' + xml[node.open_end:]


def splice_match(xml, paragraph, index, before_len, after):
    """Replace one occurrence inside a paragraph. The new text goes into the first run it touches."""
    start, end, pos, touched = index, index + before_len, 0, []
    for node, text in paragraph.segments:
        seg_start, seg_end = pos, pos + len(text)
        pos = seg_end
        if seg_end <= start or seg_start >= end:
            continue
        if node is None:
            raise Skip("unsupported", "the text spans a tab or a line break. Edit each part separately")
        touched.append((node, max(start, seg_start) - seg_start, min(end, seg_end) - seg_start))
    if not touched:
        raise Skip("error", "could not locate the text in the XML")
    for k in range(len(touched) - 1, -1, -1):
        node, a, b = touched[k]
        if k == 0:
            new = node.text[:a] + after + (node.text[b:] if len(touched) == 1 else "")
        elif k == len(touched) - 1:
            new = node.text[b:]
        else:
            new = ""
        xml = xml[:node.text_start] + formats.xml_encode(new) + xml[node.text_end:]
        if new and (new != new.strip() or "  " in new):
            xml = ensure_preserve(xml, node)
    return xml


def edit_office(path, suffix, edits, dry_run):
    results, changed = {}, {}
    with zipfile.ZipFile(path) as z:
        parts = formats.docx_parts(z) if suffix == ".docx" else formats.pptx_parts(z)
        xml = {name: z.read(name).decode("utf8") for name, _, _ in parts}
        prefixes = {name: prefix for name, prefix, _ in parts}
    # Number the units once, from the original, so `where` always means what the plan said.
    units, _ = formats.office_units(path, suffix)
    numbering, it = {}, iter(units)
    for name, prefix, _ in parts:
        for p in formats.parse_paragraphs(xml[name], prefix):
            if p.text.strip():
                numbering[(name, p.index)] = next(it)

    applied_after = []
    for e in edits:
        try:
            check_text(e, suffix)
            matches = []
            for name in xml:
                for p in formats.parse_paragraphs(xml[name], prefixes[name]):
                    unit = numbering.get((name, p.index))
                    if unit is None:
                        continue
                    for i in find_all(p.text, e["before"]):
                        matches.append(((name, p.index, i), unit.number, unit.label))
            chosen = pick(matches, e.get("where"), e.get("all"), None)
            by_part = {}
            for (name, pidx, i), _, _ in chosen:
                by_part.setdefault(name, []).append((pidx, i))
            new_xml = dict(xml)
            for name, spots in by_part.items():
                paragraphs = formats.parse_paragraphs(new_xml[name], prefixes[name])
                # Last paragraph first, and last occurrence first, so earlier positions stay valid.
                for pidx, i in sorted(spots, reverse=True):
                    new_xml[name] = splice_match(new_xml[name], paragraphs[pidx], i, len(e["before"]), e["after"])
                    paragraphs = formats.parse_paragraphs(new_xml[name], prefixes[name])
            xml = new_xml
            changed.update({n: True for n in by_part})
            applied_after.append(e["after"])
            note = ""
            grew = (len(e["after"]) - len(e["before"])) / max(len(e["before"]), 1)
            if suffix == ".pptx" and grew > GROWTH_NOTE and len(e["after"]) - len(e["before"]) >= 8:
                note = "grew %d%%: check that slide for text running out of its box" % round(grew * 100)
            results[e["id"]] = ("applied", len(chosen), note)
        except Skip as s:
            results[e["id"]] = (s.status, 0, s.detail)

    if not changed:
        return None, results
    for name in changed:  # a part that no longer parses would make the file unopenable
        try:
            ET.fromstring(xml[name].encode("utf8"))
        except ET.ParseError as err:
            raise Skip("error", "the edit would leave %s malformed (%s). Nothing was written" % (name, err))
    if dry_run:
        return None, results
    out = tempfile.NamedTemporaryFile(delete=False, dir=str(Path(path).parent), suffix=".tmp")
    out.close()
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(out.name, "w") as zout:
        for item in zin.infolist():
            data = xml[item.filename].encode("utf8") if item.filename in changed else zin.read(item.filename)
            zout.writestr(item, data)
    # Read it back the way a user's app would, and check every After is really there.
    try:
        text = formats.units_text(formats.office_units(out.name, suffix)[0])
        missing = [a for a in applied_after if a not in text]
        if missing:
            raise Skip("error", "after writing, this text was not found: %r. Nothing was changed" % missing[0])
    except (zipfile.BadZipFile, KeyError, Skip):
        os.unlink(out.name)
        raise
    return out.name, results


# ---------------------------------------------------------------------------
# HTML and notebooks
# ---------------------------------------------------------------------------

def flexible(before):
    """Match the Before text however the source wraps its whitespace."""
    return re.compile(r"\s+".join(re.escape(w) for w in before.split()))


def edit_html(text, edits):
    results = {}
    for e in edits:
        try:
            check_text(e, ".html")
            if "<" in e["after"] or ">" in e["after"]:
                raise Skip("unsupported", "After contains < or >, which would change the markup")
            after = re.sub(r"&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)", "&amp;", e["after"])
            pattern, matches = flexible(e["before"]), []
            for n, (start, end) in enumerate(formats.html_spans(text), 1):
                for m in pattern.finditer(text[start:end]):
                    matches.append(((start + m.start(), start + m.end()), n, "Text %d" % n))
            chosen = pick(matches, e.get("where"), e.get("all"), None)
            for (a, b), _, _ in sorted(chosen, reverse=True):
                text = text[:a] + after + text[b:]
            results[e["id"]] = ("applied", len(chosen), "")
        except Skip as s:
            results[e["id"]] = (s.status, 0, s.detail)
    return text, results


def edit_notebook(raw, edits):
    ok, indent = formats.notebook_roundtrips(raw)
    if not ok:
        reason = "saving this notebook would change its formatting beyond the text. Edit it by hand"
        return raw, {e["id"]: ("unsupported", 0, reason) for e in edits}
    data, cells = formats.notebook_cells(raw)
    # Same numbering as formats.read_units: units count the non-empty markdown cells, labels count all of them.
    numbered = [(c, formats.cell_text(c), i) for i, c in enumerate(cells, 1)]
    numbered = [(c, t, i) for c, t, i in numbered if t.strip()]
    results = {}
    for e in edits:
        try:
            check_text(e, ".ipynb")
            matches = []
            for n, (cell, text, cell_no) in enumerate(numbered, 1):
                for i in find_all(text, e["before"]):
                    matches.append(((n - 1, i), n, "Markdown cell %d" % cell_no))
            chosen = pick(matches, e.get("where"), e.get("all"), None)
            for (k, i), _, _ in sorted(chosen, reverse=True):
                cell, text, cell_no = numbered[k]
                new = text[:i] + e["after"] + text[i + len(e["before"]):]
                numbered[k] = (cell, new, cell_no)
                cell["source"] = new.splitlines(keepends=True) if isinstance(cell.get("source"), list) else new
            results[e["id"]] = ("applied", len(chosen), "")
        except Skip as s:
            results[e["id"]] = (s.status, 0, s.detail)
    out = json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if raw.endswith("\n") else "")
    return out, results


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def write_atomic(path, data):
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf8", newline="") as f:
        f.write(data)
    shutil.copymode(path, tmp)
    os.replace(tmp, path)


def process_file(path, edits, dry_run, backup_dir, root, allow_dirty=False):
    """Apply all edits for one file. Returns {edit id: (status, count, detail)}."""
    suffix = path.suffix.lower()
    skip_all = lambda status, detail: {e["id"]: (status, 0, detail) for e in edits}
    if not path.is_file():
        return skip_all("error", "file not found")
    if suffix in formats.UNEDITABLE:
        return skip_all("unsupported", "%s files can't be edited here: %s" % (suffix, formats.UNEDITABLE[suffix]))
    if suffix not in formats.SUPPORTED and suffix not in ai_check.CODE_EXT:
        return skip_all("unsupported", "%s files are not supported" % (suffix or "this kind of"))

    if not dry_run and not backup_dir and not allow_dirty and git_state(root, path) == "dirty":
        return skip_all("error", "git has uncommitted changes in this file, so it could not undo the edit. "
                                 "Commit or stash first, or pass --backup or --allow-dirty")
    new_path = None
    try:
        if suffix in formats.OFFICE_EXT:
            new_path, results = edit_office(path, suffix, edits, dry_run)
            data = None
        else:
            raw = path.read_text(encoding="utf8")
            if suffix in (".html", ".htm"):
                data, results = edit_html(raw, edits)
            elif suffix == ".ipynb":
                data, results = edit_notebook(raw, edits)
            else:
                data, results = edit_text(raw, suffix, edits)
            if data == raw:
                data = None
            if data is not None and suffix in ai_check.CODE_EXT:
                validate_source(path, data, suffix)
    except Skip as s:
        return skip_all(s.status, s.detail)
    except (SyntaxError, ValueError) as err:
        return skip_all("error", "the result would not be valid (%s). Nothing was written" % err)
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError) as err:
        return skip_all("error", "could not read or write it: %s" % err)

    if (new_path or data is not None) and not dry_run:
        if backup_dir:
            target = backup_dir / path.relative_to(root) if root in path.parents else backup_dir / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        if new_path:
            shutil.copymode(path, new_path)
            os.replace(new_path, path)
        else:
            write_atomic(path, data)
    elif new_path:
        os.unlink(new_path)
    return results


def run(spec, dry_run=False, backup=None, root=None, allow_dirty=False):
    root = Path(root or Path.cwd()).resolve()
    backup_dir = Path(backup).resolve() if backup else None
    by_file = {}
    for e in spec.get("edits", []):
        for key in ("id", "file", "before", "after"):
            if key not in e:
                raise ValueError("every edit needs id, file, before and after. Missing %s in %r" % (key, e))
        by_file.setdefault(e["file"], []).append(e)
    report = []
    for rel, edits in by_file.items():
        path = (root / rel).resolve()
        if root not in path.parents and path != root:
            results = {e["id"]: ("error", 0, "that path is outside the project folder") for e in edits}
        else:
            results = process_file(path, edits, dry_run, backup_dir, root, allow_dirty)
        for e in edits:
            status, count, detail = results[e["id"]]
            report.append({"id": e["id"], "file": rel, "status": status, "count": count, "detail": detail})
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edits", nargs="?", help="edits.json")
    ap.add_argument("--dry-run", action="store_true", help="report what would change and write nothing")
    ap.add_argument("--backup", metavar="DIR", help="copy each original into DIR before changing it")
    ap.add_argument("--allow-dirty", action="store_true", help="edit files that have uncommitted changes in git")
    ap.add_argument("--root", metavar="DIR", help="the project folder. Edits may not leave it (default: current folder)")
    ap.add_argument("--units", metavar="FILE", help="list a file's units with numbers and labels, then exit")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    ap.add_argument("--version", action="version", version="apply_edits " + __version__)
    args = ap.parse_args(argv)

    if args.units:
        try:
            for u in formats.read_units(args.units):
                print("%4d  %-34s %s" % (u.number, u.label, " ".join(u.text.split())[:100]))
        except (OSError, ValueError, zipfile.BadZipFile) as err:
            print("apply_edits: cannot read %s: %s" % (args.units, err), file=sys.stderr)
            return 2
        return 0
    if not args.edits:
        ap.error("give an edits.json, or --units FILE")
    try:
        spec = json.loads(Path(args.edits).read_text(encoding="utf8"))
        report = run(spec, args.dry_run, args.backup, args.root, args.allow_dirty)
    except (OSError, ValueError) as err:
        print("apply_edits: %s" % err, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for r in report:
            note = "  " + r["detail"] if r["detail"] else ""
            print("%-8s %-8s %s%s" % (r["id"], r["status"] + ("*%d" % r["count"] if r["count"] > 1 else ""), r["file"], note))
        applied = sum(1 for r in report if r["status"] == "applied")
        print("\n%d of %d edits %s%s." % (applied, len(report), "would apply" if args.dry_run else "applied",
                                         "" if applied == len(report) else ", the rest were skipped"))
    return 0 if all(r["status"] == "applied" for r in report) else 1


if __name__ == "__main__":
    sys.exit(main())
