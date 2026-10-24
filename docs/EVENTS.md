# Event contract v1 / Contratto eventi v1

Beta additions / Aggiunte beta: see the checkpoint/report extension below; the original SQLite/hash contract is unchanged. / Vedi l'estensione sotto; contratto SQLite/hash originale invariato.

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

EN: Sequences must be contiguous from 1, previous hashes must match and each hash must recompute. Unique response keys and SQLite transactions prevent concurrent double imports. An allowed decision without usage/outcome is `pending_runs`; an unknown outcome represents possible provider charges with unavailable usage. `--expected-head` matches the whole current head; beta checkpoint files can instead anchor an earlier prefix. Keep the checkpoint elsewhere before handing a ledger to someone else.

IT: Le sequenze devono partire da 1 senza salti, gli hash precedenti devono coincidere e ogni hash viene ricalcolato. Chiavi univoche e transazioni impediscono importazioni concorrenti doppie. Una decisione autorizzata senza consumo/esito è `pending_runs`; un esito ignoto può comportare addebiti senza consumo disponibile. `--expected-head` confronta la testa attuale; i file checkpoint beta possono invece ancorare un prefisso precedente. Salvalo altrove prima di consegnare il registro.

## Beta checkpoint files / File checkpoint beta

EN: SQLite and event hash schema remain v1. Reports add `selected_event_count` and `filters`; `event_count`/`checkpoint` always describe the full verified ledger. Filters select whole runs using returned usage model, otherwise requested model. `--summary` omits `events` without changing totals. Batch imports retain individual usage/run events in one transaction; no raw batch payload is stored. Public imports always carry `imported`; a duplicate live response gets a terminal unknown outcome.

IT: SQLite e hash eventi restano v1. I report aggiungono `selected_event_count` e `filters`; `event_count`/`checkpoint` descrivono sempre il registro completo verificato. Filtri su esecuzioni intere con modello restituito o, se assente, richiesto. `--summary` omette `events` senza cambiare i totali. I batch mantengono eventi consumo/esecuzione individuali in una transazione, senza payload grezzo. Import sempre `imported`; duplicati live con esito ignoto conclusivo.

```json
{"schema_version":1,"event_count":0,"checkpoint":"0000000000000000000000000000000000000000000000000000000000000000"}
```

EN: `checkpoint --output` creates a file with exactly these three fields (empty-ledger example). `verify --checkpoint FILE` verifies the saved prefix hash/count and permits valid appends; below-count truncation/different prefix fails. `--expected-head HASH` remains an exact current-head comparison. Flags are exclusive. Empty checkpoints attest no nonempty history. Checkpoints are unsigned and require separately trusted custody.

IT: `checkpoint --output` crea un file con esattamente questi tre campi (esempio vuoto). `verify --checkpoint FILE` verifica hash/numero del prefisso e accetta aggiunte valide; cancellazioni sotto il numero o prefisso diverso falliscono. `--expected-head HASH` resta il confronto esatto con la testa corrente. Opzioni esclusive. Checkpoint vuoti non attestano storia non vuota. Non sono firmati e richiedono custodia fidata separata.
