# SPDX-License-Identifier: GPL-3.0-or-later
"""SQLite persistence with transactional SHA-256 chaining and checkpoints."""

import json
import os
import re
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .domain import canonical, counter, digest, exact_keys
from .jsonio import create_output

GENESIS = "0" * 64
TABLE_SQL = """CREATE TABLE events (
    seq INTEGER PRIMARY KEY, at TEXT NOT NULL, run_id TEXT NOT NULL,
    kind TEXT NOT NULL, data TEXT NOT NULL, external_key TEXT UNIQUE,
    prev_hash TEXT NOT NULL, hash TEXT NOT NULL)"""
TRIGGER_SQL = {name: f"""CREATE TRIGGER events_no_{name} BEFORE {name.upper()} ON events
    BEGIN SELECT RAISE(ABORT, 'append_only'); END""" for name in ("update", "delete")}


def check_schema(conn):
    if conn.execute("PRAGMA user_version").fetchone()[0] != 1:
        raise ValueError("unsupported_schema")
    expected = {"events": TABLE_SQL, **{"events_no_" + k: v for k, v in TRIGGER_SQL.items()}}
    actual = {row["name"]: row["sql"] for row in conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE name NOT GLOB 'sqlite_*'")}
    compact = lambda mapping: {k: " ".join(v.split()).casefold() for k, v in mapping.items()}
    if any(not isinstance(v, str) for v in actual.values()) or compact(actual) != compact(expected):
        raise ValueError("unsupported_schema")


class Ledger:
    def __init__(self, path, create=False):
        self.path = Path(path).resolve()
        if not create and not self.path.is_file():
            raise ValueError("ledger_missing")
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection(create=create) as conn:
            conn.execute("BEGIN IMMEDIATE" if create else "BEGIN")
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if create and version == 0:
                if conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone():
                    raise ValueError("unsupported_schema")
                conn.execute(TABLE_SQL)
                for sql in TRIGGER_SQL.values():
                    conn.execute(sql)
                conn.execute("PRAGMA user_version=1")
            elif version != 1:
                raise ValueError("unsupported_schema")
            check_schema(conn)

    @contextmanager
    def _connection(self, create=False, write=False):
        mode = "rwc" if create else "rw" if write else "ro"
        conn = sqlite3.connect(self.path.as_uri() + "?mode=" + mode, uri=True, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _verified(self, conn):
        check_schema(conn)
        previous = GENESIS
        for index, row in enumerate(conn.execute("SELECT * FROM events ORDER BY seq"), 1):
            try:
                event = dict(row)
                event["data"] = json.loads(event["data"])
                event["schema_version"] = 1
                claimed = event.pop("hash")
                if event["seq"] != index or event["prev_hash"] != previous or digest(event) != claimed:
                    raise ValueError("chain_invalid")
                event["hash"] = claimed
                previous = claimed
                yield event
            except (TypeError, json.JSONDecodeError):
                raise ValueError("chain_invalid") from None

    def read(self, expected_head=None):
        if expected_head is not None and not re.fullmatch(r"[a-f0-9]{64}", expected_head):
            raise ValueError("invalid_checkpoint")
        with self._connection() as conn:
            conn.execute("BEGIN")
            events = list(self._verified(conn))
            head = events[-1]["hash"] if events else GENESIS
            if expected_head is not None and expected_head != head:
                raise ValueError("checkpoint_mismatch")
            return events

    def append(self, run_id, kind, data, external_key=None):
        return self.append_many([{"run_id": run_id, "kind": kind, "data": data,
                                  "external_key": external_key}])[0]

    def append_many(self, entries):
        if not isinstance(entries, list) or not 1 <= len(entries) <= 1000:
            raise ValueError("invalid_batch")
        with self._connection(write=True) as conn:
            conn.execute("BEGIN IMMEDIATE")
            state = self._scan(conn)
            previous, seq = state["checkpoint"], state["event_count"]
            appended = []
            for item in entries:
                exact_keys(item, {"run_id", "kind", "data", "external_key"})
                seq += 1
                event = {"schema_version": 1, "seq": seq,
                         "at": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
                         **item, "prev_hash": previous}
                hashed = digest(event)
                try:
                    inserted = conn.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (seq, event["at"], item["run_id"], item["kind"], canonical(item["data"]),
                         item["external_key"], previous, hashed))
                    if inserted.rowcount != 1:
                        raise ValueError("append_not_persisted")
                except sqlite3.IntegrityError:
                    raise ValueError("duplicate_response") from None
                appended.append({**event, "hash": hashed})
                previous = hashed
            return appended

    def _scan(self, conn, expected_head=None, checkpoint=None):
        if expected_head is not None and (not isinstance(expected_head, str)
                or not re.fullmatch(r"[a-f0-9]{64}", expected_head)):
            raise ValueError("invalid_checkpoint")
        if checkpoint is not None:
            exact_keys(checkpoint, {"schema_version", "event_count", "checkpoint"})
            if type(checkpoint["schema_version"]) is not int or checkpoint["schema_version"] != 1:
                raise ValueError("invalid_checkpoint")
            counter(checkpoint["event_count"], maximum=2**63-1)
            if not isinstance(checkpoint["checkpoint"], str) or not re.fullmatch(r"[a-f0-9]{64}", checkpoint["checkpoint"]):
                raise ValueError("invalid_checkpoint")
        head, count = GENESIS, 0
        anchored = checkpoint is None or (checkpoint["event_count"] == 0 and checkpoint["checkpoint"] == GENESIS)
        for event in self._verified(conn):
            head, count = event["hash"], event["seq"]
            if checkpoint is not None and count == checkpoint["event_count"]:
                anchored = head == checkpoint["checkpoint"]
        if not anchored or (expected_head is not None and head != expected_head):
            raise ValueError("checkpoint_mismatch")
        return {"verified": True, "event_count": count, "checkpoint": head}

    def verify(self, expected_head=None, checkpoint=None):
        with self._connection() as conn:
            conn.execute("BEGIN")
            return self._scan(conn, expected_head, checkpoint)

    def backup(self, destination):
        destination = Path(destination).absolute()
        if destination.resolve() == self.path:
            raise ValueError("output_exists")
        created = False
        try:
            with self._connection() as source:
                source.execute("BEGIN")
                state = self._scan(source)
                fd = create_output(destination)
                os.close(fd)
                created = True
                with closing(sqlite3.connect(destination)) as target:
                    source.backup(target)
            copied = Ledger(destination).verify(expected_head=state["checkpoint"])
            if copied["event_count"] != state["event_count"]:
                raise ValueError("checkpoint_mismatch")
            return {"backed_up": True, **copied}
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise
