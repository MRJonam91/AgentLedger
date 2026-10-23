# Event contract v1 / Contratto eventi v1

EN: `PRAGMA user_version=1`, exact expected table and append guards are checked when opening and reading/writing. No automatic migrations. The SQLite `events` table contains `seq`, `at`, `run_id`, `kind`, canonical JSON `data`, nullable unique `external_key`, `prev_hash`, `hash`. Reports add `schema_version: 1` before verifying hashes.

IT: All'apertura e in lettura/scrittura vengono controllati `PRAGMA user_version=1`, tabella esatta e protezioni append. Nessuna migrazione automatica. La tabella SQLite `events` contiene `seq`, `at`, `run_id`, `kind`, `data` JSON canonico, `external_key` nullable e univoco, `prev_hash`, `hash`. I report aggiungono `schema_version: 1` prima di verificare gli hash.

| Kind / Tipo | Data / Dati | Meaning / Significato |
|---|---|---|
| `decision` | source, action=ai.generate, model, max_output_tokens, reason, policy snapshot/hash | Adapter allow/deny before HTTP / Decisione adapter prima di HTTP |
| `usage` | source, provider=openai, normalized usage, cost | Observed/imported/synthetic counters / Contatori osservati/importati/sintetici |
| `outcome` | source, status, fixed reason code | not_sent or unknown; never raw exception / non inviato o ignoto, mai eccezioni grezze |

EN: Usage contains hashed response ID, model, completed/incomplete status, input/cached/output/total token counts. Prices contain either `basis=unpriced` plus reason or `basis=configured_rates`, decimal USD amount, a rate snapshot and its SHA-256. The cost formula and source labels are public contract. `imported` never implies the request passed a local policy. `live` means this adapter contacted the fixed endpoint; neither is a signed provider attestation.

IT: Il consumo contiene digest dell'ID, modello, stato completed/incomplete e contatori ingresso/cache/uscita/totale. Il prezzo contiene `basis=unpriced` e motivo oppure `basis=configured_rates`, importo USD decimale, scheda tariffe e SHA-256. Formula e fonti sono contratto pubblico. `imported` non implica il superamento di una policy locale. `live` indica il contatto all'endpoint fisso da questo adapter; nessuno dei due è un'attestazione firmata dal provider.

```text
hash = SHA256(UTF8(JSON(event_without_hash,
       sort_keys=true, separators=(",", ":"), ensure_ascii=false, allow_nan=false)))
genesis = "0" repeated 64 times
external_key = SHA256(UTF8(provider_response_id)) for usage; null otherwise
```

EN: Sequences must be contiguous from 1, previous hashes must match and each hash must recompute. Unique response keys and SQLite transactions prevent concurrent double imports. An allowed decision without usage/outcome is `pending_runs`; an unknown outcome represents possible provider charges with unavailable usage. Checkpoints match the whole current head, not arbitrary historical prefixes. Keep the checkpoint elsewhere before handing a ledger to someone else.

IT: Le sequenze devono partire da 1 senza salti, gli hash precedenti devono coincidere e ogni hash viene ricalcolato. Chiavi univoche e transazioni impediscono importazioni concorrenti doppie. Una decisione autorizzata senza consumo/esito è `pending_runs`; un esito ignoto può comportare addebiti senza consumo disponibile. Il checkpoint corrisponde alla testa attuale, non a prefissi storici arbitrari. Salvalo altrove prima di consegnare il registro.
