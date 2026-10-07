#!/usr/bin/env python3
"""Check a Word or PowerPoint file after an edit, in place of opening it.

It answers the questions a person would answer by opening the file: is it intact, did only the text
change, what changed, and could the new text overflow. It needs no libraries. If python-docx, python-pptx
or LibreOffice happen to be installed, it uses them for extra checks.

Usage:
    python3 verify_office.py deck.pptx --against deck-original.pptx
    python3 verify_office.py deck.pptx --git                 compare with the last commit
    python3 verify_office.py deck.pptx                       integrity checks only
    python3 verify_office.py deck.pptx --git --render out/   also render pages to PDF and PNG, if LibreOffice is installed
    python3 verify_office.py deck.pptx --git --json

Checks:
    intact       the zip is sound, every XML part parses, every internal link points at a real part
    text only    nothing but text changed: every other byte of every changed part is identical
    paragraphs   the paragraph count is unchanged
    changes      every changed paragraph, before and after
    growth       text that grew a lot on a slide, where it might overflow its box
    opens        the file opens in python-docx or python-pptx, when installed
    render       page counts match before and after, when LibreOffice is installed

Exit codes: 0 nothing failed (warnings are fine), 1 something failed, 2 bad input.
"""
import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import formats  # noqa: E402

__version__ = "1.0.0"

# A slide's text box does not grow with its text. Text more than this much longer than before may overflow.
GROWTH_WARN = 0.25
# Most pages worth turning into pictures for a person (or a session) to look at.
MAX_PNG_PAGES = 12
PASS, WARN, FAIL, SKIP = "pass", "warn", "fail", "skip"
MARK = {PASS: "ok  ", WARN: "warn", FAIL: "FAIL", SKIP: "skip"}


def check(name, status, detail=""):
    return {"check": name, "status": status, "detail": detail}


# ---------------------------------------------------------------------------
# Intact: the package holds together
# ---------------------------------------------------------------------------

def check_intact(path):
    out = []
    try:
        z = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as e:
        return [check("intact", FAIL, "not a valid zip file: %s" % e)]
    with z:
        bad = z.testzip()
        if bad:
            return [check("intact", FAIL, "the zip is damaged at %s" % bad)]
        names = set(z.namelist())
        if "[Content_Types].xml" not in names:
            return [check("intact", FAIL, "[Content_Types].xml is missing, so Office will not open it")]
        broken = []
        for name in sorted(names):
            if name.endswith((".xml", ".rels")):
                try:
                    ET.fromstring(z.read(name))
                except ET.ParseError as e:
                    broken.append("%s (%s)" % (name, e))
        if broken:
            return [check("intact", FAIL, "XML that does not parse: " + "; ".join(broken[:3]))]
        missing = []
        for rels in sorted(n for n in names if n.endswith(".rels")):
            base = posixpath.dirname(posixpath.dirname(rels))  # the folder of the part the rels belong to
            for m in re.finditer(r"<Relationship\b([^>]*)/?>", z.read(rels).decode("utf8", "replace")):
                attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
                if attrs.get("TargetMode") == "External" or "Target" not in attrs:
                    continue
                target = attrs["Target"]
                part = posixpath.normpath(target.lstrip("/")) if target.startswith("/") else posixpath.normpath(posixpath.join(base, target))
                if part not in names:
                    missing.append("%s -> %s" % (rels, part))
        if missing:
            out.append(check("intact", WARN, "links to parts that are not in the file: " + "; ".join(missing[:3])))
        else:
            out.append(check("intact", PASS, "%d parts, all XML parses, all links resolve" % len(names)))
    return out


def check_opens(path):
    suffix = Path(path).suffix.lower()
    try:
        if suffix == ".docx":
            import docx  # noqa: F401
            docx.Document(path)
            return check("opens", PASS, "opens in python-docx")
        import pptx  # noqa: F401
        pptx.Presentation(path)
        return check("opens", PASS, "opens in python-pptx")
    except ImportError:
        return check("opens", SKIP, "python-%s is not installed" % ("docx" if suffix == ".docx" else "pptx"))
    except Exception as e:  # any failure to open is the answer
        return check("opens", FAIL, "the library could not open it: %s" % e)


