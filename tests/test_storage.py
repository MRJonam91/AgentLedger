# SPDX-License-Identifier: GPL-3.0-or-later
import sqlite3
from contextlib import closing
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agentledger.storage import Ledger, TRIGGER_SQL


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.sqlite3"

    def append(self, ledger, key=None):
        return ledger.append("run-test", "test", {"count": 1}, external_key=key)

    def test_read_does_not_create_missing_database(self):
        with self.assertRaises(ValueError):
            Ledger(self.path)
        self.assertFalse(self.path.exists())

    def test_persist_and_verify_hashes(self):
        ledger = Ledger(self.path, create=True)
        self.append(ledger)
        self.append(ledger)
        events = Ledger(self.path).read()
        self.assertEqual([e["seq"] for e in events], [1, 2])
        self.assertEqual(events[1]["prev_hash"], events[0]["hash"])
        self.assertEqual(len(events[0]["hash"]), 64)

    def test_duplicate_is_atomic(self):
        ledger = Ledger(self.path, create=True)
        self.append(ledger, "key")
        with self.assertRaises(ValueError):
            self.append(ledger, "key")
        self.assertEqual(len(ledger.read()), 1)
        self.append(ledger, "other-key")
        self.assertEqual(len(ledger.read()), 2)

    def test_concurrent_writers_chain_and_dedupe(self):
        ledger = Ledger(self.path, create=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda i: self.append(Ledger(self.path), str(i)), range(12)))
        self.assertEqual(len(ledger.read()), 12)
        def duplicate(_):
            try:
                self.append(Ledger(self.path), "same")
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sum(pool.map(duplicate, range(4))), 1)
        self.assertEqual(len(ledger.read()), 13)

    def test_accidental_update_delete_blocked(self):
        ledger = Ledger(self.path, create=True)
        self.append(ledger)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            for sql in ["DELETE FROM events", "UPDATE events SET kind='changed'"]:
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(sql)

    def test_tampering_detected_and_append_refused(self):
        ledger = Ledger(self.path, create=True)
        self.append(ledger)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("DROP TRIGGER events_no_update")
            conn.execute("UPDATE events SET data='{}'")
            conn.execute(TRIGGER_SQL["update"])
        with self.assertRaisesRegex(ValueError, "chain_invalid"):
            ledger.read()
        with self.assertRaises(ValueError):
            self.append(ledger)

    def test_external_checkpoint_detects_tail_deletion(self):
        ledger = Ledger(self.path, create=True)
        self.append(ledger)
        self.append(ledger)
        head = ledger.read()[-1]["hash"]
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("DROP TRIGGER events_no_delete")
            conn.execute("DELETE FROM events WHERE seq=2")
            conn.execute(TRIGGER_SQL["delete"])
        self.assertEqual(len(ledger.read()), 1)
        with self.assertRaises(ValueError):
            ledger.read(expected_head=head)

    def test_schema_mismatch_refused(self):
        Ledger(self.path, create=True)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("PRAGMA user_version=99")
        with self.assertRaises(ValueError):
            Ledger(self.path, create=True)

    def test_version_one_without_constraints_rejected(self):
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("""CREATE TABLE events (seq INTEGER PRIMARY KEY, at TEXT NOT NULL,
                run_id TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL,
                external_key TEXT, prev_hash TEXT NOT NULL, hash TEXT NOT NULL)""")
            conn.execute("PRAGMA user_version=1")
        with self.assertRaisesRegex(ValueError, "unsupported_schema"):
            Ledger(self.path)

    def test_schema_guards_rechecked_on_read_and_append(self):
        ledger = Ledger(self.path, create=True)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("DROP TRIGGER events_no_delete")
        with self.assertRaisesRegex(ValueError, "unsupported_schema"):
            ledger.read()
        with self.assertRaisesRegex(ValueError, "unsupported_schema"):
            self.append(ledger)

    def test_user_trigger_resembling_internal_prefix_is_rejected(self):
        ledger = Ledger(self.path, create=True)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("""CREATE TRIGGER sqlitex_ignore BEFORE INSERT ON events
                BEGIN SELECT RAISE(IGNORE); END""")
        with self.assertRaisesRegex(ValueError, "unsupported_schema"):
            self.append(ledger)


if __name__ == "__main__":
    unittest.main()
