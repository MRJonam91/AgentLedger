# Roadmap / Prossimi passi

## Alpha 0.1 / Alfa 0.1

EN: Implemented: CLI collector, one-step text adapter, strict allow/deny, normalized imports, exact configured text cost calculation, transactional hash chain, JSON/Markdown exports and offline reproducible trial. Treat publication and CI as separate release checks in VERIFICATION.md.

IT: Implementati: collettore CLI, adapter testuale a un passo, allow/deny, importazioni normalizzate, costo testuale da tariffe configurate, catena transazionale, export JSON/Markdown e prova offline ripetibile. Pubblicazione e CI sono verifiche separate in VERIFICATION.md.

## Next analysis / Prossima analisi

1. EN: Run a deliberately authorized pilot with one real developer, model and rate card. Compare one provider usage record against the ledger and the applicable invoice basis. IT: Prova autorizzata con sviluppatore, modello e tariffe reali; confronto tra consumo provider, registro e base di fatturazione.
2. EN: Measure missing usage, pending outcomes, ingest volume and usefulness of exports. Success: reconstruct every attempted adapter action and explicitly explain every unknown. IT: Misurare consumi mancanti, esiti pendenti, volume e utilità degli export; ricostruire ogni tentativo ed esplicitare ogni ignoto.
3. EN: Examine actual TokenWatch/OpenAgentOS data contracts before choosing a bridge; avoid duplicating their runtime/proxy. IT: Esaminare i contratti reali prima di scegliere un'integrazione, evitando di duplicare runtime/proxy.

## Design before implementation / Design prima dell'implementazione

EN: Possible next slices, each requiring its own written specification and tests: read-only runtime adapter with stable run IDs; local graphical report if pilots need it; rate provenance and reconciliation; external checkpoint signing; bounded rotation/migration for large ledgers. Multi-provider billing, tools/permissions outside this adapter, team hosting and encryption need separate threat/design work. None is a current feature or delivery commitment.

IT: Possibili prossime sezioni, ognuna con specifica e test propri: adapter runtime di sola lettura con ID stabili; report grafico locale se utile ai piloti; provenienza tariffe e riconciliazione; firma esterna checkpoint; rotazione/migrazione limitata per registri grandi. Fatturazione multiprovider, tool/permessi esterni all'adapter, hosting di squadra e cifratura richiedono analisi separate. Non sono funzionalità attuali o impegni di consegna.
