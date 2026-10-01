#!/usr/bin/env python3
"""Tests for scripts/ai_check.py. Plain unittest, no dependencies.

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "jed-writing-style"
SCRIPT = SKILL / "scripts" / "ai_check.py"
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(SKILL / "scripts"))

import ai_check  # noqa: E402


def run(text, register="general", suffix=""):
    return ai_check.analyse(text, register, suffix)


def labels(result):
    return {f["label"] for f in result["findings"]}


class HumanSamplesAreClean(unittest.TestCase):
    """Writing Jed approved must not be flagged, or the checker is too noisy to trust."""

    CASES = [
        ("human/linkedin_hr.txt", "post"),
        ("human/team_message.txt", "message"),
        ("human/customer_answer.md", "customer"),
        ("human/script_clean.md", "script"),
        ("human/code_clean.py", "code"),
    ]

    def test_clean(self):
        for name, register in self.CASES:
            path = FIXTURES / name
            with self.subTest(name):
                result = run(path.read_text(), register, path.suffix)
                self.assertEqual(result["verdict"], "clean", result["findings"])
                self.assertEqual(result["dashes"], 0)


class AiSamplesAreFlagged(unittest.TestCase):
    CASES = [
        ("ai/marketing_post.txt", "post"),
        ("ai/customer_ai.md", "customer"),
        ("ai/script_ai.md", "script"),
        ("ai/code_ai.py", "code"),
    ]

    def test_flagged(self):
        for name, register in self.CASES:
            path = FIXTURES / name
            with self.subTest(name):
                result = run(path.read_text(), register, path.suffix)
                self.assertEqual(result["verdict"], "reads AI, fix before sending", result["score"])

    def test_marketing_post_finds_the_big_ones(self):
        r = run((FIXTURES / "ai/marketing_post.txt").read_text(), "post")
        self.assertTrue({"dash", "banned word", "challenge-outlook closer"} <= labels(r))

    def test_customer_finds_open_loop_and_preamble(self):
        r = run((FIXTURES / "ai/customer_ai.md").read_text(), "customer")
        self.assertTrue({"counted preamble", "open loop", "chatbot residue", "discovery voice",
                         "copula avoidance", "semicolon", "vague authority"} <= labels(r))


class IndividualRules(unittest.TestCase):
    def test_all_dash_kinds(self):
        for text in ("It works — mostly.", "It works – mostly.", "It works - mostly.",
                     "It works -- mostly.", "It works--mostly."):
            with self.subTest(text):
                self.assertIn("dash", labels(run(text)))

    def test_hyphenated_compound_is_fine(self):
        self.assertNotIn("dash", labels(run("This is a follow-up for non-technical readers.")))

    def test_semicolon(self):
        self.assertIn("semicolon", labels(run("It works; it is fast.")))

    def test_comma_heavy_sentence_but_not_a_list(self):
        chained = "We built the app, which the team liked, and so we shipped it, and then we waited."
        listed = "The repo needs naming, comment density, idiom, formatter."
        self.assertIn("comma-heavy sentence", labels(run(chained)))
        self.assertNotIn("comma-heavy sentence", labels(run(listed)))

    def test_exclamation_by_register(self):
        text = "Great result. It works!"
        self.assertIn("exclamation", labels(run(text, "customer")))
        self.assertIn("exclamation", labels(run(text, "doc")))
        self.assertNotIn("exclamation", labels(run(text, "post")))
        self.assertNotIn("exclamation", labels(run(text, "message")))

    def test_ing_rider_and_copula(self):
        r = run("The tool serves as a hub, highlighting its importance.")
        self.assertTrue({"copula avoidance", "-ing rider"} <= labels(r))

    def test_one_not_x_but_y_is_allowed_and_not_penalised(self):
        r = run("The barrier isn't access, it's trust. Plain and short. We moved on.")
        self.assertTrue(r["not_x_allowed"])

    def test_tiers(self):
        r = run("It works — mostly. The tool serves as a hub.")
        tiers = {f["label"]: f["tier"] for f in r["findings"]}
        self.assertEqual(tiers["dash"], "P0")
        self.assertEqual(tiers["copula avoidance"], "P1")

    def test_open_loop_only_in_customer_docs(self):
        text = "We will come back to you once we have more."
        self.assertIn("open loop", labels(run(text, "customer")))
        self.assertNotIn("open loop", labels(run(text, "message")))

    def test_script_unspeakable(self):
        r = run("Use LLMs (large models), e.g. GPT & friends and/or others.", "script")
        self.assertIn("unspeakable", labels(r))

    def test_script_wants_short_sentences(self):
        long_line = ("This is a very long spoken sentence that keeps on going without any pause at all so that "
                     "nobody could possibly say it in a single breath without running out of air. ") * 3
        self.assertTrue(run(long_line, "script")["rhythm"])

    def test_emoji_flagged_except_in_posts(self):
        self.assertIn("emoji", labels(run("Nice work \U0001F680", "doc")))
        self.assertNotIn("emoji", labels(run("Nice work \U0001F680", "post")))

    def test_curly_quotes(self):
        self.assertIn("curly quotes", labels(run("He said “hello”.")))


class IgnoreMarkers(unittest.TestCase):
    def test_block_marker(self):
        text = ("Plain and short.\n<!-- signature:ignore-start -->\nIt works — robustly.\n"
                "<!-- signature:ignore-end -->\nAll good.")
        self.assertEqual(run(text)["dashes"], 0)

    def test_line_marker(self):
        text = "Plain and short.\nIt is robust. <!-- signature:ignore-line -->\nAll good."
        self.assertEqual(run(text)["banned_words"], 0)

    def test_line_numbers_survive_markup(self):
        text = "# Title\n\n```\ncode\n```\n\nIt works — mostly.\n"
        r = run(text)
        self.assertEqual([f["line"] for f in r["findings"] if f["label"] == "dash"], [7])


class CodeMode(unittest.TestCase):
    def test_only_comments_are_read(self):
        src = 'name = "robust seamless"\n# plain comment about corr\n'
        self.assertEqual(run(src, "code", ".py")["banned_words"], 0)

    def test_comment_findings_have_real_line_numbers(self):
        src = "x = 1\ny = 2\n# This function is used to add\n"
        found = [f for f in run(src, "code", ".py")["findings"] if f["label"] == "narrating comment"]
        self.assertEqual(found[0]["line"], 3)

    def test_docstring_is_read(self):
        src = 'def f():\n    """Robust and seamless."""\n    return 1\n'
        self.assertGreater(run(src, "code", ".py")["banned_words"], 0)

    def test_url_hash_is_not_a_comment(self):
        src = 'url = "http://x.com/a#robust"\n'
        self.assertEqual(run(src, "code", ".py")["banned_words"], 0)


class OfficeFiles(unittest.TestCase):
    def make_zip(self, name, members):
        d = tempfile.mkdtemp()
        path = Path(d) / name
        with zipfile.ZipFile(path, "w") as z:
            for member, body in members.items():
                z.writestr(member, body)
        return path

    def test_pptx_wordy_line(self):
        wordy = " ".join(["word"] * 40)
        xml = "<a:p><a:t>Short headline</a:t></a:p><a:p><a:t>%s</a:t></a:p>" % wordy
        path = self.make_zip("deck.pptx", {"ppt/slides/slide1.xml": xml})
        r = run(ai_check.read_text(str(path)), "slides", ".pptx")
        self.assertIn("wordy slide text", labels(r))

    def test_docx_text_is_read(self):
        xml = "<w:p><w:t>It is robust.</w:t></w:p>"
        path = self.make_zip("a.docx", {"word/document.xml": xml})
        r = run(ai_check.read_text(str(path)), "doc", ".docx")
        self.assertEqual(r["banned_words"], 1)


class CommandLine(unittest.TestCase):
    def call(self, *args, stdin=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin, capture_output=True, text=True)

    def test_exit_code_clean(self):
        p = self.call(str(FIXTURES / "human/linkedin_hr.txt"), "--register", "post", "--quiet")
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("AI check: clean", p.stdout)

    def test_exit_code_dirty(self):
        p = self.call(str(FIXTURES / "ai/marketing_post.txt"), "--register", "post", "--quiet")
        self.assertEqual(p.returncode, 1)

    def test_missing_file_is_friendly(self):
        p = self.call("no-such-file.md")
        self.assertEqual(p.returncode, 2)
        self.assertIn("cannot read", p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_stdin(self):
        p = self.call("-", "--register", "doc", "--quiet", stdin="It is plain. It is short.")
        self.assertEqual(p.returncode, 0)

    def test_json(self):
        p = self.call(str(FIXTURES / "ai/customer_ai.md"), "--register", "customer", "--json")
        data = json.loads(p.stdout)
        self.assertEqual(data["register"], "customer")
        self.assertTrue(data["findings"])
        self.assertIn("tier", data["findings"][0])

    def test_source_file_defaults_to_code(self):
        p = self.call(str(FIXTURES / "human/code_clean.py"), "--quiet")
        self.assertIn("[code]", p.stdout)

    def test_list_registers(self):
        p = self.call("--list-registers")
        for name in ("code", "doc", "customer", "course", "slides", "script", "post", "message", "general"):
            self.assertIn(name, p.stdout)


class DocsPracticeWhatTheyPreach(unittest.TestCase):
    """The skill's own files must pass the checker, like the repo it learned from does."""

    def test_docs(self):
        files = [ROOT / "README.md", ROOT / "CHANGELOG.md", SKILL / "SKILL.md"] + sorted((SKILL / "references").glob("*.md"))
        for path in files:
            register = "post" if path.name == "posts-and-messages.md" else "doc"
            with self.subTest(path.name):
                r = run(path.read_text(), register, ".md")
                self.assertNotEqual(r["verdict"], "reads AI, fix before sending", r["findings"])
                self.assertEqual(r["dashes"], 0, r["findings"])


