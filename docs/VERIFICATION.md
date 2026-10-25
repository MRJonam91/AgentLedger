# Release verification / Verifiche release

**Current stable / Stabile attuale:** [1.0 verification record / Verifiche 1.0](VERIFICATION_V1.md). [Beta evidence / Evidenze beta](VERIFICATION_BETA.md) and the alpha evidence below are historical and preserved. / Le evidenze beta e alfa sotto sono storiche e conservate.

[Stable v1.0.0](https://github.com/MRJonam91/AgentLedger/releases/tag/v1.0.0) published on 2026-10-25: 87 local/extracted-source tests passed, independent review approved, four-job Windows/Linux Python 3.11/3.14 CI passed on the release revision, installed workflow and archive/remote checksums verified. Repository visibility is public. / Pubblicata il 2026-10-25: 87 test locali/dai sorgenti, revisione approvata, CI a quattro job superata, flusso installato e checksum verificati. Repository pubblica.

## Historical releases / Release storiche

Beta `v0.2.0-beta.1` published on 2026-10-24: 72 local tests, four successful Windows/Linux Python 3.11/3.14 CI jobs, independently reviewed, installed-package workflow and release digests verified. / Beta pubblicata il 2026-10-24: 72 test locali, quattro job CI superati, revisione indipendente, flusso installato e digest verificati. [Release](https://github.com/MRJonam91/AgentLedger/releases/tag/v0.2.0-beta.1).

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

- [Repository](https://github.com/MRJonam91/AgentLedger) created private first and pushed with initial commit `ab4851a16f5002d2fb135c3cd958a6d1c8b935d0`; made public only after local checks, independent review and remote CI succeeded. / Creato inizialmente privato e reso pubblico dopo controlli locali, revisione e CI.
- [GitHub Actions run 40020597334](https://github.com/MRJonam91/AgentLedger/actions/runs/40020597334): **all four jobs succeeded** on Ubuntu/Windows and Python 3.11/3.14. Each ran 41 tests, source/history scan, static checks, build, wheel installation and installed-entrypoint smoke. / Quattro job superati con test, scansione, controlli statici, build, installazione e prova CLI.
- Default branch `main`, owner MRJonam91, 12 topics, description, GPLv3 detection and `.github/FUNDING.yml` verified through GitHub API. `main` currently has no branch protection; no protected-branch or signed-tag claim is made. / Verificati branch, proprietario, topic, descrizione, riconoscimento licenza e funding; branch non protetto, nessuna affermazione di tag firmato.
- `python scripts/check_project.py --history` inspected the complete new reachable history and noreply authorship with zero findings in its defined scan scope. Generated databases, environments and test results remain ignored. / Cronologia e autori noreply controllati senza rilievi nel perimetro dichiarato; dati generati ignorati.
- [Release-target CI run 40020950027](https://github.com/MRJonam91/AgentLedger/actions/runs/40020950027) succeeded at `d336c8623a69bb98c5eb7c4fbce96fa797fe8129`, the exact commit referenced by annotated tag `v0.1.0-alpha.1`. Tag is unsigned. / CI superata sul commit esatto del tag annotato, non firmato.
- [Public prerelease](https://github.com/MRJonam91/AgentLedger/releases/tag/v0.1.0-alpha.1) verified as published, not a draft. GitHub asset digests match the local wheel, source archive and SHA256SUMS.txt. / Prerelease pubblica verificata, non bozza; digest remoti uguali ai file locali.
- Release artifact scan: zero findings in the defined credential/email/path scan; tar owners are empty (no local account metadata). Final source-archive checker inspected 51 distributed files, including Git attributes and generated source metadata, with zero errors. / Nessun rilievo nella scansione dichiarata; proprietari tar vuoti. Controllati 51 file finali dell'archivio sorgente.
- Post-release default-branch changes only complete this evidence/checklist; runtime and tag remain unchanged. / Le modifiche successive sul branch predefinito completano solo evidenze/checklist; codice e tag restano invariati.

| Asset | SHA-256 |
|---|---|
| `agentledger_local-0.1.0a1-py3-none-any.whl` | `b65e6b8a788ed9a0116ff86319068ed2ea0170258f9eb493cbd83409327a5222` |
| `agentledger_local-0.1.0a1.tar.gz` | `a833898572e7dd29daf3a402588d3b345a1a63a4251737d4e1e6b688cfb893ed` |
| `SHA256SUMS.txt` | `4745d4d6ad876800cde9735ba49570fc2e0f566d732a02eafbe427d0f9e708ba` |
