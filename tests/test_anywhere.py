#!/usr/bin/env python3
"""Tests for the pieces that make Signature work in any session: verify_office.py, plan_scan --find,
the slide growth note, install.sh, and the docs that describe them. Standard library only.

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "jed-writing-style"
VERIFY = SKILL / "scripts" / "verify_office.py"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import apply_edits  # noqa: E402
import plan_scan  # noqa: E402
import verify_office  # noqa: E402
from test_edits import make_docx, make_pptx, build_zip, DOCUMENT, W  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, True)

    def copy_original(self, path):
        original = self.root / ("orig_" + path.name)
        shutil.copy(path, original)
        return original

    def edit(self, *edits):
        return {r["id"]: r for r in apply_edits.run({"edits": list(edits)}, root=self.root, allow_dirty=True)}

    def statuses(self, result):
        return {c["check"]: c["status"] for c in result["checks"]}


class VerifyIntegrity(Base):
    def test_a_good_file_passes(self):
        make_docx(self.root / "a.docx")
        r = verify_office.verify(str(self.root / "a.docx"))
        self.assertTrue(r["ok"])
        self.assertEqual(self.statuses(r)["intact"], "pass")

    def test_not_a_zip_fails(self):
        (self.root / "a.docx").write_bytes(b"not a zip")
        r = verify_office.verify(str(self.root / "a.docx"))
        self.assertFalse(r["ok"])
        self.assertIn("not a valid zip", r["checks"][0]["detail"])

    def test_broken_xml_fails(self):
        build_zip(self.root / "a.docx", {"[Content_Types].xml": "<Types/>", "word/document.xml": "<w:document><w:p></w:document>"})
        r = verify_office.verify(str(self.root / "a.docx"))
        self.assertFalse(r["ok"])
        self.assertIn("does not parse", r["checks"][0]["detail"])

    def test_missing_content_types_fails(self):
        build_zip(self.root / "a.docx", {"word/document.xml": DOCUMENT})
        self.assertFalse(verify_office.verify(str(self.root / "a.docx"))["ok"])

    def test_a_link_to_a_missing_part_warns(self):
        build_zip(self.root / "a.docx", {"[Content_Types].xml": "<Types/>", "word/document.xml": DOCUMENT,
                                         "word/_rels/document.xml.rels": '<Relationships><Relationship Id="r1" Target="media/gone.png"/></Relationships>'})
        r = verify_office.verify(str(self.root / "a.docx"))
        self.assertTrue(r["ok"])
        self.assertEqual(self.statuses(r)["intact"], "warn")

    def test_external_links_are_not_checked(self):
        build_zip(self.root / "a.docx", {"[Content_Types].xml": "<Types/>", "word/document.xml": DOCUMENT,
                                         "word/_rels/document.xml.rels": '<Relationships><Relationship Id="r1" TargetMode="External" Target="https://x.com"/></Relationships>'})
        self.assertEqual(self.statuses(verify_office.verify(str(self.root / "a.docx")))["intact"], "pass")

    def test_only_docx_and_pptx_are_accepted(self):
        (self.root / "a.md").write_text("hi")
        with self.assertRaises(ValueError):
            verify_office.verify(str(self.root / "a.md"))


class VerifyOpens(Base):
    """A library refusing a file only counts as a failure if it opened the original."""

    def setUp(self):
        super().setUp()
        make_docx(self.root / "a.docx")
        self.original = self.copy_original(self.root / "a.docx")
        saved = verify_office.check_opens
        self.addCleanup(setattr, verify_office, "check_opens", saved)

    def fake(self, opens_original):
        def opens(path):
            ok = opens_original if Path(path).name.startswith("orig_") else False
            return verify_office.check("opens", "pass" if ok else "fail", "ok" if ok else "boom")
        verify_office.check_opens = opens

    def opens(self, original):
        r = verify_office.verify(str(self.root / "a.docx"), str(original) if original else None)
        return [c for c in r["checks"] if c["check"] == "opens"][0], r

    def test_original_opens_but_the_edit_does_not_is_a_failure(self):
        self.fake(opens_original=True)
        c, r = self.opens(self.original)
        self.assertEqual(c["status"], "fail")
        self.assertIn("edit broke it", c["detail"])
        self.assertFalse(r["ok"])

    def test_neither_opens_is_only_a_warning(self):
        self.fake(opens_original=False)
        c, r = self.opens(self.original)
        self.assertEqual(c["status"], "warn")
        self.assertTrue(r["ok"])

    def test_with_nothing_to_compare_it_is_only_a_warning(self):
        self.fake(opens_original=False)
        c, r = self.opens(None)
        self.assertEqual(c["status"], "warn")
        self.assertIn("no original", c["detail"])


class VerifyComparison(Base):
    def setUp(self):
        super().setUp()
        self.path = self.root / "a.docx"
        make_docx(self.path)
        self.original = self.copy_original(self.path)

    def verify(self):
        return verify_office.verify(str(self.path), str(self.original))

    def test_an_edit_made_by_the_editor_passes_and_is_listed(self):
        self.edit({"id": "e", "file": "a.docx", "before": "Plain closing line", "after": "Plain final line"})
        r = self.verify()
        self.assertTrue(r["ok"])
        s = self.statuses(r)
        self.assertEqual((s["text only"], s["paragraphs"], s["changes"]), ("pass", "pass", "pass"))
        self.assertEqual(r["changes"][0]["before"], "Plain closing line")
        self.assertEqual(r["changes"][0]["after"], "Plain final line")

    def test_a_change_that_is_not_only_text_fails(self):
        with zipfile.ZipFile(self.original) as z:
            members = {i.filename: z.read(i.filename) for i in z.infolist()}
        members["word/document.xml"] = members["word/document.xml"].replace(b"<w:b/>", b"<w:i/>")
        build_zip(self.path, members)
        r = self.verify()
        self.assertFalse(r["ok"])
        self.assertEqual(self.statuses(r)["text only"], "fail")

    def test_a_lost_paragraph_fails(self):
        with zipfile.ZipFile(self.original) as z:
            members = {i.filename: z.read(i.filename) for i in z.infolist()}
        xml = members["word/document.xml"].decode()
        members["word/document.xml"] = xml.replace("<w:p><w:r><w:t>Plain closing line</w:t></w:r></w:p>", "").encode()
        build_zip(self.path, members)
        r = self.verify()
        self.assertFalse(r["ok"])
        self.assertEqual(self.statuses(r)["paragraphs"], "fail")

    def test_a_changed_list_of_parts_fails(self):
        with zipfile.ZipFile(self.original) as z:
            members = {i.filename: z.read(i.filename) for i in z.infolist()}
        members["word/extra.xml"] = b"<x/>"
        build_zip(self.path, members)
        self.assertEqual(self.statuses(self.verify())["text only"], "fail")

    def test_nothing_changed_is_reported_as_nothing(self):
        r = self.verify()
        self.assertIn("nothing changed", [c["detail"] for c in r["checks"] if c["check"] == "text only"][0])


class VerifyGrowth(Base):
    def test_slide_text_that_grows_a_lot_warns_and_names_the_slide(self):
        path = self.root / "a.pptx"
        make_pptx(path)
        original = self.copy_original(path)
        self.edit({"id": "e", "file": "a.pptx", "before": "seamless and robust", "after": "seamless and robust and also very much longer than before"})
        r = verify_office.verify(str(path), str(original))
        self.assertTrue(r["ok"])
        growth = [c for c in r["checks"] if c["check"] == "growth"][0]
        self.assertEqual(growth["status"], "warn")
        self.assertIn("Slide 2", growth["detail"])

    def test_shorter_text_does_not_warn(self):
        path = self.root / "a.pptx"
        make_pptx(path)
        original = self.copy_original(path)
        self.edit({"id": "e", "file": "a.pptx", "before": "seamless and robust", "after": "plain"})
        growth = [c for c in verify_office.verify(str(path), str(original))["checks"] if c["check"] == "growth"][0]
        self.assertEqual(growth["status"], "pass")

    def test_the_editor_itself_notes_growth(self):
        path = self.root / "a.pptx"
        make_pptx(path)
        r = self.edit({"id": "e", "file": "a.pptx", "before": "seamless and robust", "after": "seamless and robust and a good deal longer"})["e"]
        self.assertEqual(r["status"], "applied")
        self.assertIn("grew", r["detail"])


class VerifyRender(Base):
    STUB = """#!/bin/sh
