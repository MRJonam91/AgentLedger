# SPDX-License-Identifier: GPL-3.0-or-later
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "ledger.sqlite3"

    def cli(self, *args, text=None):
        env = dict(os.environ, OPENAI_API_KEY="")
        return subprocess.run([sys.executable, "-m", "agentledger", "--db", str(self.db), *args],
                              input=text, capture_output=True, text=True, encoding="utf-8",
                              cwd=ROOT, env=env, timeout=10)

    def test_demo_report_verify_restart(self):
        result = self.cli("demo")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["sources"]["demo"]["calculated_usd"], "0.0057")
        self.assertEqual(data["decisions"], {"allowed": 1, "denied": 1})
        self.assertEqual(data, json.loads(self.cli("report").stdout))
        checked = self.cli("verify", "--expected-head", data["checkpoint"])
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(checked.stdout)["event_count"], 3)
        markdown = self.cli("report", "--format", "markdown")
        self.assertIn("0.0057", markdown.stdout)
        self.assertIn("demo", markdown.stdout)

    def test_import_duplicate_and_no_content(self):
        fixture = ROOT / "examples" / "response.json"
        rates = ROOT / "examples" / "rates.demo.json"
        imported = self.cli("import-response", str(fixture), "--rates", str(rates))
        self.assertEqual(imported.returncode, 0, imported.stderr)
        duplicate = self.cli("import-response", str(fixture))
        self.assertEqual(duplicate.returncode, 2)
        self.assertEqual(json.loads(duplicate.stderr)["error"], "duplicate_response")
        self.assertNotIn("EXAMPLE CONTENT", self.cli("report").stdout)

    def test_missing_database_read_does_not_create(self):
        result = self.cli("report")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "ledger_missing")
        self.assertFalse(self.db.exists())

    def test_live_default_deny_without_key_or_network(self):
        result = self.cli("run", "--model", "demo-model", text="PRIVATE PROMPT")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "denied")
        self.assertNotIn("PRIVATE", self.cli("report").stdout)

    def test_invalid_file_safe_error(self):
        path = Path(self.temp.name) / "private-person.json"
        path.write_text('{"secret": "EXAMPLE CONTENT"', encoding="utf-8")
        result = self.cli("import-response", str(path))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "invalid_json")
        self.assertNotIn("private-person", result.stderr)
        self.assertNotIn("EXAMPLE CONTENT", result.stderr)

    def test_wrong_checkpoint_fails(self):
        self.cli("demo")
        checked = self.cli("verify", "--expected-head", "1" * 64)
        self.assertEqual(checked.returncode, 2)
        self.assertEqual(json.loads(checked.stderr)["error"], "checkpoint_mismatch")

    def test_argument_error_is_json_and_does_not_echo_input(self):
        result = self.cli("run", "--model", "demo-model", "--max-output-tokens", "PRIVATE VALUE")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "invalid_arguments_use_help")
        self.assertNotIn("PRIVATE VALUE", result.stderr)

    def test_invalid_prompt_and_oversize_json_rejected(self):
        result = self.cli("run", "--model", "demo-model", text=" " * 65537)
        self.assertEqual(result.returncode, 2)
        large = Path(self.temp.name) / "large.json"
        large.write_bytes(b" " * (2 * 1024 * 1024 + 1))
        self.assertEqual(self.cli("import-response", str(large)).returncode, 2)


if __name__ == "__main__":
    unittest.main()
