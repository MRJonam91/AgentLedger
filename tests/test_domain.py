# SPDX-License-Identifier: GPL-3.0-or-later
import copy
import unittest
from decimal import Decimal

from agentledger.domain import Policy, RateCard, normalize_response


def response():
    return {"id": "resp_fixture_1", "model": "demo-model", "status": "completed",
            "usage": {"input_tokens": 1000, "input_tokens_details": {"cached_tokens": 200},
                      "output_tokens": 500, "total_tokens": 1500},
            "output": [{"text": "PRIVATE RESPONSE"}], "input": "PRIVATE PROMPT"}


def card():
    return {"schema_version": 1, "provider": "openai", "model": "demo-model",
            "currency": "USD", "effective_date": "2026-10-23",
            "input_per_million": "2", "cached_input_per_million": "0.5",
            "output_per_million": "8"}


def policy():
    return {"schema_version": 1, "allowed_models": ["demo-model"], "max_output_tokens": 1024}


class DomainTests(unittest.TestCase):
    def test_normalizes_without_content_or_provider_id(self):
        normalized = normalize_response(response())
        self.assertEqual(normalized["input_tokens"], 1000)
        self.assertEqual(normalized["cached_tokens"], 200)
        self.assertEqual(len(normalized["response_key"]), 64)
        self.assertNotIn("PRIVATE", str(normalized))
        self.assertNotIn("resp_fixture", str(normalized))

    def test_exact_cached_cost(self):
        priced = RateCard.from_dict(card()).price(normalize_response(response()))
        self.assertEqual(Decimal(priced["amount"]), Decimal("0.0057"))
        self.assertEqual(priced["basis"], "configured_rates")
        self.assertEqual(priced["rates"], card())

    def test_model_mismatch_unpriced(self):
        value = response()
        value["model"] = "different-model"
        self.assertEqual(RateCard.from_dict(card()).price(normalize_response(value)),
                         {"basis": "unpriced", "reason": "model_mismatch"})

    def test_invalid_usage_rejected(self):
        for field, bad in [("input_tokens", -1), ("output_tokens", True),
                           ("total_tokens", 99), ("output_tokens", 1.5),
                           ("input_tokens", 10**15), ("input_tokens", "1000")]:
            with self.subTest(field=field, bad=bad):
                value = response()
                value["usage"][field] = bad
                with self.assertRaises(ValueError):
                    normalize_response(value)

    def test_missing_usage_cache_and_failed_status_rejected(self):
        for mutate in [lambda r: r.update(usage=None),
                       lambda r: r["usage"].pop("input_tokens_details"),
                       lambda r: r.update(status="failed"),
                       lambda r: r.update(model="secret@example.org"),
                       lambda r: r.update(id=""),
                       lambda r: r["usage"]["input_tokens_details"].update(cached_tokens=1001),
                       lambda r: r["usage"]["input_tokens_details"].update(cache_write_tokens=10)]:
            value = response()
            mutate(value)
            with self.assertRaises(ValueError):
                normalize_response(value)

    def test_incomplete_response_accounts_all_output(self):
        value = response()
        value["status"] = "incomplete"
        self.assertEqual(normalize_response(value)["output_tokens"], 500)

    def test_rates_reject_nonfinite_negative_numeric_and_unknown_keys(self):
        for bad in ["NaN", "Infinity", "-1", 2, "1e99", "0.1234567890123"]:
            value = card()
            value["input_per_million"] = bad
            with self.assertRaises(ValueError):
                RateCard.from_dict(value)
        for field, value in [("currency", "EUR"), ("effective_date", "bad"),
                             ("provider", "other"), ("extra", "PRIVATE")]:
            data = card()
            data[field] = value
            with self.assertRaises(ValueError):
                RateCard.from_dict(data)

    def test_default_deny_allow_exact_model_and_output_limit(self):
        self.assertEqual(Policy.from_dict(None).decide("demo-model", 10), "default_deny")
        p = Policy.from_dict(policy())
        self.assertEqual(p.decide("demo-model", 512), "allowed")
        self.assertEqual(p.decide("other-model", 512), "model_denied")
        self.assertEqual(p.decide("demo-model", 2048), "output_limit")

    def test_policy_is_strict(self):
        for change in [{"max_output_tokens": True}, {"allowed_models": "demo-model"},
                       {"max_output_tokens": 0}, {"schema_version": 2}, {"prompt": "PRIVATE"}]:
            value = copy.deepcopy(policy())
            value.update(change)
            with self.assertRaises(ValueError):
                Policy.from_dict(value)


if __name__ == "__main__":
    unittest.main()
