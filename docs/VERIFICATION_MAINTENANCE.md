# 1.0.1 maintenance verification / Verifiche manutenzione

Verification date / Data verifiche: 2026-11-04. Version / Versione: 1.0.1. Maintenance work began / Manutenzione avviata: 2026-10-25.

- Baseline: 87 tests passed, eight modules passed mypy and project checks found no issues before changes. Real loopback HTTP tests ran against synthetic local traffic only. / Base: 87 test e controlli superati, solo traffico sintetico locale.
- Functional audit reproduced explicit empty checkpoint paths producing unanchored success, empty rates/policy/output paths being ignored, caller Decimal context corrupting/failing exact cost calculations, and a failed descriptor close leaving a new empty backup. / Riprodotti percorsi vuoti ignorati, dipendenza dal contesto Decimal e backup vuoto residuo su errore.
- Eight maintenance regression tests failed before implementation, including isolated legacy-invalid-cost cases. After changes all eight passed, mypy passed all runtime modules and project/whitespace checks passed. / Otto test di regressione prima falliti e poi superati, inclusi importi storici invalidi isolati; controlli statici/progetto superati.
- v1 database/hash format retained, no automatic history rewriting. No paid provider request, invoice reconciliation, external pilot or independent security certification. / Formato v1 invariato, nessuna riscrittura automatica o validazione provider/fatture/pilota/certificazione implicita.

## Review and local evidence / Revisione ed evidenze locali

- Full suite on 2026-11-04: **97 tests passed** on Windows/Python 3.14.3, including real synthetic loopback HTTP and separate-process concurrency. Mypy passed eight runtime modules; project check found zero issues with **845 physical core lines** and 74 candidate public files before incorporating an upstream documentation-only change. / Suite completa di 97 test e controlli statici superati.
- Standards review: no hard documented breaches or material code-smell findings. Specification review found one real compatibility defect: a valid 1.0.0 amount padded by a caller's Decimal clamp was incorrectly rejected. Added a failing regression, fixed numeric normalization for calculation only and obtained an independent passing recheck. Original event values, checkpoint and database bytes remain unchanged. / Revisione standard senza rilievi materiali; difetto di compatibilità riprodotto, corretto e riverificato indipendentemente.
- Differential check against actual `v1.0.0` code preserved four historical clamp representations. An independent Fraction-based comparison verified **500 exact price calculations** under both trapped and untrapped restricted Decimal contexts. / Confrontati quattro casi prodotti dalla 1.0.0 e 500 calcoli esatti con aritmetica razionale indipendente.
- Backup ownership ordering covers the injected failure after descriptor release; no blind descriptor-close retries are introduced. / Verificata la pulizia nel caso di errore segnalato dopo il rilascio del descrittore, senza retry ciechi sulla chiusura.

## Package and release / Pacchetto e release

- Fresh 1.0.1 wheel installation with `--no-deps --no-index` passed the complete eight-event CLI workflow from a new directory: idempotent init, import, exclusive JSON/Markdown export, prefix checkpoint, backup and byte-preserving no-overwrite failures. Explicitly empty checkpoint/output arguments returned safe errors. / Installazione pulita e flusso completo verificati, inclusi gli errori su percorsi vuoti.
- Extracted-source suite: **97 tests passed**. Source-archive project scan: **77 distributed files**, zero configured findings; no runtime dependencies in the wheel. All **75 tracked source/documentation files** and all eight runtime modules matched the release commit, allowing only newline normalization. License notices included, archive owner/group metadata empty, public distribution contract inspected. / Verificati sorgenti estratti, corrispondenza con il commit, licenze e contenuti pubblici.
- Actual upgrade trial loaded the original 1.0.0 wheel, created a synthetic ledger under clamped Decimal settings, then opened it with the installed 1.0.1 wheel. Report amount was exactly **0.0057**, with identical checkpoint and database bytes. / Provato l'aggiornamento reale fra i due wheel, con checkpoint e byte invariati.
- Upstream commit `b0fbf5c` was incorporated without losing its bilingual quick-start and feedback documentation. No remote history was rewritten. / Aggiornamento remoto incorporato preservando documenti e cronologia.
- [Candidate CI 41926556911](https://github.com/MRJonam91/AgentLedger/actions/runs/41926556911) and [main CI 41926962165](https://github.com/MRJonam91/AgentLedger/actions/runs/41926962165) both passed all four Windows/Linux Python 3.11/3.14 jobs on exact release commit **23b44532b6935def078247c98d0fdd65d0859fa3**. Jobs include tests, static/project/history checks, build/install and installed workflow. / Entrambe le CI superate sulla revisione esatta.
- [v1.0.1](https://github.com/MRJonam91/AgentLedger/releases/tag/v1.0.1) published as latest stable release, not draft/prerelease; repository remains public. Annotated unsigned tag resolves to the tested commit. All three remote asset digests match local files. / Release stabile pubblicata su repository pubblica, con tag sul commit testato e digest corrispondenti.
- Full pre-release history check covered ten reachable commits with zero findings in its declared scope. Final default-branch changes only complete documentation/checklists; runtime and released artefacts remain unchanged. / Cronologia controllata nel perimetro dichiarato; modifiche finali limitate a documentazione e checklist.

| Asset | SHA-256 |
|---|---|
| `agentledger_local-1.0.1-py3-none-any.whl` | `584506081d3e0e67dffe3efabc68afd085c7785ecc68118b53f79683b38ada3b` |
| `agentledger_local-1.0.1.tar.gz` | `e05ae0852004d681a41732caec9dfb4d83d79cbd596b59a5c1567daf3b55b61f` |
| `SHA256SUMS.txt` | `043a2821fe63e9e24eafbef6b036f7a22bffda4f5f1bdb86f10f4e964d165271` |
