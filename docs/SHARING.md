# Try a local accounting trail / Prova una cronologia locale

## English

AgentLedger records an agent's permission decisions and token usage in a local SQLite ledger, calculates costs from explicit rate cards and exports a verifiable history. Try `python -m agentledger demo`, then `report --format markdown` and `verify` from a checkout. The demo needs Python 3.11+, no API key and no runtime dependencies.

Its USD 0.0057 subtotal is synthetic. It demonstrates a calculation and an allow/deny trail; it is not a bill, observed saving or proof that another agent cannot bypass the adapter. A separately trusted checkpoint is needed to detect historical replacement or tail deletion. There is no monetary budget cap.

Useful feedback: could you understand the report and its distinction between demo, imported and live usage? For an import problem, send a minimal synthetic response and expected counters through [Support](../SUPPORT.md). Keep keys, prompts, response text and real ledger databases private. If useful, a star is a way to save the repository; a reproducible report helps improve it.

## Italiano

AgentLedger registra decisioni di autorizzazione e consumi di token in SQLite locale, calcola i costi con tariffe esplicite ed esporta una cronologia verificabile. Da una copia del progetto prova `python -m agentledger demo`, poi `report --format markdown` e `verify`. Servono Python 3.11+, nessuna chiave API e nessuna dipendenza runtime.

USD 0,0057 è un totale sintetico. Dimostra un calcolo e una sequenza autorizza/nega; non è una fattura, un risparmio osservato o la prova che altri agenti non possano aggirare l'adapter. Per rilevare sostituzione della cronologia o taglio della coda serve un checkpoint conservato separatamente in un luogo fidato. Non è presente un limite monetario al budget.

Feedback utile: il report distingue chiaramente demo, dati importati e chiamate reali? Per problemi di import usa una risposta sintetica minima e i contatori attesi tramite [Supporto](../SUPPORT.md). Non condividere chiavi, prompt, risposte testuali o database reali. Se utile, una stella permette di ritrovare la repository; un caso riproducibile aiuta a migliorarla.

[Repository](https://github.com/MRJonam91/AgentLedger) · [Quick start / Avvio rapido](../README.md#try-it-without-an-account). Reusable copy; no external distribution or user adoption is implied. / Testo riutilizzabile; non implica pubblicazioni esterne o adozione.
