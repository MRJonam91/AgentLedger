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

Packaging, exact-revision CI and remote release results are recorded after execution. / Pacchetti, CI della revisione esatta e release remota vengono registrati dopo l'esecuzione.
