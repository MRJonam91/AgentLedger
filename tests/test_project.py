# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts import check_project
from scripts.check_project import scan_text


class PublicationScanTests(unittest.TestCase):
    def test_distribution_paths_are_explicit(self):
        for name in ("README.md", "docs/ARCHITECTURE.md", "agentledger/cli.py", "tests/fixtures/alpha_v1.json"):
            self.assertTrue(check_project.public_path(name))
        for name in ("data.json", "private/data.json", "docs/private/data.md", "docs/_internal/data.md", ".local/data.json"):
            self.assertFalse(check_project.public_path(name))

    def test_credentials_and_private_metadata_are_flagged_without_echo(self):
        self.assertIn("credential_pattern", scan_text("sk-" + "a" * 32))
        self.assertIn("credential_pattern", scan_text("ghp_" + "x" * 32))
        self.assertIn("personal_email", scan_text("person" + "@private-domain.invalid"))
        self.assertIn("personal_windows_path", scan_text("C:" + "/Users/private-name/file"))

    def test_public_identity_and_examples_are_allowed(self):
        self.assertEqual(scan_text("1+public@users.noreply.github.com secret@example.org"), [])

    def test_source_archive_checks_files_despite_parent_git_checkout(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "source.py"
            source.write_text("# synthetic source", encoding="utf-8")
            private = root / ".agentledger"
            private.mkdir()
            (private / "ledger.sqlite3").write_bytes(b"not for publication")
            with patch.object(check_project, "ROOT", root):
                self.assertEqual(check_project.public_files(), [source])


if __name__ == "__main__":
    unittest.main()
