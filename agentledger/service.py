# SPDX-License-Identifier: GPL-3.0-or-later
"""Collection, durable policy decisions and source-separated accounting."""

from decimal import Decimal, localcontext
from typing import TypedDict
from uuid import uuid4

from .domain import Policy, RateCard, digest, normalize_response
from .provider import request_response
from .storage import GENESIS

SOURCES = ("demo", "imported", "live")


class SourceSummary(TypedDict):
    records: int
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    priced: int
    unpriced: int
    calculated_usd: str | None


class Collector:
    def __init__(self, ledger):
        self.ledger = ledger

    def _usage(self, normalized, rates, source, run_id):
        cost = rates.price(normalized) if rates else {"basis": "unpriced", "reason": "no_rates"}
        self.ledger.append(run_id, "usage", {"source": source, "provider": "openai",
                                            "usage": normalized, "cost": cost},
                           external_key=normalized["response_key"])
        return {"run_id": run_id, "status": normalized["status"], "cost": cost}

    def import_response(self, response, rates=None, source="imported"):
        if source not in SOURCES:
            raise ValueError("invalid_source")
        return self._usage(normalize_response(response), rates, source, str(uuid4()))

    def run(self, model, prompt, max_output_tokens, policy, api_key, rates=None,
            transport=request_response, _source="live"):
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode("utf-8")) > 65536:
            raise ValueError("invalid_prompt")
        if _source not in {"demo", "live"}:
            raise ValueError("invalid_source")
        reason = policy.decide(model, max_output_tokens)
        run_id = str(uuid4())
        snapshot = policy.snapshot()
        self.ledger.append(run_id, "decision", {"source": _source, "action": "ai.generate",
                           "model": model, "max_output_tokens": max_output_tokens,
                           "reason": reason, "policy": snapshot, "policy_hash": digest(snapshot)})
        if reason != "allowed":
            return {"run_id": run_id, "status": "denied", "reason": reason}
        if not api_key:
            self.ledger.append(run_id, "outcome", {"source": _source, "status": "not_sent",
                                                  "reason": "api_key_missing"})
            return {"run_id": run_id, "status": "not_sent", "reason": "api_key_missing"}
        try:
            response = transport(api_key, model, prompt, max_output_tokens)
        except Exception:
            self.ledger.append(run_id, "outcome", {"source": _source, "status": "unknown",
                                                  "reason": "transport_error"})
            return {"run_id": run_id, "status": "unknown", "reason": "transport_error"}
        try:
            normalized = normalize_response(response)
        except (ValueError, TypeError):
            self.ledger.append(run_id, "outcome", {"source": _source, "status": "unknown",
                                                  "reason": "provider_usage_invalid"})
            return {"run_id": run_id, "status": "unknown", "reason": "provider_usage_invalid"}
        return self._usage(normalized, rates, _source, run_id)

    def demo(self):
        rates = RateCard.from_dict({"schema_version": 1, "provider": "openai", "model": "demo-model",
                    "currency": "USD", "effective_date": "2026-10-23",
                    "input_per_million": "2", "cached_input_per_million": "0.5",
                    "output_per_million": "8"})
        response = {"id": "resp_demo_" + uuid4().hex, "model": "demo-model", "status": "completed",
                    "usage": {"input_tokens": 1000, "input_tokens_details": {"cached_tokens": 200},
                              "output_tokens": 500, "total_tokens": 1500}}
        allowed = Policy.from_dict({"schema_version": 1, "allowed_models": ["demo-model"],
                                    "max_output_tokens": 1024})
        self.run("demo-model", "offline fixture", 512, allowed, "offline", rates,
                 transport=lambda *args: response, _source="demo")
        self.run("demo-model", "offline fixture", 512, Policy.from_dict(None), "", rates,
                 transport=lambda *args: None, _source="demo")
        return self.report()

    def report(self):
        events = self.ledger.read()
        sources: dict[str, SourceSummary] = {
            source: {"records": 0, "input_tokens": 0, "cached_tokens": 0, "output_tokens": 0,
                     "priced": 0, "unpriced": 0, "calculated_usd": None} for source in SOURCES}
        totals = {source: Decimal(0) for source in SOURCES}
        decisions = {"allowed": 0, "denied": 0}
        started, finished = set(), set()
        unknown = 0
        for event in events:
            data = event["data"]
            if event["kind"] == "decision":
                allowed = data["reason"] == "allowed"
                decisions["allowed" if allowed else "denied"] += 1
                if allowed:
                    started.add(event["run_id"])
            elif event["kind"] == "outcome":
                finished.add(event["run_id"])
                unknown += data["status"] == "unknown"
            elif event["kind"] == "usage":
                finished.add(event["run_id"])
                source = data["source"]
                summary = sources[source]
                summary["records"] += 1
                summary["input_tokens"] += data["usage"]["input_tokens"]
                summary["cached_tokens"] += data["usage"]["cached_tokens"]
                summary["output_tokens"] += data["usage"]["output_tokens"]
                if data["cost"]["basis"] == "configured_rates":
                    summary["priced"] += 1
                    with localcontext() as context:
                        context.prec = 50
                        totals[source] += Decimal(data["cost"]["amount"])
                else:
                    summary["unpriced"] += 1
        for source, summary in sources.items():
            if summary["priced"]:
                summary["calculated_usd"] = format(totals[source], "f")
        return {"schema_version": 1, "checkpoint": events[-1]["hash"] if events else GENESIS,
                "event_count": len(events), "decisions": decisions, "sources": sources,
                "unknown_outcomes": unknown, "pending_runs": len(started - finished),
                "events": events}
