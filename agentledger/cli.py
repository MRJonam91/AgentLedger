# SPDX-License-Identifier: GPL-3.0-or-later
"""Command line interface. Data goes to stdout; safe failures go to stderr."""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

from . import __version__
from .domain import Policy, RateCard, normalize_response, validate_request
from .jsonio import read_jsonl, read_object as read_json, write_new_bytes, write_new_object
from .service import Collector
from .storage import GENESIS, Ledger

SAFE_ERRORS = {"ledger_missing", "unsupported_schema", "chain_invalid", "invalid_checkpoint",
               "checkpoint_mismatch", "duplicate_response", "invalid_fields", "invalid_counter",
               "invalid_model", "invalid_response", "invalid_response_id", "usage_missing",
               "unsupported_response_status", "unsupported_usage", "unsupported_rate_version",
               "unsupported_rate_basis", "invalid_rate_date", "invalid_rate", "invalid_allowed_models",
               "unsupported_policy_version", "duplicate_allowed_models", "invalid_prompt",
               "invalid_json", "input_too_large", "invalid_source", "append_not_persisted",
               "invalid_batch", "invalid_run_id", "output_exists"}


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, json.dumps({"error": "invalid_arguments_use_help"}) + "\n")


def markdown(report):
    lines = ["# AgentLedger", "", "Calculated subtotals from configured rates; not an invoice.",
             "Demo is synthetic; imports are unverified. Unpriced/unknown usage is excluded.", "",
             "| Source | Records | Input | Cached input | Output | Priced | Unpriced | Calculated USD |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for source, row in report["sources"].items():
        amount = row["calculated_usd"] if row["calculated_usd"] is not None else "unknown"
        lines.append(f"| {source} | {row['records']} | {row['input_tokens']} | {row['cached_tokens']} | "
                     f"{row['output_tokens']} | {row['priced']} | {row['unpriced']} | {amount} |")
    lines += ["", f"Allowed: {report['decisions']['allowed']}; denied: {report['decisions']['denied']}",
              f"Unknown outcomes: {report['unknown_outcomes']}; pending runs: {report['pending_runs']}",
              f"Selected events: {report['selected_event_count']}; full ledger: {report['event_count']}",
              "Filters: " + json.dumps(report["filters"], ensure_ascii=True, sort_keys=True),
              "", "Save this checkpoint separately to detect tail deletion:",
              f"`{report['checkpoint']}`"]
    if "events" in report:
        lines += ["", "| Seq | UTC | Source | Event | Detail |", "|---:|---|---|---|---|"]
    for event in report.get("events", []):
        data = event["data"]
        detail = data.get("reason", data.get("cost", {}).get("basis", ""))
        lines.append(f"| {event['seq']} | {event['at']} | {data.get('source', '')} | "
                     f"{event['kind']} | {detail} |")
    return "\n".join(lines) + "\n"


def parser():
    root = SafeParser(description="Local agent accounting / Registro locale agenti",
        epilog="Support / Sostieni: https://github.com/sponsors/MRJonam91 (voluntary / volontario)")
    root.add_argument("--version", action="version", version=__version__)
    root.add_argument("--db", default=".agentledger/ledger.sqlite3", help="Local SQLite path / Percorso SQLite")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Initialize or verify a ledger / Inizializza o verifica")
    commands.add_parser("demo", help="Offline synthetic allow/deny trial / Prova offline")
    imported = commands.add_parser("import-response", help="Import Responses API JSON / Importa JSON")
    imported.add_argument("file")
    imported.add_argument("--rates", help="User-supplied USD text rate card / Tariffe configurate")
    batch = commands.add_parser("import-jsonl", help="Atomic JSONL import / Importazione atomica")
    batch.add_argument("file")
    batch.add_argument("--rates")
    run = commands.add_parser("run", help="One text request; UTF-8 prompt on stdin / Prompt da stdin")
    run.add_argument("--model", required=True)
    run.add_argument("--max-output-tokens", type=int, default=512)
    run.add_argument("--policy", help="Without policy: deny / Senza policy: nega")
    run.add_argument("--rates")
    report = commands.add_parser("report", help="Verified export / Esporta registro verificato")
    report.add_argument("--format", choices=("json", "markdown"), default="json")
    report.add_argument("--source", choices=("demo", "imported", "live"))
    report.add_argument("--model")
    report.add_argument("--run-id")
    report.add_argument("--summary", action="store_true", help="Omit event details / Ometti dettagli")
    report.add_argument("--output", help="Create a new export file / Crea un nuovo file export")
    verify = commands.add_parser("verify", help="Check chain and optional head / Verifica catena")
    anchor = verify.add_mutually_exclusive_group()
    anchor.add_argument("--expected-head")
    anchor.add_argument("--checkpoint", help="Trusted prefix checkpoint / Checkpoint esterno fidato")
    checkpoint = commands.add_parser("checkpoint", help="Save a new checkpoint / Salva checkpoint")
    checkpoint.add_argument("--output", required=True)
    backup = commands.add_parser("backup", help="Verified SQLite snapshot / Copia SQLite verificata")
    backup.add_argument("destination")
    return root


def execute(args):
    if args.command == "init":
        path = Path(args.db)
        existing = path.exists() or path.is_symlink()
        return {"initialized": True, **Ledger(path, create=not existing).verify()}, 0
    if args.command in {"report", "verify", "checkpoint", "backup"}:
        ledger = Ledger(args.db)
        if args.command == "verify":
            checkpoint = read_json(args.checkpoint) if args.checkpoint else None
            return ledger.verify(expected_head=args.expected_head, checkpoint=checkpoint), 0
        if args.command == "checkpoint":
            state = ledger.verify()
            write_new_object(args.output, {"schema_version": 1, "event_count": state["event_count"],
                                          "checkpoint": state["checkpoint"]})
            return {"saved": True, **state}, 0
        if args.command == "backup":
            return ledger.backup(args.destination), 0
        report = Collector(ledger).report(args.source, args.model, args.run_id, args.summary)
        rendered = markdown(report) if args.format == "markdown" else report
        if args.output:
            content = rendered if isinstance(rendered, str) else json.dumps(rendered, ensure_ascii=True, indent=2) + "\n"
            write_new_bytes(args.output, content.encode("utf-8"))
            return {"saved": True, "format": args.format, "event_count": report["event_count"],
                    "selected_event_count": report["selected_event_count"], "checkpoint": report["checkpoint"]}, 0
        return rendered, 0
    rates = RateCard.from_dict(read_json(args.rates)) if getattr(args, "rates", None) else None
    if args.command == "import-response":
        response = read_json(args.file)
        normalize_response(response)
        return Collector(Ledger(args.db, create=True)).import_response(response, rates), 0
    if args.command == "import-jsonl":
        responses = read_jsonl(args.file)
        keys = [normalize_response(response)["response_key"] for response in responses]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate_response")
        return Collector(Ledger(args.db, create=True)).import_many(responses, rates), 0
    if args.command == "demo":
        return Collector(Ledger(args.db, create=True)).demo(), 0
    policy = Policy.from_dict(read_json(args.policy) if args.policy else None)
    raw = sys.stdin.buffer.read(65537)
    if len(raw) > 65536:
        raise ValueError("input_too_large")
    try:
        prompt = raw.decode("utf-8-sig")
    except UnicodeError:
        raise ValueError("invalid_prompt") from None
    validate_request(args.model, prompt, args.max_output_tokens)
    result = Collector(Ledger(args.db, create=True)).run(
        args.model, prompt, args.max_output_tokens, policy,
        os.environ.get("OPENAI_API_KEY", ""), rates)
    codes = {"completed": 0, "incomplete": 4, "denied": 3, "unknown": 4, "not_sent": 2}
    return result, codes[result["status"]]


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        value, code = execute(args)
        print(value if isinstance(value, str) else json.dumps(value, ensure_ascii=True, indent=2),
              end="" if isinstance(value, str) else "\n")
        return code
    except ValueError as exc:
        error = str(exc) if str(exc) in SAFE_ERRORS else "invalid_input"
    except (OSError, sqlite3.Error):
        error = "local_storage_or_file_error"
    except (TypeError, KeyError, RecursionError):
        error = "invalid_input"
    except KeyboardInterrupt:
        error = "interrupted_check_pending_runs"
    print(json.dumps({"error": error}), file=sys.stderr)
    return 2
