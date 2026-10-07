#!/usr/bin/env python3
"""Tests for the plan-first restyle: scripts/plan_scan.py and the commands around it.

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "jed-writing-style"
SCRIPT = SKILL / "scripts" / "plan_scan.py"
sys.path.insert(0, str(SKILL / "scripts"))

import plan_scan  # noqa: E402

AI_TEXT = ("I am thrilled to share this robust platform — it seamlessly empowers teams. Moreover, it serves "
           "as a pivotal hub. " * 4)
CLEAN_TEXT = ("Plain and short. This is how the tool works. If it breaks, ask me first. Nothing else is needed "
              "to start. The setup takes a minute and the rest runs on its own.")


def make_project(with_git=False):
    root = Path(tempfile.mkdtemp())
    files = {
        "README.md": AI_TEXT,
        "docs/guide.md": CLEAN_TEXT,
        "CLAUDE.md": AI_TEXT,
        "LICENSE": AI_TEXT,
        "node_modules/pkg/readme.md": AI_TEXT,
        "sample_pack/cv.txt": AI_TEXT,
        "notes/meeting-transcript.txt": AI_TEXT,
        ".hidden/secret.md": AI_TEXT,
        "archive/old.md": AI_TEXT,
        "logs/big.txt": "word " * (plan_scan.MAX_WORDS + 10),
        "src/app.py": "# This function is used to add robust things\nx = 1\n",
        "image.png": "not prose",
    }
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    if with_git:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def snapshot(root):
    return {str(p): hashlib.md5(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.parts}


class Scanner(unittest.TestCase):
    def setUp(self):
        self.root = make_project()
        self.addCleanup(shutil.rmtree, self.root, True)

    def paths(self, result):
        return [f["path"] for f in result["scanned"]]

    def skipped(self, result):
        return {s["path"]: s["reason"] for s in result["skipped"]}

    def test_scans_prose_and_skips_the_rest(self):
        r = plan_scan.scan(self.root)
        self.assertEqual(sorted(self.paths(r)), ["README.md", "docs/guide.md"])

    def test_says_why_it_skipped_things(self):
        skipped = self.skipped(plan_scan.scan(self.root))
        self.assertIn("agent or tool file", skipped["CLAUDE.md"])
        self.assertIn("agent or tool file", skipped["LICENSE"])
        self.assertIn("probably not Jed's writing", skipped["sample_pack/cv.txt"])
        self.assertIn("probably not Jed's writing", skipped["notes/meeting-transcript.txt"])
        self.assertIn("probably not Jed's writing", skipped["archive/old.md"])
        self.assertIn("log or data dump", skipped["logs/big.txt"])

    def test_does_not_scan_its_own_plan_or_backups(self):
        (self.root / "STYLE_PLAN.md").write_text(AI_TEXT)
        (self.root / ".signature-backup" / "20261006").mkdir(parents=True)
        (self.root / ".signature-backup" / "20261006" / "README.md").write_text(AI_TEXT)
        r = plan_scan.scan(self.root, keep_all=True)
        self.assertNotIn("STYLE_PLAN.md", self.paths(r))
        self.assertFalse([p for p in self.paths(r) if "signature-backup" in p])

    def test_never_scans_dependency_or_hidden_folders(self):
        r = plan_scan.scan(self.root, keep_all=True)
        for path in self.paths(r):
            self.assertNotIn("node_modules", path)
            self.assertNotIn(".hidden", path)

    def test_worst_file_comes_first(self):
        r = plan_scan.scan(self.root)
        self.assertEqual(self.paths(r)[0], "README.md")
        self.assertGreater(r["scanned"][0]["counts"]["P0"], 0)
        self.assertEqual(r["scanned"][1]["verdict"], "clean")

    def test_all_includes_samples(self):
        r = plan_scan.scan(self.root, keep_all=True)
        self.assertIn("sample_pack/cv.txt", self.paths(r))

    def test_code_is_opt_in(self):
        self.assertNotIn("src/app.py", self.paths(plan_scan.scan(self.root)))
        r = plan_scan.scan(self.root, include_code=True)
        app = [f for f in r["scanned"] if f["path"] == "src/app.py"][0]
        self.assertEqual(app["register"], "code")

    def test_paths_limit_the_scan(self):
        self.assertEqual(self.paths(plan_scan.scan(self.root, ["docs"])), ["docs/guide.md"])

    def test_signatureignore_file(self):
        (self.root / ".signatureignore").write_text("# not mine\ndocs\n")
        self.assertEqual(self.paths(plan_scan.scan(self.root)), ["README.md"])

    def test_exclude_option(self):
        self.assertEqual(self.paths(plan_scan.scan(self.root, exclude=["README.md"])), ["docs/guide.md"])

    def test_registers_follow_the_file(self):
        (self.root / "launch-script.md").write_text(CLEAN_TEXT)
        (self.root / "deck.md").write_text(CLEAN_TEXT)
        (self.root / "customer-faq.md").write_text(CLEAN_TEXT)
        registers = {f["path"]: f["register"] for f in plan_scan.scan(self.root)["scanned"]}
        self.assertEqual(registers["launch-script.md"], "script")
        self.assertEqual(registers["deck.md"], "slides")
        self.assertEqual(registers["customer-faq.md"], "customer")
        self.assertEqual(registers["README.md"], "doc")

    def test_folder_summary(self):
        folders = plan_scan.scan(self.root)["folders"]
        self.assertEqual(folders["(top level)"]["files"], 1)
        self.assertEqual(folders["docs"]["P0"], 0)

    def test_findings_are_capped_and_exclude_p2(self):
        r = plan_scan.scan(self.root, max_findings=3)
        readme = [f for f in r["scanned"] if f["path"] == "README.md"][0]
        self.assertLessEqual(len(readme["findings"]), 3)
        self.assertNotIn("P2", {f["tier"] for f in readme["findings"]})

    def test_scanning_changes_nothing(self):
        before = snapshot(self.root)
        plan_scan.scan(self.root, include_code=True, keep_all=True)
        self.assertEqual(before, snapshot(self.root))


@unittest.skipUnless(shutil.which("git"), "git is not installed")
class GitMode(unittest.TestCase):
    def test_gitignore_is_respected(self):
        root = make_project(with_git=True)
        self.addCleanup(shutil.rmtree, root, True)
        (root / ".gitignore").write_text("docs/\n")
        paths = [f["path"] for f in plan_scan.scan(root)["scanned"]]
        self.assertEqual(paths, ["README.md"])


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.root = make_project()
        self.addCleanup(shutil.rmtree, self.root, True)

    def call(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root, capture_output=True, text=True)

    def test_table_output(self):
        p = self.call()
        self.assertEqual(p.returncode, 0)
        self.assertIn("By folder:", p.stdout)
        self.assertIn("README.md", p.stdout)

    def test_json_output(self):
        data = json.loads(self.call("--json").stdout)
        self.assertEqual(data["scanned"][0]["path"], "README.md")
        self.assertIn("folders", data)

    def test_bad_path_and_empty_scan_exit_2(self):
        self.assertEqual(self.call("nope.md").returncode, 2)
        empty = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, empty, True)
        p = subprocess.run([sys.executable, str(SCRIPT)], cwd=empty, capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)


class Wiring(unittest.TestCase):
    """The commands, the reference and the skill must agree with each other."""

    def test_plan_and_apply_commands(self):
        plan = (ROOT / "commands" / "plan.md").read_text()
        apply = (ROOT / "commands" / "apply.md").read_text()
        for text in (plan, apply):
            self.assertTrue(text.startswith("---\n"))
            self.assertIn("description:", text.split("---")[1])
            self.assertIn("references/plan.md", text)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style/scripts/plan_scan.py", plan)
        self.assertIn("STYLE_PLAN.md", plan)
        self.assertIn("Do not edit anything else", plan)
        self.assertIn("Never assume everything", apply)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style/scripts/ai_check.py", apply)

    def test_personal_commands_match_the_plugin_ones(self):
        for personal, plugin in (("restyle.md", "plan.md"), ("restyle-apply.md", "apply.md"), ("restyle-verify.md", "verify.md")):
            mine = (ROOT / "docs" / "personal-commands" / personal).read_text()
            theirs = (ROOT / "commands" / plugin).read_text()
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", mine)
            self.assertIn("~/.claude/skills/jed-writing-style/scripts/", mine)
            normal = lambda t: t.replace("${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style", "~/.claude/skills/jed-writing-style")
            for line in normal(theirs).splitlines():
                if line.startswith(("Load the jed-writing-style", "Plan mode", "Apply mode", "Verify mode", "Load the jed-writing-style skill (")):
                    continue
                self.assertIn(line.strip(), mine, line)

    def test_skill_knows_about_plan_mode(self):
        body = (SKILL / "SKILL.md").read_text()
        self.assertIn("references/plan.md", body)
        self.assertIn("STYLE_PLAN.md", body)
        self.assertIn("/signature:plan", body)

    def test_reference_has_the_hard_stop_and_the_template(self):
        text = (SKILL / "references" / "plan.md").read_text()
        for needle in ("Stage one is read-only", "Stop after writing the plan", "Nothing has been changed yet",
                       "## Needs your input", "## Not changing", "How to approve", "Never assume", "git status",
                       ".signature-backup"):
            with self.subTest(needle):
                self.assertIn(needle, text)

    def test_docs_pages_exist_and_link(self):
        self.assertTrue((ROOT / "docs" / "restyle.md").exists())
        self.assertIn("docs/restyle.md", (ROOT / "README.md").read_text())

    def test_every_documented_scanner_option_exists(self):
        help_text = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True).stdout
        for option in ("--code", "--exclude", "--all", "--top", "--max-findings", "--json"):
            with self.subTest(option):
                self.assertIn(option, help_text)
                self.assertIn(option, (ROOT / "docs" / "restyle.md").read_text())


if __name__ == "__main__":
    unittest.main()
