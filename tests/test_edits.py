#!/usr/bin/env python3
"""Tests for scripts/formats.py and scripts/apply_edits.py. Standard library only.

The Word and PowerPoint packages here are built by hand, so CI needs no Office library. The tests
prove the guarantees that matter: only the text changes, everything else stays byte for byte, and
anything doubtful is skipped and reported instead of guessed.

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "jed-writing-style"
APPLY = SKILL / "scripts" / "apply_edits.py"
sys.path.insert(0, str(SKILL / "scripts"))

import apply_edits  # noqa: E402
import formats  # noqa: E402
import plan_scan  # noqa: E402

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:mc="x" mc:Ignorable="w14"'
A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'

DOCUMENT = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document %s><w:body>'
    '<w:p><w:r><w:t xml:space="preserve">Hello </w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>wor</w:t></w:r>'
    '<w:r><w:t xml:space="preserve">ld, in order to win &amp; share.</w:t></w:r></w:p>'
    '<w:p><w:r><w:t>Tab</w:t></w:r><w:r><w:tab/></w:r><w:r><w:t>here and more text here.</w:t></w:r></w:p>'
    '<w:p><w:r><w:t>Second paragraph. In order to start.</w:t></w:r></w:p>'
    '<w:p/>'
    '<w:p><w:r><w:t>Plain closing line</w:t></w:r></w:p>'
    '</w:body></w:document>' % W)
HEADER = '<?xml version="1.0"?><w:hdr %s><w:p><w:r><w:t>Company header text</w:t></w:r></w:p></w:hdr>' % W


def slide(*paragraphs):
    body = "".join("<a:p><a:r><a:t>%s</a:t></a:r></a:p>" % t for t in paragraphs)
    return '<?xml version="1.0"?><p:sld %s><p:cSld><p:spTree><p:sp><p:txBody>%s</p:txBody></p:sp></p:spTree></p:cSld></p:sld>' % (A, body)


PRESENTATION = ('<?xml version="1.0"?><p:presentation %s><p:sldIdLst><p:sldId id="256" r:id="rId2"/>'
                '<p:sldId id="257" r:id="rId1"/></p:sldIdLst></p:presentation>' % A)
PRES_RELS = ('<?xml version="1.0"?><Relationships xmlns="r"><Relationship Id="rId1" Type="t" Target="slides/slide1.xml"/>'
             '<Relationship Id="rId2" Type="t" Target="slides/slide2.xml"/></Relationships>')
SLIDE1_RELS = ('<?xml version="1.0"?><Relationships xmlns="r"><Relationship Id="rId1" Type="t" '
               'Target="../notesSlides/notesSlide7.xml"/></Relationships>')


def build_zip(path, members):
    with zipfile.ZipFile(path, "w") as z:
        for name, data in members.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 2, 3, 4, 6))
            info.compress_type = zipfile.ZIP_STORED if name.endswith(".png") else zipfile.ZIP_DEFLATED
            z.writestr(info, data)


def make_docx(path):
    build_zip(path, {"[Content_Types].xml": "<Types/>", "word/document.xml": DOCUMENT, "word/header1.xml": HEADER,
                     "word/media/pic.png": b"\x89PNG-not-really"})


def make_pptx(path):
    build_zip(path, {"[Content_Types].xml": "<Types/>", "ppt/presentation.xml": PRESENTATION,
                     "ppt/_rels/presentation.xml.rels": PRES_RELS,
                     "ppt/slides/slide1.xml": slide("Slide one is shown second", "It is seamless and robust"),
                     "ppt/slides/slide2.xml": slide("Slide two is shown first"),
                     "ppt/slides/_rels/slide1.xml.rels": SLIDE1_RELS,
                     "ppt/notesSlides/notesSlide7.xml": slide("Speaker note for the second slide"),
                     "ppt/media/image1.png": b"\x89PNG-not-really"})


def digest(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


class Base(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)

    def edit(self, *edits, **kwargs):
        report = apply_edits.run({"edits": list(edits)}, root=self.root, **kwargs)
        return {r["id"]: r for r in report}

    def status(self, *edits, **kwargs):
        return {k: v["status"] for k, v in self.edit(*edits, **kwargs).items()}


class OfficeReading(Base):
    def test_docx_units(self):
        make_docx(self.root / "a.docx")
        units = formats.read_units(str(self.root / "a.docx"))
        self.assertEqual([u.number for u in units], [1, 2, 3, 4, 5])  # the empty paragraph is skipped
        self.assertEqual(units[0].text, "Hello world, in order to win & share.")
        self.assertEqual(units[1].text, "Tab here and more text here.")  # a tab reads as a space
        self.assertEqual(units[3].label, "Paragraph 4")
        self.assertEqual(units[4].label, "Header 1 paragraph 1")

    def test_pptx_follows_display_order_and_pairs_notes(self):
        make_pptx(self.root / "a.pptx")
        units = formats.read_units(str(self.root / "a.pptx"))
        self.assertEqual([u.label for u in units], [
            "Slide 1, paragraph 1", "Slide 2, paragraph 1", "Slide 2, paragraph 2",
            "Notes for slide 2, paragraph 1"])
        self.assertEqual(units[0].text, "Slide two is shown first")  # slide2.xml is displayed first

    def test_checker_reads_office_files_through_the_same_layer(self):
        import ai_check
        make_pptx(self.root / "a.pptx")
        self.assertIn("seamless", ai_check.read_text(str(self.root / "a.pptx")))


class DocxEditing(Base):
    def setUp(self):
        super().setUp()
        self.path = self.root / "a.docx"
        make_docx(self.path)
        self.original = zipfile.ZipFile(self.path)

    def units(self):
        return [u.text for u in formats.read_units(str(self.path))]

    def test_edit_across_three_runs(self):
        s = self.status({"id": "e", "file": "a.docx", "before": "world, in order to win & share", "after": "world, to win and share"})
        self.assertEqual(s["e"], "applied")
        self.assertEqual(self.units()[0], "Hello world, to win and share.")

    def test_only_text_nodes_change_everything_else_is_identical(self):
        self.edit({"id": "e", "file": "a.docx", "before": "in order to win", "after": "to win"})
        new = zipfile.ZipFile(self.path)
        self.assertEqual([i.filename for i in self.original.infolist()], [i.filename for i in new.infolist()])
        for a, b in zip(self.original.infolist(), new.infolist()):
            self.assertEqual((a.compress_type, a.date_time), (b.compress_type, b.date_time), a.filename)
            if a.filename != "word/document.xml":
                self.assertEqual(self.original.read(a.filename), new.read(a.filename), a.filename)
        strip = lambda x: re.sub(r"<w:t(?:\s[^>]*)?>[^<]*</w:t>", "<w:t/>", x.decode())
        self.assertEqual(strip(self.original.read("word/document.xml")), strip(new.read("word/document.xml")))

    def test_declared_namespaces_and_ignorable_survive(self):
        self.edit({"id": "e", "file": "a.docx", "before": "Plain closing", "after": "Plain final"})
        xml = zipfile.ZipFile(self.path).read("word/document.xml").decode()
        self.assertIn('mc:Ignorable="w14"', xml)
        self.assertIn('xmlns:mc="x"', xml)

    def test_special_characters_are_escaped_and_the_part_still_parses(self):
        self.edit({"id": "e", "file": "a.docx", "before": "Plain closing line", "after": "a < b & c > d"})
        xml = zipfile.ZipFile(self.path).read("word/document.xml")
        ET.fromstring(xml)
        self.assertEqual(self.units()[3], "a < b & c > d")

    def test_leading_and_trailing_spaces_get_xml_space_preserve(self):
        self.edit({"id": "e", "file": "a.docx", "before": "Plain closing line", "after": " padded "})
        self.assertIn('<w:t xml:space="preserve"> padded </w:t>', zipfile.ZipFile(self.path).read("word/document.xml").decode())

    def test_the_header_can_be_edited(self):
        self.assertEqual(self.status({"id": "e", "file": "a.docx", "before": "Company header", "after": "Our header"})["e"], "applied")
        self.assertIn("Our header text", self.units()[4])

    def test_ambiguous_without_where_then_pinned_then_all(self):
        edit = {"id": "e", "file": "a.docx", "before": "In order to", "after": "To"}
        # "in order to" in paragraph 1 is lower case, so only paragraph 3 matches. Make two matches instead.
        make_docx(self.path)
        two = {"id": "e", "file": "a.docx", "before": "order to", "after": "to"}
        r = self.edit(two)["e"]
        self.assertEqual(r["status"], "ambiguous")
        self.assertIn("2 times", r["detail"])
        self.assertEqual(self.edit(dict(two, where=3))["e"]["status"], "applied")
        make_docx(self.path)
        r = self.edit(dict(two, all=True))["e"]
        self.assertEqual((r["status"], r["count"]), ("applied", 2))
        self.assertNotIn("order to", " ".join(self.units()))
        self.assertEqual(self.status(edit)["e"], "not_found")

    def test_a_tab_or_multi_paragraph_edit_is_refused_not_guessed(self):
        before = digest(self.path)
        s = self.status({"id": "t", "file": "a.docx", "before": "Tab here", "after": "Tab there"},
                        {"id": "p", "file": "a.docx", "before": "share.\nTab", "after": "x"})
        self.assertEqual(s, {"t": "unsupported", "p": "unsupported"})
        self.assertEqual(before, digest(self.path))

    def test_one_skipped_edit_does_not_stop_the_others(self):
        s = self.status({"id": "bad", "file": "a.docx", "before": "not in the file", "after": "x"},
                        {"id": "ok", "file": "a.docx", "before": "Plain closing", "after": "Plain final"})
        self.assertEqual(s, {"bad": "not_found", "ok": "applied"})

    def test_dry_run_writes_nothing(self):
        before = digest(self.path)
        s = self.status({"id": "e", "file": "a.docx", "before": "Plain closing", "after": "Plain final"}, dry_run=True)
        self.assertEqual(s["e"], "applied")
        self.assertEqual(before, digest(self.path))

    def test_backup_keeps_the_original(self):
        before = digest(self.path)
        self.edit({"id": "e", "file": "a.docx", "before": "Plain closing", "after": "Plain final"}, backup=self.root / "bak")
        self.assertEqual(digest(self.root / "bak" / "a.docx"), before)
        self.assertNotEqual(digest(self.path), before)

    def test_no_temp_files_are_left_behind(self):
        self.edit({"id": "e", "file": "a.docx", "before": "Plain closing", "after": "Plain final"})
        self.assertEqual([p.name for p in self.root.iterdir() if p.suffix == ".tmp"], [])


class PptxEditing(Base):
    def setUp(self):
        super().setUp()
        self.path = self.root / "a.pptx"
        make_pptx(self.path)

    def test_where_accepts_a_slide_label(self):
        s = self.status({"id": "e", "file": "a.pptx", "before": "seamless and robust", "after": "smooth and strong", "where": "Slide 2"})
        self.assertEqual(s["e"], "applied")
        s = self.status({"id": "n", "file": "a.pptx", "before": "Speaker note", "after": "Note", "where": "Slide 2"})
        self.assertEqual(s["n"], "not_found")  # the note label starts with "Notes", not "Slide"

    def test_notes_can_be_edited(self):
        self.assertEqual(self.status({"id": "n", "file": "a.pptx", "before": "Speaker note", "after": "Note"})["n"], "applied")
        self.assertIn("Note for the second slide", [u.text for u in formats.read_units(str(self.path))][3])

    def test_untouched_slides_are_byte_identical(self):
        original = zipfile.ZipFile(self.path)
        self.edit({"id": "e", "file": "a.pptx", "before": "Slide two", "after": "Slide 2"})
        new = zipfile.ZipFile(self.path)
        changed = [i.filename for i in original.infolist() if original.read(i.filename) != new.read(i.filename)]
        self.assertEqual(changed, ["ppt/slides/slide2.xml"])

    def test_image_only_slides_are_noted(self):
        build_zip(self.root / "img.pptx", {"[Content_Types].xml": "<Types/>", "ppt/slides/slide1.xml": slide(),
                                           "ppt/slides/slide2.xml": slide("Real text")})
        self.assertIn("1 of 2", plan_scan.image_only_note(self.root / "img.pptx"))


class TextAndCodeEditing(Base):
    def write(self, name, text):
        (self.root / name).write_text(text)

    def read(self, name):
        return (self.root / name).read_text()

    def test_markdown_exact_ambiguous_where_and_all(self):
        self.write("a.md", "Use it. In order to go.\nIn order to stop.\n")
        e = {"id": "e", "file": "a.md", "before": "In order to", "after": "To"}
        self.assertEqual(self.status(e)["e"], "ambiguous")
        self.assertEqual(self.status(dict(e, where=2))["e"], "applied")
        self.assertEqual(self.read("a.md"), "Use it. In order to go.\nTo stop.\n")
        self.assertEqual(self.edit(dict(e, all=True))["e"]["count"], 1)

    def test_multi_line_before(self):
        self.write("a.md", "First line\nsecond line\n")
        self.assertEqual(self.status({"id": "e", "file": "a.md", "before": "line\nsecond", "after": "line, second"})["e"], "applied")

    def test_code_comments_and_strings_can_be_edited_but_code_cannot(self):
        self.write("a.py", 'x = robust_value  # a robust comment about the value\n'
                           'raise ValueError("Could not find the file, please check the path")\n')
        s = self.status({"id": "c", "file": "a.py", "before": "a robust comment", "after": "a comment"},
                        {"id": "s", "file": "a.py", "before": "Could not find the file", "after": "Cannot find the file"},
                        {"id": "x", "file": "a.py", "before": "robust_value", "after": "value"})
        self.assertEqual(s, {"c": "applied", "s": "applied", "x": "unsupported"})
        self.assertIn("x = robust_value  # a comment", self.read("a.py"))

    def test_an_edit_that_would_break_the_code_writes_nothing(self):
        self.write("a.py", 'raise ValueError("Could not find the file, please check the path")\n')
        before = digest(self.root / "a.py")
        s = self.status({"id": "s", "file": "a.py", "before": "Could not find the file", "after": 'Could not "find" the file'})
        self.assertEqual(s["s"], "error")
        self.assertEqual(before, digest(self.root / "a.py"))

    def test_paths_outside_the_project_are_refused(self):
        self.assertEqual(self.status({"id": "e", "file": "../elsewhere.md", "before": "a", "after": "b"})["e"], "error")

    def test_unsupported_and_uneditable_types_say_why(self):
        (self.root / "a.pdf").write_bytes(b"%PDF")
        r = self.edit({"id": "e", "file": "a.pdf", "before": "a", "after": "b"})["e"]
        self.assertEqual(r["status"], "unsupported")
        self.assertIn("made from", r["detail"])

    def test_same_before_and_after_is_refused(self):
        self.write("a.md", "hello there\n")
        self.assertEqual(self.status({"id": "e", "file": "a.md", "before": "hello", "after": "hello"})["e"], "unsupported")


@unittest.skipUnless(shutil.which("git"), "git is not installed")
class GitSafety(Base):
    def git(self, *args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.root, check=True, capture_output=True)

    def setUp(self):
        super().setUp()
        self.git("init", "-q")
        (self.root / "a.md").write_text("Hello there friend\n")
        make_docx(self.root / "a.docx")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "x")
        self.e = {"id": "e", "file": "a.md", "before": "Hello", "after": "Hi"}

    def test_a_clean_file_is_edited(self):
        self.assertEqual(self.status(self.e)["e"], "applied")

    def test_a_file_with_uncommitted_changes_is_skipped(self):
        (self.root / "a.md").write_text("Hello there friend, again\n")
        r = self.edit(self.e)["e"]
        self.assertEqual(r["status"], "error")
        self.assertIn("uncommitted", r["detail"])
        self.assertEqual((self.root / "a.md").read_text(), "Hello there friend, again\n")

    def test_a_file_git_does_not_know_is_skipped(self):
        (self.root / "new.md").write_text("Hello there friend\n")
        self.assertEqual(self.status(dict(self.e, file="new.md"))["e"], "error")

    def test_backup_or_allow_dirty_lets_it_through(self):
        (self.root / "a.md").write_text("Hello there friend, again\n")
        self.assertEqual(self.status(self.e, backup=self.root / "bak")["e"], "applied")
        (self.root / "a.md").write_text("Hello there friend, again\n")
        self.assertEqual(self.status(self.e, allow_dirty=True)["e"], "applied")

    def test_a_dry_run_ignores_it(self):
        (self.root / "a.md").write_text("Hello there friend, again\n")
        self.assertEqual(self.status(self.e, dry_run=True)["e"], "applied")

    def test_office_files_are_protected_too(self):
        edit = {"id": "e", "file": "a.docx", "before": "Plain closing", "after": "Plain final"}
        self.assertEqual(self.status(edit)["e"], "applied")  # clean
        self.assertEqual(self.status(dict(edit, before="Plain final", after="Plain last"))["e"], "error")  # now dirty


class HtmlEditing(Base):
    def test_only_visible_text_is_edited(self):
        page = ('<html><body title="a robust title"><p>This is a robust\n   platform.</p>'
                '<script>var s = "a robust platform";</script></body></html>')
        (self.root / "a.html").write_text(page)
        s = self.status({"id": "v", "file": "a.html", "before": "a robust platform", "after": "a plain platform"})
        self.assertEqual(s["v"], "applied")  # whitespace in the source can wrap differently
        out = (self.root / "a.html").read_text()
        self.assertIn("<p>This is a plain platform.</p>", out)
        self.assertIn('title="a robust title"', out)
        self.assertIn('var s = "a robust platform";', out)

    def test_markup_characters_in_after_are_refused(self):
        (self.root / "a.html").write_text("<p>Hello there friend</p>")
        self.assertEqual(self.status({"id": "e", "file": "a.html", "before": "Hello", "after": "<b>Hi</b>"})["e"], "unsupported")

    def test_bare_ampersand_is_escaped(self):
        (self.root / "a.html").write_text("<p>Hello there friend</p>")
        self.edit({"id": "e", "file": "a.html", "before": "Hello there", "after": "Tom & Jerry"})
        self.assertIn("<p>Tom &amp; Jerry friend</p>", (self.root / "a.html").read_text())


class PlanItemsTheEditorMustAccept(Base):
    """What a real plan contains: unit numbers for HTML and notebooks, comment markers and quotes in Before,
    and gaps left for Jed to fill."""

    def test_html_where_is_the_unit_number_the_scanner_prints(self):
        page = "<html><head><title>Acme</title></head><body><h1>Acme Tracker</h1>\n<p>A robust platform for all.</p></body></html>"
        (self.root / "a.html").write_text(page)
        units = formats.read_units(str(self.root / "a.html"))
        n = [u.number for u in units if "robust" in u.text][0]
        self.assertEqual(n, 3)
        self.assertEqual(self.status({"id": "e", "file": "a.html", "before": "robust", "after": "plain", "where": n})["e"], "applied")
        make = self.status({"id": "x", "file": "a.html", "before": "plain", "after": "clear", "where": 2})
        self.assertEqual(make["x"], "not_found")  # unit 2 is the heading, not the paragraph

    def test_notebook_where_matches_the_scanner_even_after_an_empty_cell(self):
        nb = {"cells": [{"cell_type": "markdown", "metadata": {}, "source": []},
                        {"cell_type": "markdown", "metadata": {}, "source": ["A robust note here.\n"]}],
              "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
        (self.root / "a.ipynb").write_text(json.dumps(nb, indent=1) + "\n")
        unit = formats.read_units(str(self.root / "a.ipynb"))[0]
        self.assertEqual((unit.number, unit.label), (1, "Markdown cell 2"))
        r = self.edit({"id": "e", "file": "a.ipynb", "before": "robust ", "after": "", "where": unit.number})["e"]
        self.assertEqual(r["status"], "applied")
        self.assertEqual(self.edit({"id": "l", "file": "a.ipynb", "before": "note", "after": "memo", "where": "Markdown cell 2"})["l"]["status"], "applied")

    def test_code_before_may_include_the_comment_marker_or_the_quotes(self):
        (self.root / "a.py").write_text('# This function is used to run a robust check\n'
                                        'raise ValueError("Moreover, we could not find the file, so check the path")\n')
        s = self.status({"id": "c", "file": "a.py", "before": "# This function is used to run a robust check", "after": "# Fail early."},
                        {"id": "s", "file": "a.py", "before": '"Moreover, we could not find the file, so check the path"',
                         "after": '"File not found. Check the path."'})
        self.assertEqual(s, {"c": "applied", "s": "applied"})
        self.assertEqual((self.root / "a.py").read_text(),
                         '# Fail early.\nraise ValueError("File not found. Check the path.")\n')

    def test_a_marker_in_only_one_of_before_and_after_is_not_stripped(self):
        (self.root / "a.py").write_text("x = 1  # a robust comment about the value here\n")
        self.assertEqual(self.status({"id": "c", "file": "a.py", "before": "# a robust comment", "after": "a comment"})["c"], "unsupported")

    def test_a_placeholder_is_never_written_unless_allowed(self):
        make_pptx(self.root / "a.pptx")
        gap = {"id": "e", "file": "a.pptx", "before": "Speaker note for the second slide", "after": "[How it works, in one sentence.]"}
        r = self.edit(gap)["e"]
        self.assertEqual(r["status"], "unsupported")
        self.assertIn("placeholder", r["detail"])
        self.assertEqual(self.status(dict(gap, allow_placeholder=True))["e"], "applied")

    def test_links_and_citations_are_not_placeholders(self):
        (self.root / "a.md").write_text("See the guide for details about this thing.\n")
        s = self.status({"id": "l", "file": "a.md", "before": "the guide", "after": "[the guide](docs/guide.md)"},
                        {"id": "c", "file": "a.md", "before": "this thing", "after": "this thing [1]"})
        self.assertEqual(s, {"l": "applied", "c": "applied"})


class NotebookEditing(Base):
    NB = {"cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# Title\n", "This robust thing is plain.\n"]},
                    {"cell_type": "code", "metadata": {}, "source": ["x = 'robust thing'\n"], "outputs": [], "execution_count": None}],
          "metadata": {}, "nbformat": 4, "nbformat_minor": 5}

    def test_markdown_cells_edit_and_code_cells_do_not(self):
        raw = json.dumps(self.NB, indent=1, ensure_ascii=False) + "\n"
        (self.root / "a.ipynb").write_text(raw)
        s = self.status({"id": "m", "file": "a.ipynb", "before": "This robust thing", "after": "This thing"},
                        {"id": "c", "file": "a.ipynb", "before": "robust thing'", "after": "thing'"})
        self.assertEqual(s, {"m": "applied", "c": "not_found"})
        data = json.loads((self.root / "a.ipynb").read_text())
        self.assertEqual(data["cells"][0]["source"], ["# Title\n", "This thing is plain.\n"])
        self.assertEqual(data["cells"][1]["source"], ["x = 'robust thing'\n"])

    def test_a_notebook_that_would_be_reformatted_is_left_alone(self):
        raw = json.dumps(self.NB, separators=(",", ":"))
        (self.root / "a.ipynb").write_text(raw)
        self.assertEqual(self.status({"id": "m", "file": "a.ipynb", "before": "This robust", "after": "This"})["m"], "unsupported")
        self.assertEqual((self.root / "a.ipynb").read_text(), raw)


class CommandLine(Base):
    def call(self, *args):
        return subprocess.run([sys.executable, str(APPLY), *args], cwd=self.root, capture_output=True, text=True)

    def test_exit_codes_and_report(self):
        (self.root / "a.md").write_text("Hello there friend\n")
        (self.root / "ok.json").write_text(json.dumps({"edits": [{"id": "e", "file": "a.md", "before": "Hello", "after": "Hi"}]}))
        (self.root / "skip.json").write_text(json.dumps({"edits": [{"id": "e", "file": "a.md", "before": "nope", "after": "x"}]}))
        self.assertEqual(self.call("ok.json").returncode, 0)
        p = self.call("skip.json")
        self.assertEqual(p.returncode, 1)
        self.assertIn("not_found", p.stdout)
        self.assertEqual(self.call("missing.json").returncode, 2)
        self.assertNotIn("Traceback", self.call("missing.json").stderr)

    def test_missing_keys_are_a_clear_error(self):
        (self.root / "bad.json").write_text(json.dumps({"edits": [{"id": "e", "file": "a.md"}]}))
        p = self.call("bad.json")
        self.assertEqual(p.returncode, 2)
        self.assertIn("before", p.stderr)

    def test_units_listing(self):
        make_pptx(self.root / "a.pptx")
        p = self.call("--units", "a.pptx")
        self.assertEqual(p.returncode, 0)
        self.assertIn("Slide 1, paragraph 1", p.stdout)
        self.assertIn("Notes for slide 2", p.stdout)

    def test_json_report(self):
        (self.root / "a.md").write_text("Hello there friend\n")
        (self.root / "e.json").write_text(json.dumps({"edits": [{"id": "e", "file": "a.md", "before": "Hello", "after": "Hi"}]}))
        self.assertEqual(json.loads(self.call("e.json", "--json").stdout)[0]["status"], "applied")


class ScannerFormats(Base):
    def test_scanner_reads_word_powerpoint_html_and_notebooks_with_where_labels(self):
        make_docx(self.root / "a.docx")
        make_pptx(self.root / "a.pptx")
        (self.root / "a.html").write_text("<p>This robust platform seamlessly empowers teams a lot.</p>")
        (self.root / "n.ipynb").write_text(json.dumps(NotebookEditing.NB, indent=1) + "\n")
        result = plan_scan.scan(self.root)
        paths = {f["path"]: f for f in result["scanned"]}
        self.assertEqual(sorted(paths), ["a.docx", "a.html", "a.pptx", "n.ipynb"])
        pptx = paths["a.pptx"]["findings"]
        self.assertTrue(any(f["where"].startswith("Slide 2") for f in pptx), pptx)
        self.assertTrue(all("unit" in f for f in pptx))
        self.assertTrue(paths["a.html"]["findings"][0]["where"].startswith("Text"))

    def test_uneditable_formats_are_listed_with_a_reason(self):
        (self.root / "a.pdf").write_bytes(b"%PDF")
        reasons = {s["path"]: s["reason"] for s in plan_scan.scan(self.root)["skipped"]}
        self.assertIn("edit the file it was made from", reasons["a.pdf"])

    def test_strings_are_opt_in(self):
        (self.root / "a.py").write_text('raise ValueError("Moreover, this robust tool seamlessly fails every single time")\n')
        quiet = plan_scan.scan(self.root, include_code=True)["scanned"][0]
        loud = plan_scan.scan(self.root, include_code=True, strings=True)["scanned"][0]
        self.assertEqual(quiet["counts"]["P1"] + quiet["counts"]["P0"], 0)
        self.assertGreater(loud["counts"]["P1"], 0)

    def test_where_in_findings_works_as_an_edit_target(self):
        make_pptx(self.root / "a.pptx")
        finding = [f for f in plan_scan.scan(self.root)["scanned"][0]["findings"] if "seamless" in f["snippet"]][0]
        s = self.status({"id": "e", "file": "a.pptx", "before": "seamless and robust", "after": "smooth", "where": finding["unit"]})
        self.assertEqual(s["e"], "applied")


class Docs(unittest.TestCase):
    def test_apply_edits_options_are_documented(self):
        help_text = subprocess.run([sys.executable, str(APPLY), "--help"], capture_output=True, text=True).stdout
        docs = (ROOT / "docs" / "restyle.md").read_text()
        for option in ("--dry-run", "--backup", "--allow-dirty", "--root", "--units", "--json"):
            with self.subTest(option):
                self.assertIn(option, help_text)
                self.assertIn(option, docs)

    def test_commands_and_reference_use_the_editor(self):
        for rel in ("commands/apply.md", "docs/personal-commands/restyle-apply.md", "skills/jed-writing-style/references/plan.md"):
            with self.subTest(rel):
                self.assertIn("apply_edits.py", (ROOT / rel).read_text())

    def test_docs_list_every_supported_format(self):
        docs = (ROOT / "docs" / "restyle.md").read_text()
        for suffix in sorted(formats.SUPPORTED):
            with self.subTest(suffix):
                self.assertIn(suffix, docs)


if __name__ == "__main__":
    unittest.main()
