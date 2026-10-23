# SPDX-License-Identifier: GPL-3.0-or-later
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from agentledger.domain import Policy, RateCard
from agentledger.service import Collector
from agentledger.storage import Ledger
from agentledger.provider import request_response
from test_domain import card, policy, response


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.sqlite3"
        self.collector = Collector(Ledger(self.path, create=True))
        self.rates = RateCard.from_dict(card())
        self.policy = Policy.from_dict(policy())

    def run_agent(self, transport, policy_value=None, api_key="PRIVATE API KEY"):
        return self.collector.run("demo-model", "PRIVATE PROMPT", 512,
                                  policy_value or self.policy, api_key, self.rates,
                                  transport=transport)

    def test_deny_durably_logged_without_transport(self):
        def forbidden(*args):
            self.fail("Denied request contacted provider")
        result = self.run_agent(forbidden, Policy.from_dict(None))
        self.assertEqual(result["status"], "denied")
        self.assertEqual(self.collector.report()["decisions"]["denied"], 1)

    def test_suppressed_decision_insert_prevents_provider_contact(self):
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("""CREATE TRIGGER sqlitex_ignore BEFORE INSERT ON events
                BEGIN SELECT RAISE(IGNORE); END""")
        with self.assertRaisesRegex(ValueError, "unsupported_schema"):
            self.run_agent(lambda *args: self.fail("Provider called before durable decision"))

    def test_allowed_decision_precedes_transport_and_content_is_dropped(self):
        def transport(*args):
            events = Ledger(self.path).read()
            self.assertEqual(events[-1]["kind"], "decision")
            self.assertEqual(events[-1]["data"]["reason"], "allowed")
            return response()
        result = self.run_agent(transport)
        self.assertEqual(result["status"], "completed")
        data = json.dumps(self.collector.report())
        self.assertNotIn("PRIVATE", data)
        self.assertNotIn(b"PRIVATE", self.path.read_bytes())
        summary = self.collector.report()["sources"]["live"]
        self.assertEqual(summary["calculated_usd"], "0.0057")
        self.assertEqual(summary["priced"], 1)

    def test_import_is_untrusted_and_duplicate_not_counted(self):
        self.collector.import_response(response(), self.rates)
        with self.assertRaises(ValueError):
            self.collector.import_response(response(), self.rates)
        report = self.collector.report()
        self.assertEqual(report["sources"]["imported"]["records"], 1)
        self.assertEqual(report["sources"]["live"]["records"], 0)
        self.assertEqual(len(report["events"]), 1)

    def test_missing_rates_and_mismatch_are_unpriced_not_zero(self):
        self.collector.import_response(response())
        changed = response()
        changed.update(id="resp_fixture_2", model="other-model")
        self.collector.import_response(changed, self.rates)
        summary = self.collector.report()["sources"]["imported"]
        self.assertEqual(summary["unpriced"], 2)
        self.assertIsNone(summary["calculated_usd"])

    def test_transport_error_is_unknown_no_retry_or_error_leak(self):
        calls = []
        def broken(*args):
            calls.append(1)
            raise RuntimeError("PRIVATE KEY AND PROMPT")
        result = self.run_agent(broken)
        self.assertEqual(calls, [1])
        self.assertEqual(result["status"], "unknown")
        report = self.collector.report()
        self.assertEqual(report["unknown_outcomes"], 1)
        self.assertNotIn("PRIVATE", json.dumps(report))

    def test_invalid_live_response_is_unknown(self):
        value = response()
        value["usage"] = None
        result = self.run_agent(lambda *args: value)
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(self.collector.report()["unknown_outcomes"], 1)

    def test_no_key_is_local_error_and_no_provider_attempt(self):
        result = self.run_agent(lambda *args: self.fail("no key"), api_key="")
        self.assertEqual(result["status"], "not_sent")
        self.assertEqual(self.collector.report()["unknown_outcomes"], 0)

    def test_unfinished_allowed_attempt_is_explicit(self):
        def interrupted(*args):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            self.run_agent(interrupted)
        self.assertEqual(self.collector.report()["pending_runs"], 1)

    def test_provider_contract_no_tools_store_or_redirects(self):
        class Reply:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, size):
                return json.dumps(response()).encode()
        with patch("agentledger.provider.build_opener") as build:
            build.return_value.open.return_value = Reply()
            self.assertEqual(request_response("key", "demo-model", "prompt", 512)["id"],
                             "resp_fixture_1")
            args, kwargs = build.return_value.open.call_args
            request = args[0]
            payload = json.loads(request.data)
            self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
            self.assertFalse(payload["store"])
            self.assertEqual(payload["tools"], [])
            self.assertEqual(payload["input"], "prompt")
            self.assertEqual(kwargs["timeout"], 60)


if __name__ == "__main__":
    unittest.main()
