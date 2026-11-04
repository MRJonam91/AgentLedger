# 1.0.1 maintenance design / Manutenzione 1.0.1

Scope / Perimetro: bounded fixes to the existing local CLI and accounting contract after a functional audit. The 1.0 schema, hash inputs, source labels and command defaults remain compatible. / Correzioni circoscritte dopo revisione funzionale; schema, hash, fonti e valori predefiniti della 1.0 restano compatibili.

Reproduced / Riprodotti:

- An explicitly empty checkpoint path silently becomes unanchored verification. Empty output/rates/policy paths are also treated as missing options. Distinguish omitted (`None`) from provided paths; empty paths must fail with safe JSON errors, never silently weaken the requested operation. Invalid rate/policy paths must not create a new ledger. / Un percorso vuoto esplicito deve fallire, non disattivare l'opzione o creare un registro.
- Decimal pricing/report contexts inherit the caller's exponent bounds and traps. This can throw or persist Infinity for ordinary valid rates. Use a fully specified independent context for exact arithmetic. Reject nonfinite or out-of-range stored per-response amounts with `invalid_cost`; preserve the ledger bytes and never rewrite historical events. / Contesto Decimal indipendente e rifiuto di importi persistiti non finiti/fuori limite, senza riscritture.
- A backup descriptor-close failure occurs before output ownership is recorded, leaving an empty output file. Record ownership immediately after exclusive creation, so failure removes only this attempt's new file. Existing destinations remain byte-identical. / Registrare subito la creazione esclusiva per eliminare solo il nuovo file su errore.

Limits / Limiti: no migration, runtime dependency, paid provider calls, automatic retry, new provider/pricing assumption or UI subsystem. Keep runtime below 1,500 physical lines and update EN/IT docs together. Exact costs remain user-rate calculations, not invoices. / Nessuna migrazione, dipendenza runtime, chiamata a pagamento, retry, nuova assunzione provider/prezzi o sottosistema grafico.

2026-11-04 review clarification / Chiarimento revisione: old Decimal clamp settings can add insignificant trailing zeros to an otherwise exact valid amount. Validate numeric representability after disregarding those zeros for calculation only; preserve original stored strings, event hashes and database bytes. / La validazione ignora gli zeri finali non significativi solo per il calcolo, conservando stringhe originali, hash e byte del registro.

Success / Successo: fail-first regressions for empty paths, restricted Decimal contexts/traps and backup close failure; legacy nonfinite costs fail closed in reports without modifying history; alpha/beta/1.0 compatibility and all existing workflow, loopback/process tests pass. Review changes independently, install/package smoke-test, inspect public contents/history and publish a checksummed maintenance patch after CI. / Test prima del fix, compatibilità, revisione, prova pacchetto e pubblicazione verificata.