class SkillShape(unittest.TestCase):
    """Rules from Anthropic's skill authoring guide."""

    def test_frontmatter(self):
        text = (SKILL / "SKILL.md").read_text()
        head = text.split("---")[1]
        name = [l for l in head.splitlines() if l.startswith("name:")][0].split(":", 1)[1].strip()
        desc = [l for l in head.splitlines() if l.startswith("description:")][0].split(":", 1)[1].strip()
        self.assertRegex(name, r"^[a-z0-9-]{1,64}$")
        self.assertNotIn("claude", name)
        self.assertLessEqual(len(desc), 1024)
        self.assertNotRegex(desc, r"\b(I|you|your)\b")

    def test_skill_md_is_short(self):
        self.assertLess(len((SKILL / "SKILL.md").read_text().splitlines()), 500)

    def test_every_reference_is_linked_from_skill_md(self):
        body = (SKILL / "SKILL.md").read_text()
        for ref in (SKILL / "references").glob("*.md"):
            with self.subTest(ref.name):
                self.assertIn("references/" + ref.name, body)

    def test_long_references_have_contents(self):
        for ref in (SKILL / "references").glob("*.md"):
            text = ref.read_text()
            if len(text.splitlines()) > 100:
                with self.subTest(ref.name):
                    self.assertIn("## Contents", text)

    def test_references_are_one_level_deep(self):
        for ref in (SKILL / "references").glob("*.md"):
            with self.subTest(ref.name):
                self.assertNotRegex(ref.read_text(), r"\]\((?:\./)?references/|\]\([a-z-]+\.md\)")

    def test_manifest_json(self):
        for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "hooks/hooks.json",
                    "evals/evals.json"):
            with self.subTest(rel):
                json.loads((ROOT / rel).read_text())


if __name__ == "__main__":
    unittest.main()
