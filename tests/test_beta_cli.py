# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_domain import response

ROOT = Path(__file__).resolve().parents[1]


class BetaCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.db = self.directory / "ledger.sqlite3"

    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "agentledger", "--db", str(self.db), *args],
                              capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
                              env=dict(os.environ, OPENAI_API_KEY=""), timeout=15)

    def test_atomic_import_filtered_summary_and_no_content(self):
        result = self.cli("import-jsonl", "examples/responses.jsonl", "--rates", "examples/rates.demo.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["imported"], 2)
        report = self.cli("report", "--source", "imported", "--model", "demo-model", "--summary")
        self.assertEqual(report.returncode, 0, report.stderr)
        data = json.loads(report.stdout)
        self.assertNotIn("events", data)
        self.assertEqual(data["selected_event_count"], 2)
        self.assertEqual(data["sources"]["imported"]["calculated_usd"], "0.0114")
        self.assertNotIn(b"EXAMPLE CONTENT", self.db.read_bytes())
        text = self.cli("report", "--summary", "--format", "markdown").stdout
        self.assertIn("Selected events: 2", text)

    def test_checkpoint_accepts_appends_backup_and_exact_head_remains_strict(self):
        self.assertEqual(self.cli("demo").returncode, 0)
        checkpoint = self.directory / "checkpoint.json"
        saved = self.cli("checkpoint", "--output", str(checkpoint))
        self.assertEqual(saved.returncode, 0, saved.stderr)
        anchor = json.loads(checkpoint.read_text())
        self.assertEqual(set(anchor), {"schema_version", "event_count", "checkpoint"})
        self.assertEqual(self.cli("demo").returncode, 0)
        checked = self.cli("verify", "--checkpoint", str(checkpoint))
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(checked.stdout)["event_count"], 6)
        self.assertEqual(self.cli("verify", "--expected-head", anchor["checkpoint"]).returncode, 2)
        backup = self.directory / "backup.sqlite3"
        copied = self.cli("backup", str(backup))
        self.assertEqual(copied.returncode, 0, copied.stderr)
        self.assertTrue(json.loads(copied.stdout)["backed_up"])
        self.assertEqual(json.loads(copied.stdout)["event_count"], 6)
        for command in [("backup", str(backup)), ("checkpoint", "--output", str(checkpoint))]:
            existing = backup.read_bytes(), checkpoint.read_bytes()
            denied = self.cli(*command)
            self.assertEqual(denied.returncode, 2)
            self.assertEqual(json.loads(denied.stderr)["error"], "output_exists")
            self.assertEqual((backup.read_bytes(), checkpoint.read_bytes()), existing)

    def test_invalid_import_does_not_create_database(self):
        path = self.directory / "bad.jsonl"
        path.write_text(json.dumps(response()) + '\n{"usage":null}', encoding="utf-8")
        result = self.cli("import-jsonl", str(path))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.db.exists())
        path.write_text('{"usage":null}', encoding="utf-8")
        result = self.cli("import-response", str(path))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.db.exists())

    def test_duplicate_batch_keeps_existing_history(self):
        self.cli("demo")
        before = json.loads(self.cli("report").stdout)
        path = self.directory / "duplicate.jsonl"
        path.write_text((json.dumps(response()) + "\n") * 2, encoding="utf-8")
        result = self.cli("import-jsonl", str(path))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "duplicate_response")
        self.assertEqual(json.loads(self.cli("report").stdout), before)

    def test_checkpoint_arguments_exclusive_and_bad_file_safe(self):
        self.cli("demo")
        checkpoint = self.directory / "private-person.json"
        checkpoint.write_text('{"secret":"PRIVATE"}', encoding="utf-8")
        result = self.cli("verify", "--checkpoint", str(checkpoint))
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("PRIVATE", result.stderr)
        self.assertNotIn("private-person", result.stderr)
        both = self.cli("verify", "--checkpoint", str(checkpoint), "--expected-head", "0" * 64)
        self.assertEqual(both.returncode, 2)
        self.assertEqual(json.loads(both.stderr)["error"], "invalid_arguments_use_help")


if __name__ == "__main__":
    unittest.main()