def settle_opens(result, original):
    """A library is pickier than Word. Only call it a failure if the original opened and this one doesn't."""
    if result["status"] != FAIL:
        return result
    if original and check_opens(original)["status"] == PASS:
        return check("opens", FAIL, result["detail"] + ". The original opens, so the edit broke it")
    why = "the original could not be checked either" if original else "no original to compare with"
    return check("opens", WARN, result["detail"] + ". This may be an unusual file, not a broken one (%s)" % why)


# ---------------------------------------------------------------------------
# Compare with the original
# ---------------------------------------------------------------------------

def strip_text(xml):
    """The XML with every text node emptied and xml:space ignored, to see if anything but text differs."""
    xml = re.sub(r"<(w|a):t(?:\s[^>]*)?>[^<]*</\1:t>", r"<\1:t/>", xml)
    return xml.replace(' xml:space="preserve"', "")


def compare(path, original):
    suffix = Path(path).suffix.lower()
    checks, changes = [], []
    try:
        with zipfile.ZipFile(path) as zn, zipfile.ZipFile(original) as zo:
            if [i.filename for i in zo.infolist()] != [i.filename for i in zn.infolist()]:
                checks.append(check("text only", FAIL, "the list of parts in the file changed"))
                return checks, changes
            changed = [n for n in zo.namelist() if zo.read(n) != zn.read(n)]
            non_text = []
            for n in changed:
                if not n.endswith(".xml") or strip_text(zo.read(n).decode("utf8", "replace")) != strip_text(zn.read(n).decode("utf8", "replace")):
                    non_text.append(n)
            if non_text:
                checks.append(check("text only", FAIL, "more than text changed in: " + ", ".join(non_text[:4])))
            elif not changed:
                checks.append(check("text only", PASS, "nothing changed"))
            else:
                checks.append(check("text only", PASS, "only text changed, in %d part%s: %s" % (
                    len(changed), "" if len(changed) == 1 else "s", ", ".join(changed[:4]) + (" ..." if len(changed) > 4 else ""))))
    except (zipfile.BadZipFile, OSError) as e:
        return [check("text only", FAIL, "could not compare: %s" % e)], changes

    new_units, old_units = formats.read_units(path), formats.read_units(original)
    if len(new_units) != len(old_units):
        checks.append(check("paragraphs", FAIL, "the paragraph count changed from %d to %d" % (len(old_units), len(new_units))))
        return checks, changes
    checks.append(check("paragraphs", PASS, "%d paragraphs before and after" % len(new_units)))
    for a, b in zip(old_units, new_units):
        if a.text != b.text:
            changes.append({"unit": b.number, "label": b.label, "before": a.text, "after": b.text})
    checks.append(check("changes", PASS, "%d paragraph%s changed" % (len(changes), "" if len(changes) == 1 else "s")))

    if suffix == ".pptx":
        grown = [c for c in changes if len(c["after"]) > len(c["before"]) * (1 + GROWTH_WARN) and len(c["after"]) - len(c["before"]) >= 8]
        if grown:
            where = ", ".join("%s (+%d%%)" % (c["label"], round(100 * (len(c["after"]) - len(c["before"])) / max(len(c["before"]), 1))) for c in grown[:5])
            checks.append(check("growth", WARN, "longer text may overflow its box. Look at: " + where))
        else:
            checks.append(check("growth", PASS, "no changed paragraph grew by more than %d%%" % (GROWTH_WARN * 100)))
    return checks, changes


# ---------------------------------------------------------------------------
# Render: only if LibreOffice is installed
# ---------------------------------------------------------------------------

def pdf_pages(pdf):
    data = Path(pdf).read_bytes()
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", data))


