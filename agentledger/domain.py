# SPDX-License-Identifier: GPL-3.0-or-later
"""Strict boundaries for usage, user-supplied rates and adapter policy."""

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def counter(value, minimum=0, maximum=10**9):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("invalid_counter")
    return value


def model_id(value):
    if (not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9.-]{0,95}", value)
            or value.startswith("sk-")):
        raise ValueError("invalid_model")
    return value


def exact_keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("invalid_fields")


def normalize_response(response):
    if not isinstance(response, dict):
        raise ValueError("invalid_response")
    rid = response.get("id")
    if not isinstance(rid, str) or not rid.startswith("resp_") or not 6 <= len(rid) <= 256:
        raise ValueError("invalid_response_id")
    model = model_id(response.get("model"))
    status = response.get("status")
    if not isinstance(status, str) or status not in {"completed", "incomplete"}:
        raise ValueError("unsupported_response_status")
    usage = response.get("usage")
    if not isinstance(usage, dict) or not isinstance(usage.get("input_tokens_details"), dict):
        raise ValueError("usage_missing")
    incoming = counter(usage.get("input_tokens"))
    outgoing = counter(usage.get("output_tokens"))
    total = counter(usage.get("total_tokens"), maximum=2*10**9)
    cached = counter(usage["input_tokens_details"].get("cached_tokens"))
    cache_write = counter(usage["input_tokens_details"].get("cache_write_tokens", 0))
    if cached > incoming or total != incoming + outgoing or cache_write:
        raise ValueError("unsupported_usage")
    return {"response_key": hashlib.sha256(rid.encode("utf-8")).hexdigest(),
            "model": model, "status": status, "input_tokens": incoming,
            "cached_tokens": cached, "output_tokens": outgoing, "total_tokens": total}


RATE_KEYS = {"schema_version", "provider", "model", "currency", "effective_date",
             "input_per_million", "cached_input_per_million", "output_per_million"}


@dataclass(frozen=True)
class RateCard:
    encoded: str

    @classmethod
    def from_dict(cls, value):
        exact_keys(value, RATE_KEYS)
        if type(value["schema_version"]) is not int or value["schema_version"] != 1:
            raise ValueError("unsupported_rate_version")
        if value["provider"] != "openai" or value["currency"] != "USD":
            raise ValueError("unsupported_rate_basis")
        model_id(value["model"])
        if not isinstance(value["effective_date"], str):
            raise ValueError("invalid_rate_date")
        try:
            parsed = date.fromisoformat(value["effective_date"])
            if parsed.isoformat() != value["effective_date"]:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("invalid_rate_date") from None
        for key in ("input_per_million", "cached_input_per_million", "output_per_million"):
            number = value[key]
            if (not isinstance(number, str)
                    or not re.fullmatch(r"\d{1,7}(?:\.\d{1,12})?", number)
                    or Decimal(number) > 1000000):
                raise ValueError("invalid_rate")
        return cls(canonical(value))

    def price(self, usage):
        rates = json.loads(self.encoded)
        if rates["model"] != usage["model"]:
            return {"basis": "unpriced", "reason": "model_mismatch"}
        with localcontext() as context:
            context.prec = 50
            amount = ((usage["input_tokens"] - usage["cached_tokens"])
                      * Decimal(rates["input_per_million"])
                      + usage["cached_tokens"] * Decimal(rates["cached_input_per_million"])
                      + usage["output_tokens"] * Decimal(rates["output_per_million"])) / 1000000
        return {"basis": "configured_rates", "amount": format(amount, "f"),
                "currency": "USD", "rates": rates, "rate_hash": digest(rates)}


@dataclass(frozen=True)
class Policy:
    models: tuple
    limit: int

    @classmethod
    def from_dict(cls, value):
        if value is None:
            return cls((), 1)
        exact_keys(value, {"schema_version", "allowed_models", "max_output_tokens"})
        if type(value["schema_version"]) is not int or value["schema_version"] != 1:
            raise ValueError("unsupported_policy_version")
        models = value["allowed_models"]
        if not isinstance(models, list) or len(models) > 100:
            raise ValueError("invalid_allowed_models")
        models = tuple(model_id(m) for m in models)
        if len(set(models)) != len(models):
            raise ValueError("duplicate_allowed_models")
        return cls(models, counter(value["max_output_tokens"], 1, 100000))

    def snapshot(self):
        return {"schema_version": 1, "allowed_models": list(self.models),
                "max_output_tokens": self.limit}

    def decide(self, model, max_output_tokens):
        model_id(model)
        counter(max_output_tokens, 1, 100000)
        if not self.models:
            return "default_deny"
        if model not in self.models:
            return "model_denied"
        if max_output_tokens > self.limit:
            return "output_limit"
        return "allowed"
