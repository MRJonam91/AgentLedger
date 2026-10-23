# Alpha verification / Verifica alfa

Date / Data: 2026-10-23. Version / Versione: 0.1.0a1.

EN: This file records release evidence, not a certification. Local verification completed; remote results are recorded separately below. / IT: Questo file registra evidenze di release, non una certificazione. Verifiche locali completate; risultati remoti registrati separatamente sotto.

- Initial suite / Suite iniziale: 33 tests passed on Windows with Python 3.14; real SQLite, offline HTTP seam, CLI subprocesses.
- Independent review / Revisione indipendente: one reviewer inspected the runtime and ran all 33 tests. Found missing schema-shape validation (Important) and argparse errors bypassing JSON (Minor). Both reproduced with failing regression tests and corrected; 36 tests then passed.
- Explicitly unperformed / Esplicitamente non eseguiti: paid live-provider request, invoice reconciliation, external pilot, independent security audit, large-ledger performance and Docker. The release is a local CLI; Docker is not a deliverable.
- Privacy/publication scan / Scansione: known credential/email/path patterns plus review of tracked contents and reachable Git history; no assertion of comprehensive secret detection.
- Model price/availability / Prezzi e disponibilità: no live values assumed; sample is synthetic. No external model or API key required for demo and tests.
- Funding / Sostegno: repository metadata and links checked; provider-program eligibility and donation transactions are not tested.

## Final local evidence / Evidenze locali finali

- `python -m unittest discover -s tests -v`: **41 passed** on Windows/Python 3.14.3. Includes content minimization, exact cached-token pricing, default deny before HTTP, unknown/pending outcomes, duplicate/concurrent imports, tamper/checkpoint/schema checks, CLI subprocess workflows and source-archive publication scanning.
- A second independent review found a SQLite LIKE wildcard issue allowing a user trigger to suppress inserts. Two failing regressions reproduced it; literal internal-prefix filtering and insert-row verification fixed it. Final reviewer verdict: approved within local-alpha scope; independently ran all 40 tests with no remaining material findings.
- `python -m mypy --check-untyped-defs agentledger`: no issues in seven source files after explicit source-summary typing. This is partial static analysis, not full strict typing. / Analisi statica parziale, non tipizzazione strict completa.
- `python scripts/check_project.py`: zero errors across 49 public source/documentation files. Runtime scope is all seven `agentledger/*.py` files: **563 physical lines including comments/blanks**, counted by `splitlines()`.
- `.venv/Scripts/python -m build --no-isolation`: built wheel and source archive using build 1.6.1 / setuptools 84.2.1 / wheel 0.48.0. Mypy 2.4.0 used for static checks. Build tooling is not included in runtime.
- Installed wheel with `--no-deps --no-index` into a new venv, then ran installed `agentledger --version`, `demo`, `report --format markdown` and `verify` from a separate directory. Confirmed import resolves to installed site-packages; 3 events, 1 allow, 1 deny, synthetic USD 0.0057.
- Inspected wheel (15 entries) for LICENSE/NOTICE/THIRD_PARTY_NOTICES and zero `Requires-Dist` runtime dependencies. Source archive includes examples, tests, specifications, docs and funding/CI metadata; private SQLite files, venvs and test outputs are excluded.
- Sandbox-only issue / Problema solo sandbox: system TEMP access/cleanup restrictions required checkout-local TEMP/TMP for tests/build. An initial wheel install completed but pip reported sandbox TEMP cleanup warnings; the installed CLI smoke succeeded. No source data was published from temporary directories.
- The source archive's project checker was also exercised after extraction inside a parent checkout. A failing regression caught accidental use of the parent's Git index; the checker now falls back to the archive tree. Final extracted-source scan: 50 files including generated metadata, zero errors. / Verificato anche il controllo dell'archivio estratto; corretto con test un uso accidentale dell'indice Git del checkout padre. 50 file inclusi metadati generati, zero errori.

## Remote evidence / Evidenze remote

Repository, CI, visibility, refs and release assets are verified during publication. / Repository, CI, visibilità, riferimenti e asset della release vengono verificati durante la pubblicazione.
