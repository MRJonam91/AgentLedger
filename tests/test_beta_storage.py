# SPDX-License-Identifier: GPL-3.0-or-later
import json
import sqlite3
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from agentledger.storage import GENESIS, Ledger, TRIGGER_SQL


def entry(key):
    return {"run_id": "run-test", "kind": "test", "data": {"count": 1}, "external_key": key}


class BetaStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.sqlite3"
        self.ledger = Ledger(self.path, create=True)

    def test_batch_verifies_history_once_and_chains_every_event(self):
        self.ledger.append("test", "test", {})
        with patch.object(self.ledger, "_verified", wraps=self.ledger._verified) as verified:
            result = self.ledger.append_many([entry(str(i)) for i in range(100)])
            self.assertEqual(verified.call_count, 1)
        self.assertEqual([e["seq"] for e in result], list(range(2, 102)))
        self.assertEqual(self.ledger.verify()["event_count"], 101)

    def test_batch_duplicate_rolls_back_all_new_events(self):
        self.ledger.append_many([entry("old")])
        before = self.ledger.read()
        for entries in [[entry("new"), entry("old")], [entry("same"), entry("same")]]:
            with self.assertRaisesRegex(ValueError, "duplicate_response"):
                self.ledger.append_many(entries)
            self.assertEqual(self.ledger.read(), before)

    def test_concurrent_batches_are_atomic(self):
        def collect(_):
            try:
                Ledger(self.path).append_many([entry("one"), entry("two")])
                return 1
            except ValueError:
                return 0
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sum(pool.map(collect, range(4))), 1)
        self.assertEqual(self.ledger.verify()["event_count"], 2)

    def test_prefix_checkpoint_survives_valid_appends(self):
        self.ledger.append_many([entry("one")])
        state = self.ledger.verify()
        anchor = {"schema_version": 1, "event_count": 1, "checkpoint": state["checkpoint"]}
        self.ledger.append_many([entry("two")])
        self.assertEqual(self.ledger.verify(checkpoint=anchor)["event_count"], 2)
        with self.assertRaisesRegex(ValueError, "checkpoint_mismatch"):
            self.ledger.verify(expected_head=anchor["checkpoint"])

    def test_truncated_checkpoint_and_bad_shapes_rejected(self):
        self.ledger.append_many([entry("one"), entry("two")])
        state = self.ledger.verify()
        anchor = {"schema_version": 1, "event_count": 2, "checkpoint": state["checkpoint"]}
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("DROP TRIGGER events_no_delete")
            conn.execute("DELETE FROM events WHERE seq=2")
            conn.execute(TRIGGER_SQL["delete"])
        with self.assertRaisesRegex(ValueError, "checkpoint_mismatch"):
            self.ledger.verify(checkpoint=anchor)
        for changed in [{"event_count": True}, {"checkpoint": "bad"}, {"schema_version": 2},
                        {"event_count": -1}, {"extra": "not allowed"}]:
            with self.assertRaises(ValueError):
                self.ledger.verify(checkpoint={**anchor, **changed})

    def test_zero_checkpoint_requires_genesis(self):
        anchor = {"schema_version": 1, "event_count": 0, "checkpoint": GENESIS}
        self.assertTrue(self.ledger.verify(checkpoint=anchor)["verified"])
        with self.assertRaisesRegex(ValueError, "checkpoint_mismatch"):
            self.ledger.verify(checkpoint={**anchor, "checkpoint": "1" * 64})

    def test_backup_is_verified_snapshot_and_preserves_existing_file(self):
        self.ledger.append_many([entry("one"), entry("two")])
        destination = Path(self.temp.name) / "backup.sqlite3"
        result = self.ledger.backup(destination)
        self.assertTrue(result["backed_up"])
        self.assertEqual(Ledger(destination).read(), self.ledger.read())
        before = destination.read_bytes()
        with self.assertRaisesRegex(ValueError, "output_exists"):
            self.ledger.backup(destination)
        with self.assertRaises(ValueError):
            self.ledger.backup(self.path)
        self.assertEqual(destination.read_bytes(), before)
        self.ledger.append_many([entry("three")])
        self.assertEqual(Ledger(destination).verify()["event_count"], 2)

    def test_failed_backup_removes_only_own_partial_file(self):
        destination = Path(self.temp.name) / "partial.sqlite3"
        with patch.object(Ledger, "verify", side_effect=ValueError("verification_failed")):
            with self.assertRaises(ValueError):
                self.ledger.backup(destination)
        self.assertFalse(destination.exists())

    def test_read_connection_is_read_only(self):
        with self.ledger._connection() as conn:
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("INSERT INTO events VALUES(1,'x','x','x','{}',NULL,'x','x')")

    def test_actual_alpha_hashes_and_schema_are_preserved(self):
        root = Path(__file__).resolve().parents[1]
        try:
            old = subprocess.run(["git", "show", "v0.1.0-alpha.1:agentledger/storage.py"],
                                 cwd=root, capture_output=True, text=True, encoding="utf-8")
        except FileNotFoundError:
            self.skipTest("Git unavailable; frozen alpha fixture still verifies compatibility")
        if old.returncode:
            self.skipTest("Alpha Git tag unavailable in source archive")
        namespace = {"__name__": "agentledger.alpha_compat", "__package__": "agentledger"}
        exec(compile(old.stdout, "alpha_storage_fixture", "exec"), namespace)
        path = Path(self.temp.name) / "alpha.sqlite3"
        alpha = namespace["Ledger"](path, create=True)
        alpha.append("alpha-run", "test", {"counter": 2})
        original = alpha.read()
        current = Ledger(path)
        self.assertEqual(current.read(), original)
        current.append_many([entry("new")])
        self.assertEqual(alpha.read(), current.read())

    def test_frozen_alpha_fixture_works_without_git_history(self):
        fixture = Path(__file__).parent / "fixtures" / "alpha_v1.json"
        value = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertEqual(value["source_tag"], "v0.1.0-alpha.1")
        with self.ledger._connection(write=True) as conn:
            for event in value["events"]:
                conn.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?,?)",
                    (event["seq"], event["at"], event["run_id"], event["kind"],
                     json.dumps(event["data"], sort_keys=True, separators=(",", ":")),
                     event["external_key"], event["prev_hash"], event["hash"]))
        self.assertEqual(self.ledger.read(), value["events"])
        self.ledger.append_many([entry("beta-after-alpha")])
        self.assertEqual(self.ledger.read()[:len(value["events"])], value["events"])


if __name__ == "__main__":
    unittest.main()
