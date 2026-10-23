# AgentLedger contributor guidance

Read `docs/ARCHITECTURE.md` before changing module boundaries and `docs/EVENTS.md` before changing persistence. Read `docs/THREAT_MODEL.md` before changing collection, permissions or networking. The active alpha contract is `docs/superpowers/specs/2026-10-23-alpha-design.md`; future behavior changes need a written scope, design and verification plan in `docs/`.

Keep runtime dependency-free and Python 3.11 compatible. Runtime scope is `agentledger/*.py`, below 1,500 physical lines. Use `python -m unittest discover -s tests -v` and `python scripts/check_project.py`; test changed behavior before implementation. Restricted Windows environments may require an existing checkout-local TEMP/TMP directory.

Preserve strict content minimization, default deny before network effects, Decimal costs and separate demo/imported/live evidence. Store only normalized metadata; keep raw provider exceptions, prompts, outputs and keys out of logs and fixtures. Test the HTTP seam offline; live paid calls require a deliberately configured local environment.

Update English and Italian user documentation together. Every source file has an SPDX header. Apply the documented GPL-3.0-or-later decision, attribution and repository funding files. Before publishing inspect tracked files, all reachable commits, author metadata, release contents and checksums. Record actual test results and skipped checks in `docs/VERIFICATION.md`.
