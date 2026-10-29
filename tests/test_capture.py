#!/usr/bin/env python3
"""Tests for scripts/capture.py: the snapshot hook, pairing with git, and the report.

Every test uses a temporary data folder and temporary git repos, never ~/.claude/signature.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "jed-writing-style"
SCRIPT = SKILL / "scripts" / "capture.py"
sys.path.insert(0, str(SKILL / "scripts"))
os.environ.setdefault("SIGNATURE_PROFILE", "jed")  # a private profile on this machine must not change results

import capture  # noqa: E402

DAY = 86400
CLAUDE = ("We leverage a robust pipeline — it is truly seamless. The team ran it on Tuesday.\n\n"
          "Setup takes ten minutes. Run the installer, then sign in.\n")
JED = ("The pipeline is quick to run. The team ran it on Tuesday.\n\n"
       "Setup takes ten minutes. Run the installer, then sign in.\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (capture.DATA, capture.CONFIG, capture.DRAFTS, capture.EDITS)
        capture.DATA = self.tmp / "data"
        capture.CONFIG, capture.DRAFTS, capture.EDITS = (capture.DATA / "capture.json", capture.DATA / "drafts",
                                                         capture.DATA / "edits.jsonl")
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "T")
        (self.repo / "seed.txt").write_text("seed\n")
        self.commit("seed", when=time.time() - 30 * DAY)

    def tearDown(self):
        capture.DATA, capture.CONFIG, capture.DRAFTS, capture.EDITS = self.saved

    def git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True, check=True,
                              env=dict(os.environ, **(env or {}))).stdout

    def commit(self, message, when):
        stamp = "@%d +0000" % int(when)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message, env={"GIT_COMMITTER_DATE": stamp, "GIT_AUTHOR_DATE": stamp})

    def enable(self, **extra):
        capture.save_private(capture.CONFIG, json.dumps(dict(capture.DEFAULTS, enabled=True, **extra)))

    def write(self, name, text, when, session="s1"):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return capture.snapshot({"tool_name": "Write", "session_id": session,
                                 "tool_input": {"file_path": str(path), "content": text}}, now=when)


class Snapshot(Base):
    def test_off_by_default(self):
        self.assertIsNone(self.write("README.md", CLAUDE, time.time()))
        self.assertFalse(capture.DRAFTS.exists())

    def test_write_saves_claudes_version_privately(self):
        self.enable()
        d = self.write("docs/guide.md", CLAUDE, time.time())
        self.assertEqual((d["rel"], d["written"]), ("docs/guide.md", [CLAUDE]))
        saved = next(capture.DRAFTS.glob("*.json"))
        self.assertEqual(oct(saved.stat().st_mode & 0o777), "0o600")

    def test_skips_what_is_not_the_writers_prose(self):
        self.enable(exclude=["*/clients/*"])
        (self.repo / ".signatureignore").write_text("drafts/\n")
        for name in ("app.py", "CLAUDE.md", "clients/acme.md", "drafts/x.md"):
            with self.subTest(name):
                self.assertIsNone(self.write(name, CLAUDE, time.time()))

    def test_edits_in_one_session_are_one_draft(self):
        self.enable()
        now = time.time()
        self.write("a.md", JED, now - 100, session="s0")
        path = self.repo / "a.md"
        path.write_text(JED.replace("quick to run", "quick to run, and cheap"))
        payload = {"tool_name": "Edit", "session_id": "s1",
                   "tool_input": {"file_path": str(path), "old_string": "quick to run", "new_string": "quick to run, and cheap"}}
        capture.snapshot(payload, now=now)
        capture.snapshot(dict(payload, tool_input=dict(payload["tool_input"], new_string="ten minutes")), now=now + 5)
        drafts = sorted(capture.DRAFTS.glob("*.json"))
        self.assertEqual(len(drafts), 2)  # the s0 draft is kept apart, to be paired on its own
        current = [capture.read_json(p) for p in drafts if "-" not in p.stem][0]
        self.assertEqual(current["written"], ["quick to run, and cheap", "ten minutes"])

    def test_hook_never_fails(self):
        env = dict(os.environ, SIGNATURE_HOME=str(self.tmp / "data"))
        for stdin in ("not json", "{}", json.dumps({"tool_name": "Write", "tool_input": {"file_path": "/nope.md"}})):
            started = time.time()
            p = subprocess.run([sys.executable, str(SCRIPT), "snapshot"], input=stdin, capture_output=True, text=True, env=env)
            self.assertEqual((p.returncode, p.stdout, p.stderr), (0, "", ""))
            self.assertLess(time.time() - started, 2)


class Pair(Base):
    def test_kept_as_written(self):
        self.enable()
        now = time.time()
        self.write("README.md", CLAUDE, now - 2 * DAY)
        self.commit("Add readme\n\nCo-Authored-By: Claude <noreply@anthropic.com>", now - 2 * DAY + 60)
        self.assertEqual(capture.pair(now=now), (1, 0, 0))
        r = list(capture.load_records().values())[0]
        self.assertEqual((r["kept"], r["edited"], r["cut"], r["edit_ratio"], r["claude_commit"], r["status"]),
                         (2, 0, 0, 0.0, True, "open"))

    def test_edited_by_the_writer(self):
        self.enable()
        now = time.time()
        self.write("README.md", CLAUDE, now - 3 * DAY)
        (self.repo / "README.md").write_text(JED)
        self.commit("Tidy readme", now - 2 * DAY)
        capture.pair(now=now)
        r = list(capture.load_records().values())[0]
        self.assertEqual((r["kept"], r["edited"]), (1, 1))
        self.assertGreater(r["edit_ratio"], 0)
        self.assertEqual(r["passages"][0]["after"], "The pipeline is quick to run. The team ran it on Tuesday.")
        self.assertEqual(r["tells_before"].get("dash"), 1)
        self.assertNotIn("dash", r["tells_after"])

    def test_only_claudes_passages_count(self):
        self.enable()
        now = time.time()
        (self.repo / "notes.md").write_text(JED)
        self.commit("Jed's notes", now - 5 * DAY)
        path = self.repo / "notes.md"
        path.write_text(JED + "\nA new closing line that Claude added here.\n")
        capture.snapshot({"tool_name": "Edit", "session_id": "s1", "tool_input": {
            "file_path": str(path), "old_string": "sign in.", "new_string": "sign in.\n\nA new closing line that Claude added here."}},
            now=now - 4 * DAY)
        path.write_text(JED.replace("quick to run", "fast") + "\nA new closing line that Claude added here.\n")
        self.commit("Edit my own paragraph only", now - 3 * DAY)
        capture.pair(now=now)
        r = list(capture.load_records().values())[0]
        self.assertEqual((r["kept"], r["edited"], r["outside"], r["edit_ratio"]), (1, 0, 1, 0.0))

    def test_waiting_then_closed(self):
        self.enable()
        now = time.time()
        self.write("README.md", CLAUDE, now - 2 * DAY)
        self.assertEqual(capture.pair(now=now), (0, 1, 0))
        self.assertEqual(capture.pair(now=now + 20 * DAY), (0, 1, 1))
        self.assertFalse(list(capture.DRAFTS.glob("*.json")))
        self.assertEqual(capture.load_records(), {})

    def test_commit_after_the_window_does_not_count(self):
        self.enable()
        now = time.time()
        self.write("README.md", CLAUDE, now - 30 * DAY)
        (self.repo / "README.md").write_text(JED)
        self.commit("much later", now - 10 * DAY)
        self.assertEqual(capture.pair(now=now), (0, 1, 1))

    def test_numbers_only_keeps_no_text(self):
        self.enable(numbers_only=True)
        now = time.time()
        self.write("README.md", CLAUDE, now - 3 * DAY)
        (self.repo / "README.md").write_text(JED)
        self.commit("Tidy", now - 2 * DAY)
        capture.pair(now=now)
        text = capture.EDITS.read_text()
        self.assertNotIn("pipeline", text)
        self.assertIn('"edited": 1', text)

    def test_old_pairs_are_dropped(self):
        self.enable()
        now = time.time()
        self.write("README.md", CLAUDE, now - 3 * DAY)
        (self.repo / "README.md").write_text(JED)
        self.commit("Tidy", now - 2 * DAY)
        capture.pair(now=now)
        capture.pair(now=now + 100 * DAY)
        self.assertEqual(capture.load_records(), {})


class Report(Base):
    def test_report_names_what_the_writer_removes(self):
        self.enable()
        now = time.time()
        self.write("README.md", CLAUDE, now - 3 * DAY)
        (self.repo / "README.md").write_text(JED)
        self.commit("Tidy", now - 2 * DAY)
        capture.pair(now=now)
        s = capture.summarise(list(capture.load_records().values()))
        self.assertEqual(s["drafts"], 1)
        self.assertIn(("dash", 1), s["tells_removed"])
        self.assertIn("leverage", dict(s["words_removed"]))

    def test_cli_round_trip(self):
        env = dict(os.environ, SIGNATURE_HOME=str(self.tmp / "cli"))
        run = lambda *a: subprocess.run([sys.executable, str(SCRIPT), *a], capture_output=True, text=True, env=env, cwd=self.repo)
        self.assertIn("Capture is off", run("status").stdout)
        self.assertIn("Capture is on", run("enable", "--exclude", "*/clients/*").stdout)
        self.assertIn("*/clients/*", run("status").stdout)
        self.assertEqual(run("pair", "--quiet").stdout, "")
        self.assertIn("No paired drafts yet", run("report").stdout)
        self.assertIn("Capture is off", run("disable").stdout)


class InstallCapture(unittest.TestCase):
    """--capture adds our two hooks to settings.json, keeps everything else, and --uninstall takes them out."""

    def run_install(self, home, *args):
        env = dict(os.environ, CLAUDE_HOME=str(home), CODEX_HOME=str(home / "codex"))
        return subprocess.run(["bash", str(ROOT / "install.sh"), *args], capture_output=True, text=True, env=env)

    def test_add_twice_then_remove(self):
        home = Path(tempfile.mkdtemp())
        mine = {"model": "opus", "hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo hi"}]}]}}
        (home / "settings.json").write_text(json.dumps(mine))
        self.assertEqual(self.run_install(home, "--capture").returncode, 2)  # the skill must be installed first
        self.assertEqual(self.run_install(home, "--claude").returncode, 0)
        before = (home / "settings.json").read_text()
        self.assertIn("would: add", self.run_install(home, "--capture", "--dry-run").stdout)
        self.assertEqual((home / "settings.json").read_text(), before)
        for _ in range(2):
            self.assertEqual(self.run_install(home, "--capture").returncode, 0)
        data = json.loads((home / "settings.json").read_text())
        commands = [h["command"] for g in data["hooks"]["PostToolUse"] + data["hooks"]["SessionStart"] for h in g["hooks"]]
        self.assertEqual(data["model"], "opus")
        self.assertIn("echo hi", commands)
        self.assertEqual(sum("capture.py" in c for c in commands), 2)
        self.assertTrue((home / "settings.json.signature-backup").exists())
        self.assertEqual(self.run_install(home, "--uninstall").returncode, 0)
        self.assertEqual(json.loads((home / "settings.json").read_text()), mine)


class Wiring(unittest.TestCase):
    def test_plugin_hooks_point_at_real_scripts(self):
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())["hooks"]
        post = hooks["PostToolUse"][0]
        self.assertEqual(post["matcher"], "Write|Edit|MultiEdit")
        self.assertIn("capture.py\" snapshot", post["hooks"][0]["command"])
        starts = [h["command"] for h in hooks["SessionStart"][0]["hooks"]]
        self.assertTrue(any("capture.py\" pair --quiet" in c for c in starts))
        for command in [post["hooks"][0]["command"]] + starts:
            script = command.split('"')[1].replace("${CLAUDE_PLUGIN_ROOT}", str(ROOT))
            self.assertTrue(Path(script).exists(), script)


if __name__ == "__main__":
    unittest.main()
