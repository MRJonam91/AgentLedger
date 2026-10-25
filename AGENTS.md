# AgentLedger contributor guidance

Read `docs/ARCHITECTURE.md` before changing module boundaries and `docs/EVENTS.md` before changing persistence. Read `docs/THREAT_MODEL.md` before changing collection, permissions or networking. The stable contract is `docs/superpowers/specs/2026-10-24-v1-design.md`; alpha/beta records retain v1 compatibility. Future behavior changes need a written scope, design and verification plan in `docs/`.

Keep runtime dependency-free and Python 3.11 compatible. Runtime scope is `agentledger/*.py`, below 1,500 physical lines. Use `python -m unittest discover -s tests -v` and `python scripts/check_project.py`; test changed behavior before implementation. Restricted Windows environments may require an existing checkout-local TEMP/TMP directory.

Preserve strict content minimization, default deny before network effects, Decimal costs and separate demo/imported/live evidence. Store only normalized metadata; keep raw provider exceptions, prompts, outputs and keys out of logs and fixtures. Test the HTTP seam offline; live paid calls require a deliberately configured local environment.

For collection changes, test all-or-nothing batches, duplicate/concurrent writes and no new ledger on invalid imports/requests. For maintenance, test prefix checkpoints after appends and truncation, read-only inspection, idempotent init, exclusive exports, verified backups and byte-identical existing destinations. Always verify the full chain before report filtering. Keep checkpoint files in separately trusted storage and no-overwrite operations explicit. Exercise loopback transport and separate-process concurrency tests without paid calls.

Update English and Italian user documentation together. Every source file has an SPDX header. Apply the documented GPL-3.0-or-later decision, attribution and repository funding files. Before publishing inspect tracked files, all reachable commits, author metadata, release contents and checksums. Record actual test results and skipped checks in `docs/VERIFICATION.md`.