while [ $# -gt 0 ]; do case "$1" in --outdir) out="$2"; shift;; --convert-to) shift;; --headless) ;; *) f="$1";; esac; shift; done
base=$(basename "$f"); stem="${base%.*}"
case "$base" in orig_*) pages=2;; *) pages=${STUB_PAGES:-3};; esac
{ echo "%PDF-1.4"; i=0; while [ $i -lt $pages ]; do echo "<< /Type /Page >>"; i=$((i+1)); done; echo "<< /Type /Pages >>"; } > "$out/$stem.pdf"
"""

    def setUp(self):
        super().setUp()
        self.path = self.root / "a.pptx"
        make_pptx(self.path)
        self.original = self.copy_original(self.path)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        old = os.environ.get("PATH", "")
        self.addCleanup(os.environ.__setitem__, "PATH", old)

    def test_no_libreoffice_is_a_skip_with_advice(self):
        os.environ["PATH"] = str(self.bin)
        r = verify_office.verify(str(self.path), str(self.original), str(self.root / "out"))
        render = [c for c in r["checks"] if c["check"] == "render"][0]
        self.assertEqual(render["status"], "skip")
        self.assertIn("Open the file in Word or PowerPoint", render["detail"])
        self.assertTrue(r["ok"])

    def test_a_changed_page_count_warns(self):
        stub = self.bin / "soffice"
        stub.write_text(self.STUB)
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        os.environ["PATH"] = str(self.bin) + os.pathsep + "/usr/bin" + os.pathsep + "/bin"
        r = verify_office.verify(str(self.path), str(self.original), str(self.root / "out"))
        render = [c for c in r["checks"] if c["check"] == "render"][0]
        self.assertEqual(render["status"], "warn")
        self.assertIn("from 2 to 3", render["detail"])

    def test_the_same_page_count_passes(self):
        stub = self.bin / "soffice"
        stub.write_text(self.STUB.replace("pages=${STUB_PAGES:-3}", "pages=2"))
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        os.environ["PATH"] = str(self.bin) + os.pathsep + "/usr/bin" + os.pathsep + "/bin"
        r = verify_office.verify(str(self.path), str(self.original), str(self.root / "out"))
        self.assertEqual([c for c in r["checks"] if c["check"] == "render"][0]["status"], "pass")


class VerifyCommandLine(Base):
    def call(self, *args):
        return subprocess.run([sys.executable, str(VERIFY), *args], cwd=self.root, capture_output=True, text=True)

    def test_exit_codes(self):
        make_docx(self.root / "a.docx")
        (self.root / "bad.docx").write_bytes(b"nope")
        self.assertEqual(self.call("a.docx").returncode, 0)
        self.assertEqual(self.call("bad.docx").returncode, 1)
        self.assertEqual(self.call("missing.docx").returncode, 2)
        self.assertEqual(self.call("a.docx", "--against", "missing.docx").returncode, 2)

    def test_report_ends_with_what_a_person_should_still_do(self):
        make_docx(self.root / "a.docx")
        out = self.call("a.docx").stdout
        self.assertIn("A person should still", out)
        self.assertIn("Review, Compare", out)

    def test_json(self):
        make_docx(self.root / "a.docx")
        data = json.loads(self.call("a.docx", "--json").stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["checks"][0]["check"], "intact")

    @unittest.skipUnless(shutil.which("git"), "git is not installed")
    def test_git_compares_with_the_last_commit(self):
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=self.root, check=True, capture_output=True)
        git("init", "-q")
        make_docx(self.root / "a.docx")
        git("add", "-A")
        git("commit", "-q", "-m", "x")
        apply_edits.run({"edits": [{"id": "e", "file": "a.docx", "before": "Plain closing", "after": "Plain final"}]}, root=self.root, allow_dirty=True)
        out = self.call("a.docx", "--git").stdout
        self.assertIn("1 paragraph changed", out)
        self.assertIn("Plain final line", out)

    def test_both_against_and_git_is_an_error(self):
        make_docx(self.root / "a.docx")
        self.assertEqual(self.call("a.docx", "--git", "--against", "a.docx").returncode, 2)


class Find(Base):
    def setUp(self):
        super().setUp()
        make_docx(self.root / "a.docx")
        make_pptx(self.root / "a.pptx")
        (self.root / "a.md").write_text("Acme builds things.\nAcme again, and ACME once more.\n")
        (self.root / "page.html").write_text("<p>Welcome to Acme Tracker today</p><script>var a = 'Acme in a script here ok';</script>")
        (self.root / "sample_data").mkdir()
        (self.root / "sample_data" / "x.txt").write_text("Acme in sample data")

    def find(self, text, **kw):
        import re
        flags = re.I if kw.pop("ignore_case", False) else 0
        pattern = re.compile(text if kw.pop("regex", False) else re.escape(text), flags)
        return plan_scan.find(self.root, pattern, **kw)

    def test_finds_across_every_format_with_where_and_unit(self):
        r = self.find("Plain closing")
        self.assertEqual([f["path"] for f in r["files"]], ["a.docx"])
        self.assertEqual(r["files"][0]["matches"][0]["where"], "Paragraph 4")
        self.assertEqual(r["files"][0]["matches"][0]["unit"], 4)

    def test_pptx_notes_and_slides(self):
        r = self.find("second slide")
        self.assertEqual(r["files"][0]["matches"][0]["where"], "Notes for slide 2, paragraph 1")

    def test_text_files_report_lines(self):
        r = self.find("Acme", ignore_case=True)
        md = [f for f in r["files"] if f["path"] == "a.md"][0]
        self.assertEqual((md["count"], [m["unit"] for m in md["matches"]]), (3, [1, 2, 2]))

    def test_case_sensitive_by_default(self):
        md = [f for f in self.find("Acme")["files"] if f["path"] == "a.md"][0]
        self.assertEqual(md["count"], 2)

    def test_html_scripts_and_sample_data_are_left_out(self):
        r = self.find("Acme")
        self.assertEqual([f["path"] for f in r["files"] if f["path"] == "page.html"], ["page.html"])
        self.assertEqual(next(f for f in r["files"] if f["path"] == "page.html")["count"], 1)
        self.assertNotIn("sample_data/x.txt", [f["path"] for f in r["files"]])
        self.assertIn("sample_data/x.txt", [f["path"] for f in self.find("Acme", keep_all=True)["files"]])

    def test_regex(self):
        r = self.find(r"Ac\w+", regex=True)
        self.assertGreater(r["total"], 0)

    def test_results_work_as_edit_targets(self):
        match = self.find("Plain closing")["files"][0]["matches"][0]
        out = self.edit({"id": "e", "file": "a.docx", "before": "Plain closing", "after": "Plain final", "where": match["unit"]})
        self.assertEqual(out["e"]["status"], "applied")

    def test_command_line_exit_codes(self):
        call = lambda *a: subprocess.run([sys.executable, str(SKILL / "scripts" / "plan_scan.py"), *a], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(call("--find", "Plain closing").returncode, 0)
        self.assertEqual(call("--find", "nothing like this anywhere").returncode, 1)
        p = call("--find", "(", "--regex")
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)
        self.assertEqual(json.loads(call("--find", "Plain closing", "--json").stdout)["total"], 1)


@unittest.skipUnless(shutil.which("bash"), "bash is not installed")
class Installer(Base):
    def setUp(self):
        super().setUp()
        self.claude, self.codex = self.root / "claude", self.root / "codex"
        self.env = dict(os.environ, CLAUDE_HOME=str(self.claude), CODEX_HOME=str(self.codex))

    def run_install(self, *args):
        return subprocess.run(["bash", str(ROOT / "install.sh"), *args], env=self.env, capture_output=True, text=True)

    def test_no_arguments_prints_usage_and_changes_nothing(self):
        p = self.run_install()
        self.assertEqual(p.returncode, 0)
        self.assertIn("./install.sh --all", p.stdout)
        self.assertFalse(self.claude.exists())

    def test_dry_run_changes_nothing(self):
        p = self.run_install("--all", "--dry-run")
        self.assertIn("would:", p.stdout)
        self.assertFalse(self.claude.exists() or self.codex.exists())

    def test_claude_install_copies_the_skill_and_commands(self):
        self.assertEqual(self.run_install("--claude").returncode, 0)
        self.assertTrue((self.claude / "skills/jed-writing-style/SKILL.md").exists())
        self.assertTrue((self.claude / "skills/jed-writing-style/scripts/apply_edits.py").exists())
        self.assertEqual(sorted(p.name for p in (self.claude / "commands").iterdir()), ["restyle-apply.md", "restyle-verify.md", "restyle.md"])
        self.assertFalse(list((self.claude / "skills").rglob("__pycache__")))

    def test_codex_install(self):
        self.run_install("--codex")
        self.assertTrue((self.codex / "skills/jed-writing-style/SKILL.md").exists())

    def test_the_note_is_added_once_and_keeps_existing_text(self):
        self.claude.mkdir()
        (self.claude / "CLAUDE.md").write_text("# My notes\nKeep this line.\n")
        self.run_install("--global-note")
        self.run_install("--global-note")
        text = (self.claude / "CLAUDE.md").read_text()
        self.assertEqual(text.count("signature:start"), 1)
        self.assertTrue(text.startswith("# My notes\nKeep this line.\n"))
        self.assertIn("apply_edits.py", text)
        self.assertIn("git clone --depth 1 https://github.com/jedlwk/Signature", text)

    def test_a_project_gets_claude_md_and_agents_md_only_if_it_has_one(self):
        project = self.root / "proj"
        project.mkdir()
        self.run_install("--project", str(project))
        self.assertTrue((project / "CLAUDE.md").exists())
        self.assertFalse((project / "AGENTS.md").exists())
        (project / "AGENTS.md").write_text("existing\n")
        self.run_install("--project", str(project))
        self.assertIn("signature:start", (project / "AGENTS.md").read_text())

    def test_uninstall_removes_only_what_it_installed(self):
        self.claude.mkdir()
        (self.claude / "CLAUDE.md").write_text("# My notes\n")
        self.run_install("--all")
        (self.claude / "commands" / "mine.md").write_text("my own command")
        self.run_install("--uninstall")
        self.assertFalse((self.claude / "skills/jed-writing-style").exists())
        self.assertFalse((self.codex / "skills/jed-writing-style").exists())
        self.assertEqual(sorted(p.name for p in (self.claude / "commands").iterdir()), ["mine.md"])
        self.assertEqual((self.claude / "CLAUDE.md").read_text().strip(), "# My notes")

    def test_a_different_skill_with_the_same_name_is_left_alone(self):
        other = self.claude / "skills" / "jed-writing-style"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_text("name: someone-elses\n")
        p = self.run_install("--claude")
        self.assertEqual(p.returncode, 1)
        self.assertIn("Leaving it alone", p.stderr)
        self.assertEqual((other / "SKILL.md").read_text(), "name: someone-elses\n")

    def test_unknown_option_is_a_clear_error(self):
        p = self.run_install("--nope")
        self.assertEqual(p.returncode, 2)
        self.assertIn("unknown option", p.stderr)


class Docs(unittest.TestCase):
    def read(self, rel):
        return (ROOT / rel).read_text()

    def test_every_installer_option_is_documented(self):
        docs = self.read("docs/anywhere.md")
        for option in ("--all", "--claude", "--codex", "--project", "--uninstall", "--dry-run"):
            with self.subTest(option):
                self.assertIn(option, docs)
                self.assertIn(option, self.read("install.sh"))

    def test_the_playbook_covers_every_rung_and_the_report(self):
        text = self.read("skills/jed-writing-style/references/office.md")
        for needle in ("A shell and Python 3", "python-docx", "LibreOffice", "Computer use", "No shell, no files",
                       "Never save a Word or PowerPoint file with python-docx", "verify_office.py", "Replace with",
                       "Looked at:", "Please check:", "Undo:"):
            with self.subTest(needle):
                self.assertIn(needle, text)

    def test_the_plan_reference_points_at_the_playbook_and_lists_purposes(self):
        text = self.read("skills/jed-writing-style/references/plan.md")
        self.assertIn("references/office.md", text)
        self.assertIn("verify_office.py", text)
        for purpose in ("Rename a term", "Update a fact", "Remove a name", "Tighten"):
            self.assertIn(purpose, text)

    def test_the_plan_reference_covers_a_session_that_cannot_run_the_scripts(self):
        text = self.read("skills/jed-writing-style/references/plan.md")
        self.assertIn("## If the scripts can't run", text)
        self.assertIn("Don't pretend the scanner ran", text)
        self.assertIn("never markup", text)  # a Before text is words, not tags

    def test_the_bootstrap_prompt_says_the_scripts_are_mine_and_admits_the_limit(self):
        docs = self.read("docs/anywhere.md")
        self.assertIn("I wrote it, and you may run its scripts", docs)
        self.assertIn("refuse to run code they have just downloaded", docs)
        self.assertIn("./install.sh --all", docs)

    def test_verify_command_exists_in_both_forms(self):
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style/scripts/verify_office.py", self.read("commands/verify.md"))
        self.assertIn("~/.claude/skills/jed-writing-style/scripts/verify_office.py", self.read("docs/personal-commands/restyle-verify.md"))

    def test_readme_links_the_new_pages(self):
        readme = self.read("README.md")
        for rel in ("docs/anywhere.md", "docs/restyle.md"):
            self.assertIn(rel, readme)
        self.assertIn("install.sh", readme)

    def test_the_bootstrap_prompt_names_real_paths(self):
        docs = self.read("docs/anywhere.md")
        for rel in ("skills/jed-writing-style/SKILL.md", "references/plan.md", "scripts/apply_edits.py", "scripts/verify_office.py", "references/office.md"):
            self.assertIn(rel.split("/")[-1], docs)
            self.assertTrue(list((ROOT / "skills" / "jed-writing-style").rglob(rel.split("/")[-1])), rel)

    def test_install_script_is_executable(self):
        self.assertTrue(os.access(ROOT / "install.sh", os.X_OK))


if __name__ == "__main__":
    unittest.main()
