# Architecture / Architettura

EN: A local process reads input, validates it, records a decision before provider contact, normalizes usage and appends a hashed event. Verified reports are reconstructed from immutable event payloads. No background service, server, telemetry or auto-updater exists.

IT: Un processo locale legge e valida gli input, registra la decisione prima di contattare il provider, normalizza i consumi e aggiunge un evento con hash. I report verificati vengono ricostruiti dai payload degli eventi. Nessun servizio in background, server, telemetria o aggiornamento automatico.

```mermaid
flowchart LR
  CLI[CLI / Python API] --> Domain[Usage, rates, policy]
  CLI --> Collector[Collector]
  Collector --> Ledger[SQLite hash chain]
  Collector -->|Only after durable allow| HTTP[OpenAI HTTPS]
  HTTP -->|Usage only; content dropped| Collector
  Ledger --> Verify[Verify + report]
```

| Module / Modulo | Responsibility / Responsabilità | Extension seam / Punto di estensione |
|---|---|---|
| `domain.py` | Strict schema, integer usage, Decimal cost, policy / Schema, consumi, costo, policy | Add a versioned normalization contract / Aggiungere contratto versionato |
| `storage.py` | Transactional append, schema checks, chain verification / Append, schema, verifica | Explicit migration required / Migrazione esplicita |
| `provider.py` | Bounded single HTTPS request / Singola richiesta limitata | Inject transport for tests / Transport sostituibile nei test |
| `service.py` | Decisions, collection, source-separated totals / Decisioni, raccolta, totali separati | Collector accepts normalized provider response / Contratto collettore |
| `cli.py` | Bounded files/stdin, JSON or Markdown output / File e stdin limitati, output | Thin command layer / Livello comandi sottile |

EN: Start from the specification and implementation plan under `docs/superpowers/`. For another provider first define trustworthy counter semantics, missing-usage behavior, cache accounting and identifier minimization; add failing tests before an adapter. Do not silently treat arbitrary OpenAI-compatible APIs as identical. For TokenWatch/OpenAgentOS, design an explicit run correlation and permission-evidence adapter before importing their logs; their READMEs were inspected, but no integration or runtime interoperability was tested.

IT: Parti da specifica e piano sotto `docs/superpowers/`. Per un altro provider definisci prima significato dei contatori, gestione del consumo assente, cache e minimizzazione degli identificatori; aggiungi test prima dell'adapter. Non trattare automaticamente tutte le API compatibili OpenAI come identiche. Per TokenWatch/OpenAgentOS progetta correlazione delle esecuzioni ed evidenza dei permessi prima di importare log; i README sono stati esaminati, ma integrazione e interoperabilità non sono state provate.

EN: Each append currently verifies the entire chain inside a write transaction. This deliberately favors a small auditable alpha over throughput; very large ledgers have O(n) append/read cost and no supported rotation/migration yet. SQLite connections close after each operation. Use one database per pilot/project and keep private backups outside Git. Default location follows the working directory, not the package installation directory.

IT: Ogni append verifica l'intera catena nella transazione di scrittura. L'alfa privilegia verificabilità e dimensioni contenute rispetto al throughput; registri grandi hanno costo O(n) per append/lettura e non dispongono ancora di rotazione/migrazione. Le connessioni si chiudono dopo ogni operazione. Usa un database per prova/progetto e conserva backup privati fuori da Git. Il percorso predefinito segue la cartella corrente, non quella d'installazione.
