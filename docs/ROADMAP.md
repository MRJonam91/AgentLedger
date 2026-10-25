# Development plan / Piano di sviluppo

## Stable 1.0 / Stabile 1.0

EN: Deliver a local developer CLI for minimized accounting, repeatable collection and verified maintenance. The [implementation plan](superpowers/plans/2026-10-24-v1.md) and [verification](VERIFICATION_V1.md) track completion and publication separately. Alpha/beta evidence is historical. The stable label covers the implemented contract.

IT: Consegna una CLI locale per contabilità minimizzata, raccolta ripetibile e manutenzione verificata. [Piano](superpowers/plans/2026-10-24-v1.md) e [verifiche](VERIFICATION_V1.md) separano completamento e pubblicazione. Evidenze alfa/beta storiche. Stabile riguarda il contratto implementato.

| Delivery / Consegna | State / Stato | Evidence / Evidenza |
|---|---|---|
| Minimized collection, sources, exact costs / Raccolta, fonti, costi esatti | Implemented / Implementato | Domain/privacy/accounting tests |
| Default deny before effects / Nega prima degli effetti | Implemented / Implementato | Durable decision before transport |
| Atomic JSONL and dedupe / JSONL atomici e deduplicazione | Implemented / Implementato | Rollback, threads, separate processes |
| Verified whole-run reports / Report verificati per esecuzione | Implemented / Implementato | Hidden corruption/filter regressions |
| Prefix checkpoints and backups / Checkpoint e backup | Implemented / Implementato | Append/truncation, no-overwrite |
| Explicit init and exclusive exports / Init ed export esclusivi | Implemented / Implementato | Empty/existing/corrupt/failure tests |
| Alpha/beta v1 compatibility / Compatibilita v1 | Preserved / Conservata | Original alpha code and frozen fixture |
| Package/docs/CI/release / Pacchetto, documenti, CI e release | Release gates / Controlli release | Exact revision and asset checksums |

## Maintenance of 1.x / Manutenzione 1.x

EN: Prioritize reproducible defects, data-preserving fixes, compatibility and dependency-free runtime. Require explicit scope, regression tests, bilingual docs and verification for each behavior change. Preserve schema/hash v1 unless a separately designed major migration is approved. Measure performance with scripts/benchmark.py; local timings are observations, not throughput guarantees. Exercise installed packages at every release.

IT: Priorita a difetti riproducibili, preservazione dei dati, compatibilita e runtime senza dipendenze. Ogni modifica richiede scope, test, documenti bilingui e verifiche. Schema/hash v1 invariati salvo migrazione maggiore progettata separatamente. Misura con scripts/benchmark.py: tempi locali osservati, non garanzie. Prova i pacchetti installati a ogni release.

## Separate validation / Validazioni separate

EN: Real authorized developer pilots, paid-provider acceptance and invoice reconciliation need actual account/data evidence. These remain open validation activities, not missing features represented as complete. When authorized, record provenance, missing usage, pending outcomes and export usefulness; retain the distinction between observed counters and configured costs.

IT: Piloti reali autorizzati, accettazione provider a pagamento e riconciliazione richiedono dati/account effettivi. Restano validazioni aperte, senza rappresentarle come concluse. Quando autorizzate, registra provenienza, consumi mancanti, esiti pendenti e utilita export; distingui contatori osservati e costi configurati.

## Future initiatives / Iniziative future

EN: TokenWatch/OpenAgentOS adapters require actual source contracts and run correlation. A graphical view depends on user feedback. Other providers, rate provenance, signed checkpoints, rotation/migrations, team hosting and encryption require separate design/threat work. These are possible extensions, not missing 1.0 deliveries or date commitments.

IT: Adapter TokenWatch/OpenAgentOS richiedono contratti reali e correlazione. Una vista grafica dipende dai riscontri degli utenti. Altri provider, provenienza tariffe, firme, rotazione/migrazione, hosting di squadra e cifratura richiedono analisi separate. Sono estensioni possibili, non consegne mancanti della 1.0 o impegni di calendario.
