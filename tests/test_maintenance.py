# SPDX-License-Identifier: GPL-3.0-or-later
"""Data-preserving regressions found in the post-1.0 functional audit."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal, Inexact, Overflow, Underflow, localcontext
from pathlib import Path
from unittest.mock import patch

from agentledger.domain import RateCard, normalize_response
from agentledger.service import Collector
from agentledger.storage import Ledger
import agentledger.storage as storage
from test_domain import card, response

ROOT = Path(__file__).resolve().parents[1]


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.db = self.directory / "ledger.sqlite3"

    def cli(self, *args, prompt=None):
        return subprocess.run([sys.executable, "-m", "agentledger", "--db", str(self.db), *args],
            cwd=ROOT, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=15,
            env=dict(os.environ, OPENAI_API_KEY=""))

    def test_empty_checkpoint_is_error_and_not_unanchored_success(self):
        self.assertEqual(self.cli("demo").returncode, 0)
        before = self.db.read_bytes()
        result = self.cli("verify", "--checkpoint", "")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["error"], "local_storage_or_file_error")
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.db.read_bytes(), before)

    def test_empty_output_is_error_and_does_not_print_report(self):
        self.assertEqual(self.cli("demo").returncode, 0)
        before = self.db.read_bytes()
        result = self.cli("report", "--output", "")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.db.read_bytes(), before)

    def test_empty_rates_path_is_not_silently_unpriced(self):
        result = self.cli("import-response", "examples/response.json", "--rates", "")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.db.exists())
        self.assertEqual(result.stdout, "")

    def test_empty_policy_path_is_not_silently_default_deny(self):
        result = self.cli("run", "--model", "demo-model", "--policy", "", prompt="synthetic")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.db.exists())

    def test_prices_and_imports_are_independent_of_caller_decimal_context(self):
        rates = RateCard.from_dict(card())
        collector = Collector(Ledger(self.db, create=True))
        for index, trap in enumerate((True, False)):
            value = response()
            value["id"] += str(index)
            with self.subTest(trap=trap), localcontext() as context:
                context.prec, context.Emax, context.Emin = 2, 2, -2
                context.traps[Overflow] = trap
                context.traps[Underflow] = trap
                context.traps[Inexact] = trap
                result = rates.price(normalize_response(value))
                self.assertEqual(result["amount"], "0.0057")
                collector.import_response(value, rates)
                report = collector.report()
                self.assertEqual(report["sources"]["imported"]["calculated_usd"],
                                 ("0.0057", "0.0114")[index])
                self.assertEqual((context.prec, context.Emax, context.Emin), (2, 2, -2))
        for event in collector.ledger.read():
            self.assertTrue(Decimal(event["data"]["cost"]["amount"]).is_finite())

    def test_report_large_valid_subtotal_under_restricted_context(self):
        rates = card()
        rates.update(input_per_million="1000000", cached_input_per_million="1000000",
                     output_per_million="1000000")
        collector = Collector(Ledger(self.db, create=True))
        collector.import_response(response(), RateCard.from_dict(rates))
        for trap in (True, False):
            with self.subTest(trap=trap), localcontext() as context:
                context.Emax, context.Emin = 2, -2
                context.traps[Overflow] = trap
                self.assertEqual(collector.report()["sources"]["imported"]["calculated_usd"], "1500")

    def test_smallest_rates_and_maximum_v1_cost_remain_exact(self):
        collector = Collector(Ledger(self.db, create=True))
        tiny = response()
        tiny["usage"].update(input_tokens=1, output_tokens=1, total_tokens=2,
                             input_tokens_details={"cached_tokens": 0})
        small_rates = card()
        large_rates = card()
        for key in ("input_per_million", "cached_input_per_million", "output_per_million"):
            small_rates[key] = "0.000000000001"
            large_rates[key] = "1000000"
        maximum = response()
        maximum["id"] += "_maximum"
        maximum["usage"].update(input_tokens=10**9, output_tokens=10**9, total_tokens=2*10**9,
                                input_tokens_details={"cached_tokens": 0})
        with localcontext() as context:
            context.Emax, context.Emin = 2, -2
            context.traps[Overflow] = context.traps[Underflow] = context.traps[Inexact] = True
            collector.import_response(tiny, RateCard.from_dict(small_rates))
            collector.import_response(maximum, RateCard.from_dict(large_rates))
            self.assertEqual(collector.report()["sources"]["imported"]["calculated_usd"],
                             "2000000000.000000000000000002")

    def test_legacy_invalid_amount_fails_report_without_rewriting_history(self):
        usage = normalize_response(response())
        invalid = ("Infinity", "NaN", "-0.1", "2000000001", "bad", "sNaN",
                   "0." + "1" * 60, "1e-1000100", "0e-1000100", "0e1000100")
        for index, amount in enumerate(invalid):
            with self.subTest(amount=amount):
                self.db = self.directory / f"legacy-{index}.sqlite3"
                ledger = Ledger(self.db, create=True)
                ledger.append("historical", "usage", {"source": "imported", "provider": "openai",
                              "usage": usage, "cost": {"basis": "configured_rates", "amount": amount}})
                before = self.db.read_bytes()
                self.assertTrue(ledger.verify()["verified"])
                result = self.cli("report", "--summary")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stderr)["error"], "invalid_cost")
                self.assertEqual(result.stdout, "")
                self.assertEqual(self.db.read_bytes(), before)

    def test_legacy_clamped_finite_cost_preserves_value_and_history(self):
        usage = normalize_response(response())
        # v1.0.0 with Emax=6, Emin=-6 and clamp=1 produced this exact value.
        legacy = "0.0057" + "0" * 39
        ledger = Ledger(self.db, create=True)
        ledger.append("historical", "usage", {"source": "imported", "provider": "openai",
            "usage": usage, "cost": {"basis": "configured_rates", "amount": legacy}})
        before = self.db.read_bytes()
        before_head = ledger.verify()["checkpoint"]
        for trap in (True, False):
            with self.subTest(trap=trap), localcontext() as context:
                context.prec, context.Emax, context.Emin = 2, 2, -2
                context.traps[Inexact] = context.traps[Overflow] = context.traps[Underflow] = trap
                report = Collector(ledger).report()
                self.assertEqual(report["sources"]["imported"]["calculated_usd"], "0.0057")
                self.assertEqual(report["events"][0]["data"]["cost"]["amount"], legacy)
        self.assertEqual(ledger.verify()["checkpoint"], before_head)
        self.assertEqual(self.db.read_bytes(), before)

    def test_backup_close_failure_removes_only_new_owned_output(self):
        ledger = Ledger(self.db, create=True)
        ledger.append("run", "test", {})
        before = self.db.read_bytes()
        destination = self.directory / "backup.sqlite3"
        actual_close = storage.os.close
        def close_then_fail(fd):
            actual_close(fd)
            raise OSError("synthetic close failure")
        with patch.object(storage.os, "close", side_effect=close_then_fail):
            with self.assertRaises(OSError):
                ledger.backup(destination)
        self.assertFalse(destination.exists())
        self.assertEqual(self.db.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
