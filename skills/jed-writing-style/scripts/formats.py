#!/usr/bin/env python3
"""Read the writing out of different file types, with stable numbering, using only the standard library.

Both the scanner and the editor build on this, so the unit numbers in a plan always match the ones the
editor uses.

A unit is one paragraph or text block. Units are numbered from 1 across the whole file, skipping empty
ones. The label says where it is in human terms, for example "Slide 3, paragraph 2".

Supported:
    .md .markdown .txt .rst .adoc   the whole file is one text, edited by exact match
    .docx                           paragraphs in the body, headers, footers, footnotes and endnotes
    .pptx                           paragraphs on slides (in display order) and speaker notes
    .html .htm                      visible text, never tags, attributes, scripts or styles
    .ipynb                          markdown cells
"""
import html
import json
import posixpath
import re
import zipfile
from collections import namedtuple
from html.parser import HTMLParser

Unit = namedtuple("Unit", "number label text part")

TEXT_EXT = {".md", ".markdown", ".txt", ".rst", ".adoc"}
OFFICE_EXT = {".docx", ".pptx"}
SUPPORTED = TEXT_EXT | OFFICE_EXT | {".html", ".htm", ".ipynb"}
# Formats that hold writing but can't be edited in place. The plan says to edit the source instead.
UNEDITABLE = {".pdf": "edit the file it was made from", ".xlsx": "spreadsheet text is data, edit it in Excel",
              ".doc": "old Word format, save as .docx first", ".ppt": "old PowerPoint format, save as .pptx first",
              ".pages": "export to .docx first", ".key": "export to .pptx first"}


# ---------------------------------------------------------------------------
# Office files: paragraphs inside the XML
# ---------------------------------------------------------------------------

# One regex walks the XML in order and reports text nodes and paragraph ends. Nothing is re-serialised,
# so everything outside the text stays byte for byte as Word or PowerPoint wrote it.
# The lookahead after "<w:t" stops it matching <w:tab/>, <w:tbl>, <w:tc> and similar tags.
def _tokens(prefix):
    p = re.escape(prefix)
    return re.compile(
        r"(?P<open><%(p)s:t(?:\s[^>]*)?>)(?P<text>[^<]*)</%(p)s:t>"
        r"|<%(p)s:t(?:\s[^>]*)?/>"
        r"|(?P<tab><%(p)s:tab\s*/>)"
        r"|(?P<br><%(p)s:br(?:\s[^>]*)?/>)"
        r"|(?P<end></%(p)s:p>)" % {"p": p})


TOKENS = {"w": _tokens("w"), "a": _tokens("a")}

Node = namedtuple("Node", "open_start open_end text_start text_end raw text")
Paragraph = namedtuple("Paragraph", "index nodes segments text")


def xml_decode(raw):
    return html.unescape(raw)  # handles &amp; &lt; &gt; &quot; &apos; and numeric references


def xml_encode(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_paragraphs(xml, prefix):
    """Split an XML part into paragraphs. Each has its text nodes (with exact positions) and its text.

    segments is a list of (node or None, text). A tab or a line break is a one-character segment with no
    node, so an edit can refuse to span it.
    """
    paragraphs, nodes, segments = [], [], []
    for m in TOKENS[prefix].finditer(xml):
        if m.group("open"):
            raw = m.group("text")
            node = Node(m.start("open"), m.end("open"), m.start("text"), m.end("text"), raw, xml_decode(raw))
            nodes.append(node)
            segments.append((node, node.text))
        elif m.group("tab") or m.group("br"):
            segments.append((None, " "))
        elif m.group("end"):
            text = "".join(t for _, t in segments)
            paragraphs.append(Paragraph(len(paragraphs), nodes, segments, text))
            nodes, segments = [], []
    if segments:  # text after the last paragraph end, in a malformed part
        paragraphs.append(Paragraph(len(paragraphs), nodes, segments, "".join(t for _, t in segments)))
    return paragraphs


def _natural(name):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def _read_rels(z, rels_name):
    try:
        xml = z.read(rels_name).decode("utf8")
    except KeyError:
        return {}
    rels = {}
    for m in re.finditer(r"<Relationship\b([^>]*)/?>", xml):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        if "Id" in attrs and "Target" in attrs:
            rels[attrs["Id"]] = attrs["Target"]
    return rels


def _resolve(base_dir, target):
    return posixpath.normpath(target.lstrip("/")) if target.startswith("/") else posixpath.normpath(posixpath.join(base_dir, target))


def docx_parts(z):
    """(part name, prefix, label) in reading order."""
    names = set(z.namelist())
    parts = []
    if "word/document.xml" in names:
        parts.append(("word/document.xml", "w", "Paragraph"))
    for kind, label in (("header", "Header"), ("footer", "Footer")):
        for n in sorted((n for n in names if re.fullmatch(r"word/%s\d*\.xml" % kind, n)), key=_natural):
            parts.append((n, "w", "%s %s paragraph" % (label, re.sub(r"\D", "", n) or "1")))
    for n, label in (("word/footnotes.xml", "Footnote"), ("word/endnotes.xml", "Endnote")):
        if n in names:
            parts.append((n, "w", label))
    return parts


def pptx_parts(z):
    """(part name, prefix, label) with slides in display order, each followed by its notes."""
    names = set(z.namelist())
    order = []
    try:
        pres = z.read("ppt/presentation.xml").decode("utf8")
        rels = _read_rels(z, "ppt/_rels/presentation.xml.rels")
        for rid in re.findall(r'<p:sldId\b[^>]*\br:id="([^"]+)"', pres):
            if rid in rels:
                order.append(_resolve("ppt", rels[rid]))
    except KeyError:
        pass
    order = [n for n in order if n in names]
    if not order:
        order = sorted((n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)), key=_natural)
    parts = []
    for i, slide in enumerate(order, 1):
        parts.append((slide, "a", "Slide %d, paragraph" % i))
        rels = _read_rels(z, "ppt/slides/_rels/%s.rels" % posixpath.basename(slide))
        for target in rels.values():
            if "notesSlide" in target:
                notes = _resolve("ppt/slides", target)
                if notes in names:
                    parts.append((notes, "a", "Notes for slide %d, paragraph" % i))
    return parts


