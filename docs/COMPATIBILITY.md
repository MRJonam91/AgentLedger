# Stable contract and upgrades / Contratto stabile e aggiornamenti

EN: 1.0 supports Python 3.11+ and one local account. The compatibility baseline is the alpha/beta SQLite v1 table/trigger layout, event JSON hash inputs, source labels and exact Decimal arithmetic. 1.0 opens those ledgers directly; no migration or hash rewrite is performed. Preserve the ledger directory when upgrading. Take a verified backup and a separately trusted checkpoint before changing installations.

IT: La 1.0 supporta Python 3.11+ e un account locale. La base di compatibilità è lo schema SQLite v1 alfa/beta, gli input JSON degli hash, le fonti e l'aritmetica Decimal esatta. I registri si aprono direttamente, senza migrazioni o riscrittura degli hash. Conserva la cartella dati durante l'aggiornamento. Prima di cambiare installazione crea backup verificato e checkpoint separato fidato.

```sh
agentledger backup before-upgrade.sqlite3
agentledger checkpoint --output before-upgrade.json
python -m pip install --upgrade ./agentledger_local-1.0.0-py3-none-any.whl
agentledger --version
agentledger verify --checkpoint before-upgrade.json
```

EN: Use new output names; no-overwrite is intentional. For a first installation use `agentledger init`, then import existing provider Responses JSON/JSONL or run the offline demo. `init` is idempotent and verifies existing history. The installed package and `python -m agentledger` expose the same commands. Paths remain relative to your working directory unless `--db` is explicit. The Python distribution name is `agentledger-local`, the module/command name is `agentledger`.

IT: Usa nomi nuovi: il rifiuto della sovrascrittura è intenzionale. Per la prima installazione usa `agentledger init`, poi importa JSON/JSONL Responses esistenti o prova la demo offline. `init` è idempotente e verifica la storia esistente. Pacchetto installato e `python -m agentledger` espongono gli stessi comandi. I percorsi seguono la cartella corrente salvo `--db` esplicito. Il pacchetto Python si chiama `agentledger-local`, modulo/comando `agentledger`.

| Interface / Interfaccia | Stable behavior / Comportamento stabile |
|---|---|
| Existing commands / Comandi esistenti | demo, imports, run, report, verify, checkpoint, backup retained / mantenuti |
| Added / Aggiunti | init, report --output |
| Stored records / Record persistiti | v1 unchanged; original alpha fixture covered / v1 invariato e fixture alfa verificata |
| Report JSON | Existing fields retained; optional file export gives a separate receipt / campi mantenuti, export con ricevuta separata |
| Errors / Errori | Fixed JSON on stderr, exit 2 local/input, 3 denied, 4 unknown/incomplete / codici fissi |
| Provider evidence / Evidenza provider | Demo synthetic, imports unverified, live applies only to this adapter / fonti distinte |

EN: 1.x changes preserve this documented contract or add explicit opt-in capabilities. An incompatible schema/CLI change requires a major version and an explicit migration/export design; no silent destructive update. Live provider acceptance, invoice reconciliation, cross-host recovery and multi-user security are separate validations, not consequences of the version number. Neither GitHub releases nor checksums authenticate imported provider counters.

IT: Le versioni 1.x conservano il contratto documentato o aggiungono capacità esplicite. Modifiche incompatibili a schema/CLI richiedono versione maggiore e progetto di migrazione/export, senza aggiornamenti distruttivi silenziosi. Accettazione provider, riconciliazione fatture, recupero fra host e sicurezza multiutente sono verifiche separate, non conseguenze del numero di versione. Release e checksum non autenticano i consumi importati.
