# Changelog / Modifiche

## 1.0.0 — 2026-10-25

- EN: Stable local CLI contract with explicit idempotent `init` and create-only JSON/Markdown report files. Existing destinations and v1 event hashes are preserved. IT: Contratto stabile con `init` idempotente ed export esclusivi; destinazioni e hash v1 conservati.
- EN: Shared request preflight prevents malformed requests from creating a ledger; strict JSON types and failure cleanup hardened. IT: Validazione condivisa prima della creazione del registro; tipi JSON e pulizia su errore rafforzati.
- EN: Separate-process concurrency, actual loopback HTTP/redirect/bounded-response tests, explicit distribution roots and installed-release checks. IT: Test fra processi e HTTP loopback, sorgenti distribuibili espliciti e prove della release installata.
- EN: EN/IT documentation, compatibility policy and completed local delivery roadmap; external provider/pilot/invoice validation remains separate. IT: Documenti EN/IT, compatibilità e piano locale allineati; validazioni esterne separate.

## 0.2.0b1 — 2026-10-24

- EN: Atomic JSONL imports, strict shared JSON decoding, verified batch transactions with one historical scan and streamed verification. IT: Import JSONL atomici, parsing JSON rigoroso condiviso, transazioni con una scansione storica e verifica in streaming.
- EN: Filter reports by source/model/run with whole-run context; compact summaries; reusable prefix checkpoints and verified no-overwrite SQLite backups. IT: Report per fonte/modello/esecuzione con contesto, riepiloghi compatti, checkpoint di prefisso e backup verificati senza sovrascrittura.
- EN: Fix source-label laundering via ingestion, non-roundtrippable default policy, malformed provider JSON/status and pending duplicate-live outcomes. Preserve alpha v1 schema/hash compatibility and existing CLI commands. IT: Corretti fonte import falsificabile, policy predefinita non ricaricabile, JSON/stato provider malformati ed esiti duplicati live pendenti. Compatibilità schema/hash alfa v1 e vecchi comandi mantenuta.
- EN: Expanded regression/compatibility/concurrency checks, reproducible benchmark and installed-package CI workflow. No paid-provider or external-pilot validation implied. IT: Test estesi di regressione/compatibilità/concorrenza, benchmark ripetibile e workflow CI del pacchetto installato. Nessuna validazione provider a pagamento o pilota esterno implicita.

## 0.1.0a1 — 2026-10-23

- EN: First usable local CLI: offline trial, strict Responses import, minimal text request adapter, allow/deny, usage/cached-token accounting and explicit configured rate snapshots. IT: Prima CLI locale utilizzabile con demo, importazione Responses, adapter testuale minimo, policy, contabilizzazione cache e tariffe esplicite.
- EN: Versioned transactional SQLite hash chain, duplicate protection, schema checks, checkpoint verification and JSON/Markdown reports. IT: Catena hash SQLite transazionale versionata, deduplicazione, verifica schema/checkpoint e report JSON/Markdown.
- EN: Bilingual project foundation, tests, packaging, CI, threat model and documented integration roadmap. IT: Fondamenta bilingui, test, pacchetto, CI, modello di minaccia e roadmap integrazioni.
- EN: Limitations: no provider/invoice attestation, OS sandbox, encryption, GUI or paid provider smoke test. IT: Limiti: nessuna attestazione provider/fattura, sandbox OS, cifratura, GUI o prova provider a pagamento.