def office_units(path, kind):
    """All units in a .docx or .pptx, numbered. Returns (units, parts) where parts maps part name to paragraphs."""
    units, parsed = [], {}
    with zipfile.ZipFile(path) as z:
        parts = docx_parts(z) if kind == ".docx" else pptx_parts(z)
        number = 0
        for name, prefix, label in parts:
            paragraphs = parse_paragraphs(z.read(name).decode("utf8"), prefix)
            parsed[name] = (prefix, paragraphs)
            k = 0
            for p in paragraphs:
                if not p.text.strip():
                    continue
                number += 1
                k += 1
                units.append(Unit(number, "%s %d" % (label, k), p.text, name))
    return units, parsed


# ---------------------------------------------------------------------------
# HTML: visible text only
# ---------------------------------------------------------------------------

class _Visible(HTMLParser):
    """Collects text segments outside script, style and similar, with their offsets in the source."""
    SKIP = {"script", "style", "noscript", "template", "svg", "code", "pre"}

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.depth, self.spans = source, 0, []
        self.line_starts = [0]
        for m in re.finditer("\n", source):
            self.line_starts.append(m.end())

    def position(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if not self.depth and data.strip():
            start = self.position()
            self.spans.append((start, start + len(data)))


def html_spans(source):
    parser = _Visible(source)
    parser.feed(source)
    parser.close()
    return parser.spans


# ---------------------------------------------------------------------------
# Notebooks: markdown cells
# ---------------------------------------------------------------------------

def notebook_cells(source):
    data = json.loads(source)
    return data, [c for c in data.get("cells", []) if c.get("cell_type") == "markdown"]


def cell_text(cell):
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def notebook_roundtrips(source):
    """True if loading and dumping the notebook gives back the same text. Only then is editing it safe."""
    data = json.loads(source)
    indent = 1 if source.startswith('{\n "') else 2 if source.startswith('{\n  "') else 4 if source.startswith('{\n    "') else None
    if indent is None:
        return False, None
    return json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if source.endswith("\n") else "") == source, indent


# ---------------------------------------------------------------------------
# The one entry point the scanner and the checker use
# ---------------------------------------------------------------------------

def read_units(path):
    """Units for any supported file. Raises OSError, zipfile.BadZipFile or ValueError on a bad file."""
    suffix = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if suffix in OFFICE_EXT:
        return office_units(path, suffix)[0]
    with open(path, encoding="utf8", errors="replace") as f:
        raw = f.read()
    if suffix in (".html", ".htm"):
        units = []
        for start, end in html_spans(raw):
            text = " ".join(html.unescape(raw[start:end]).split())
            units.append(Unit(len(units) + 1, "Text %d" % (len(units) + 1), text, path))
        return units
    if suffix == ".ipynb":
        _, cells = notebook_cells(raw)
        units = []
        for i, cell in enumerate(cells, 1):
            text = cell_text(cell)
            if text.strip():
                units.append(Unit(len(units) + 1, "Markdown cell %d" % i, text, path))
        return units
    return [Unit(1, "Whole file", raw, path)]


def units_text(units):
    return "\n".join(u.text for u in units)
