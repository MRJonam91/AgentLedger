# SPDX-License-Identifier: GPL-3.0-or-later
"""SQLite persistence with transactional SHA-256 chaining and checkpoints."""

import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .domain import canonical, digest

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
    def _connection(self, create=False):
        mode = "rwc" if create else "rw"
        conn = sqlite3.connect(self.path.as_uri() + "?mode=" + mode, uri=True, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _verified(self, conn):
        check_schema(conn)
        events = []
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
                events.append(event)
                previous = claimed
            except (TypeError, json.JSONDecodeError):
                raise ValueError("chain_invalid") from None
        return events

    def read(self, expected_head=None):
        if expected_head is not None and not re.fullmatch(r"[a-f0-9]{64}", expected_head):
            raise ValueError("invalid_checkpoint")
        with self._connection() as conn:
            conn.execute("BEGIN")
            events = self._verified(conn)
            head = events[-1]["hash"] if events else GENESIS
            if expected_head is not None and expected_head != head:
                raise ValueError("checkpoint_mismatch")
            return events

    def append(self, run_id, kind, data, external_key=None):
        with self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            events = self._verified(conn)
            event = {"schema_version": 1, "seq": len(events) + 1,
                     "at": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
                     "run_id": run_id, "kind": kind, "data": data,
                     "external_key": external_key,
                     "prev_hash": events[-1]["hash"] if events else GENESIS}
            hashed = digest(event)
            try:
                inserted = conn.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                        (event["seq"], event["at"], run_id, kind, canonical(data),
                                         external_key, event["prev_hash"], hashed))
                if inserted.rowcount != 1:
                    raise ValueError("append_not_persisted")
            except sqlite3.IntegrityError:
                raise ValueError("duplicate_response") from None
            return {**event, "hash": hashed}