def render(path, original, outdir):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return [check("render", SKIP, "LibreOffice is not installed, so nothing was rendered. Open the file in "
                                     "Word or PowerPoint and look, or install LibreOffice")], []
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    pages, pdfs = {}, {}
    for tag, src in (("after", path), ("before", original)):
        if not src:
            continue
        work = outdir / tag
        work.mkdir(exist_ok=True)
        try:
            subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(work), str(src)],
                           capture_output=True, timeout=180, check=True)
        except (OSError, subprocess.SubprocessError) as e:
            return [check("render", WARN, "LibreOffice could not convert the %s file: %s" % (tag, e))], []
        pdf = work / (Path(src).stem + ".pdf")
        if not pdf.exists():
            return [check("render", WARN, "LibreOffice produced no PDF for the %s file" % tag)], []
        pages[tag], pdfs[tag] = pdf_pages(pdf), pdf
    out = []
    if "before" in pages and pages["before"] != pages["after"]:
        out.append(check("render", WARN, "the page count changed from %d to %d" % (pages["before"], pages["after"])))
    else:
        out.append(check("render", PASS, "%d pages%s" % (pages["after"], ", the same as before" if "before" in pages else "")))
    pngs = []
    if shutil.which("pdftoppm"):
        prefix = outdir / "after" / "page"
        subprocess.run(["pdftoppm", "-png", "-r", "60", "-l", str(MAX_PNG_PAGES), str(pdfs["after"]), str(prefix)],
                       capture_output=True, timeout=180)
        pngs = sorted(str(p) for p in (outdir / "after").glob("page*.png"))
    return out, pngs


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def git_original(path):
    """The committed version of a file, written to a temp file. Returns its path, or None."""
    p = Path(path).resolve()
    try:
        top = subprocess.run(["git", "-C", str(p.parent), "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=30)
        if top.returncode != 0:
            return None
        rel = p.relative_to(Path(top.stdout.strip()).resolve())
        blob = subprocess.run(["git", "-C", top.stdout.strip(), "show", "HEAD:" + rel.as_posix()], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    if blob.returncode != 0:
        return None
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=p.suffix)
    tmp.write(blob.stdout)
    tmp.close()
    return tmp.name


def verify(path, original=None, render_dir=None):
    suffix = Path(path).suffix.lower()
    if suffix not in formats.OFFICE_EXT:
        raise ValueError("%s is not a .docx or .pptx file" % path)
    checks = check_intact(path)
    changes, pngs = [], []
    if checks[0]["status"] != FAIL:
        checks.append(settle_opens(check_opens(path), original))
        if original:
            more, changes = compare(path, original)
            checks += more
        if render_dir:
            more, pngs = render(path, original, render_dir)
            checks += more
    failed = any(c["status"] == FAIL for c in checks)
    return {"file": str(path), "ok": not failed, "checks": checks, "changes": changes, "images": pngs,
            "compared_with": str(original) if original else None}


def print_report(r, limit=40):
    print("%s  %s" % ("PASS" if r["ok"] else "FAIL", r["file"]))
    for c in r["checks"]:
        print("  %s  %-10s %s" % (MARK[c["status"]], c["check"], c["detail"]))
    if r["changes"]:
        print("\nChanged paragraphs:")
        for c in r["changes"][:limit]:
            print("  %3d  %s" % (c["unit"], c["label"]))
            print("       before: %s" % " ".join(c["before"].split())[:150])
            print("       after:  %s" % " ".join(c["after"].split())[:150])
        if len(r["changes"]) > limit:
            print("  and %d more" % (len(r["changes"]) - limit))
    if r["images"]:
        print("\nPages rendered for a visual check:")
        for img in r["images"]:
            print("  " + img)
    skipped = [c for c in r["checks"] if c["status"] == SKIP]
    if skipped or not r["compared_with"]:
        print("\nA person should still:")
        print("  open the file in Word or PowerPoint, and check there is no repair prompt;")
        if any(c["check"] == "growth" and c["status"] == WARN for c in r["checks"]):
            print("  look at the slides listed under growth for text running out of its box;")
        print("  use Review, Compare against the original to see the changes in place.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="the .docx or .pptx to check")
    ap.add_argument("--against", metavar="ORIGINAL", help="the file before the edit")
    ap.add_argument("--git", action="store_true", help="compare with the last commit of this file")
    ap.add_argument("--render", metavar="DIR", help="render to PDF and PNG in DIR, if LibreOffice is installed")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    ap.add_argument("--version", action="version", version="verify_office " + __version__)
    args = ap.parse_args(argv)
    if not args.file:
        ap.error("give a .docx or .pptx file")
    if args.against and args.git:
        ap.error("use --against or --git, not both")

    original, temp = args.against, None
    if args.git:
        original = temp = git_original(args.file)
        if not original:
            print("verify_office: no committed version of %s, so nothing to compare with" % args.file, file=sys.stderr)
    try:
        if not Path(args.file).is_file():
            print("verify_office: cannot read %s" % args.file, file=sys.stderr)
            return 2
        if original and not Path(original).is_file():
            print("verify_office: cannot read %s" % original, file=sys.stderr)
            return 2
        result = verify(args.file, original, args.render)
    except ValueError as e:
        print("verify_office: %s" % e, file=sys.stderr)
        return 2
    finally:
        if temp:
            try:
                Path(temp).unlink()
            except OSError:
                pass
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
