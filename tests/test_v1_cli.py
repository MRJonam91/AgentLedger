# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StableCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.db = self.directory / "ledger.sqlite3"

    def cli(self, *args, prompt=None):
        return subprocess.run([sys.executable, "-m", "agentledger", "--db", str(self.db), *args],
            input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=15,
            env=dict(os.environ, OPENAI_API_KEY=""), cwd=ROOT)

    def test_init_empty_and_existing_are_non_destructive(self):
        initialized = self.cli("init")
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        state = json.loads(initialized.stdout)
        self.assertEqual(state["event_count"], 0)
        self.assertTrue(state["initialized"])
        self.cli("demo")
        before = self.db.read_bytes()
        existing = self.cli("init")
        self.assertEqual(existing.returncode, 0, existing.stderr)
        self.assertEqual(json.loads(existing.stdout)["event_count"], 3)
        self.assertEqual(self.db.read_bytes(), before)

    def test_init_rejects_corrupt_existing_ledger_without_changes(self):
        self.cli("demo")
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("DROP TRIGGER events_no_update")
            conn.execute("UPDATE events SET data='{}'")
            from agentledger.storage import TRIGGER_SQL
            conn.execute(TRIGGER_SQL["update"])
        before = self.db.read_bytes()
        result = self.cli("init")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "chain_invalid")
        self.assertEqual(self.db.read_bytes(), before)

    def test_init_does_not_initialize_existing_empty_or_foreign_files(self):
        for contents in (b"", b"not a SQLite database"):
            self.db.write_bytes(contents)
            result = self.cli("init")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(self.db.read_bytes(), contents)
        self.db.unlink()
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("PRAGMA user_version=0")
        before = self.db.read_bytes()
        result = self.cli("init")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "unsupported_schema")
        self.assertEqual(self.db.read_bytes(), before)

    def test_report_exports_filtered_summary_and_markdown(self):
        self.cli("demo")
        output = self.directory / "report.json"
        result = self.cli("report", "--source", "demo", "--summary", "--output", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertTrue(receipt["saved"])
        self.assertNotIn("events", report)
        self.assertEqual(report["sources"]["demo"]["calculated_usd"], "0.0057")
        self.assertEqual(receipt["checkpoint"], report["checkpoint"])
        self.assertNotIn(str(self.directory), result.stdout)
        markdown = self.directory / "report.md"
        result = self.cli("report", "--format", "markdown", "--output", str(markdown))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0.0057", markdown.read_text(encoding="utf-8"))

    def test_report_never_overwrites_existing_output_or_ledger(self):
        self.cli("demo")
        output = self.directory / "existing.json"
        output.write_bytes(b"preserve exactly")
        for path in (output, self.db):
            before = path.read_bytes()
            result = self.cli("report", "--output", str(path))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)["error"], "output_exists")
            self.assertEqual(path.read_bytes(), before)

    def test_bad_request_does_not_create_ledger(self):
        for args, prompt in [(("--model", "demo-model"), "  "),
                             (("--model", "PRIVATE MODEL"), "synthetic"),
                             (("--model", "demo-model", "--max-output-tokens", "0"), "synthetic")]:
            result = self.cli("run", *args, prompt=prompt)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(self.db.exists())
            self.assertNotIn("PRIVATE MODEL", result.stderr)


if __name__ == "__main__":
    unittest.main()
