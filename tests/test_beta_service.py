# SPDX-License-Identifier: GPL-3.0-or-later
import copy
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from agentledger.domain import Policy, RateCard, normalize_response
from agentledger.provider import request_response
from agentledger.service import Collector
from agentledger.storage import Ledger, TRIGGER_SQL
from test_domain import card, policy, response


class BetaServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.sqlite3"
        self.ledger = Ledger(self.path, create=True)
        self.collector = Collector(self.ledger)
        self.rates = RateCard.from_dict(card())

    def test_bulk_normalization_is_atomic_and_private(self):
        first, second = response(), response()
        second["id"] = "resp_fixture_2"
        result = self.collector.import_many([first, second], self.rates)
        self.assertEqual(result["imported"], 2)
        self.assertEqual(len(set(result["run_ids"])), 2)
        report = self.collector.report()
        self.assertEqual(report["sources"]["imported"]["calculated_usd"], "0.0114")
        self.assertNotIn("PRIVATE", json.dumps(report))
        self.assertNotIn(b"PRIVATE", self.path.read_bytes())

    def test_bad_final_record_and_duplicates_do_not_write(self):
        invalid = response()
        invalid["usage"] = None
        for records in [[response(), invalid], [response(), response()], [], "wrong"]:
            with self.subTest(records=str(records)[:10]), self.assertRaises(ValueError):
                self.collector.import_many(records)
            self.assertEqual(self.ledger.read(), [])

    def test_imported_data_cannot_claim_live_or_demo_source(self):
        for source in ["live", "demo", "unknown"]:
            with self.assertRaisesRegex(ValueError, "invalid_source"):
                self.collector.import_response(response(), source=source)
        self.assertEqual(self.ledger.read(), [])

    def test_default_policy_snapshot_roundtrips(self):
        denied = Policy.from_dict(None)
        loaded = Policy.from_dict(denied.snapshot())
        self.assertEqual(loaded.decide("demo-model", 512), "default_deny")

    def test_live_duplicate_is_terminal_unknown_not_pending(self):
        self.collector.import_response(response())
        result = self.collector.run("demo-model", "PRIVATE", 512, Policy.from_dict(policy()), "key",
                                    self.rates, transport=lambda *args: response())
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["reason"], "duplicate_response")
        report = self.collector.report()
        self.assertEqual(report["pending_runs"], 0)
        self.assertEqual(report["unknown_outcomes"], 1)
        self.assertEqual(report["sources"]["live"]["records"], 0)

    def test_source_run_and_model_filters_keep_whole_context(self):
        self.collector.demo()
        result = self.collector.run("demo-model", "PRIVATE", 512, Policy.from_dict(policy()), "key",
                                    self.rates, transport=lambda *args: response())
        selected = self.collector.report(source="live", run_id=result["run_id"], model="demo-model")
        self.assertEqual(selected["event_count"], 5)
        self.assertEqual(selected["selected_event_count"], 2)
        self.assertEqual(selected["decisions"], {"allowed": 1, "denied": 0})
        self.assertEqual({e["kind"] for e in selected["events"]}, {"decision", "usage"})
        summary = self.collector.report(source="live", summary=True)
        self.assertNotIn("events", summary)
        self.assertEqual(summary["checkpoint"], selected["checkpoint"])
        empty = self.collector.report(model="no-such-model")
        self.assertEqual(empty["selected_event_count"], 0)
        self.assertIsNone(empty["sources"]["live"]["calculated_usd"])

    def test_model_filter_uses_returned_model_and_retains_requested_decision(self):
        value = response()
        value["model"] = "snapshot-model"
        self.collector.run("demo-model", "PRIVATE", 512, Policy.from_dict(policy()), "key",
                           self.rates, transport=lambda *args: value)
        selected = self.collector.report(model="snapshot-model")
        self.assertEqual(selected["selected_event_count"], 2)
        self.assertEqual(selected["sources"]["live"]["unpriced"], 1)
        self.assertEqual(self.collector.report(model="demo-model")["selected_event_count"], 0)

    def test_pending_and_unknown_outcomes_are_filterable_by_requested_model(self):
        def interrupted(*args):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            self.collector.run("demo-model", "PRIVATE", 512, Policy.from_dict(policy()), "key",
                               transport=interrupted)
        self.assertEqual(self.collector.report(model="demo-model")["pending_runs"], 1)

    def test_hidden_corruption_still_fails_filtered_summary(self):
        self.collector.demo()
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("DROP TRIGGER events_no_update")
            conn.execute("UPDATE events SET data='{}' WHERE seq=1")
            conn.execute(TRIGGER_SQL["update"])
        with self.assertRaisesRegex(ValueError, "chain_invalid"):
            self.collector.report(source="imported", summary=True)

    def test_bad_filters_and_bad_status_are_fixed_validation_errors(self):
        for filters in [{"source": "private"}, {"model": "person@example.org"}, {"run_id": "bad"}]:
            with self.assertRaises(ValueError):
                self.collector.report(**filters)
        value = response()
        value["status"] = []
        with self.assertRaises(ValueError):
            normalize_response(value)

    def test_provider_json_rejects_duplicate_fields(self):
        class Reply:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, size):
                return b'{"usage":null,"usage":{}}'
        with patch("agentledger.provider.build_opener") as build:
            build.return_value.open.return_value = Reply()
            with self.assertRaisesRegex(ValueError, "invalid_json"):
                request_response("key", "demo-model", "PRIVATE", 512)


if __name__ == "__main__":
    unittest.main()
