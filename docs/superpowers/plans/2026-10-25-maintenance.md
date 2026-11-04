# 1.0.1 implementation and verification plan

Spec: `docs/superpowers/specs/2026-10-25-maintenance-design.md`. Execute inline; one independent review before publication. / Esecuzione nella sessione, revisione indipendente prima della pubblicazione.

- [x] Add `tests/test_maintenance.py`: CLI subprocess regressions for empty checkpoint/output/rates/policy paths, no new ledger on invalid configuration, Decimal context independence with finite persistence/totals, legacy invalid-cost rejection and owned backup cleanup. Run before implementation and confirm failures.
- [x] Fix `cli.py` option presence checks, `domain.py`/`service.py` exact arithmetic and stored-amount validation, `storage.py` backup ownership ordering. Preserve schema/hash/default commands and byte-identical existing destinations. Run targeted regressions to green.
- [x] Update EN/IT README/support/error/compatibility notes, version 1.0.1, changelog and verification evidence. Run full suite, mypy, project/whitespace checks. Independently review the diff and address material findings with regressions. Full reachable-history checks remain part of the publication gate below.
- [x] Build/install and exercise the patch, compare archives against the commit and inspect distribution contents. Verify CI, publish maintenance assets/checksums, update release evidence and leave a clean synchronized checkout.
