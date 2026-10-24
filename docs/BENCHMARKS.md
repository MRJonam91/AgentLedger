# Batch benchmark / Benchmark batch

Run / Esegui: `python scripts/benchmark.py --records 200`.

EN: This offline script creates two temporary ledgers with the same synthetic metadata: one uses 200 individually committed appends, the other one atomic batch. Both fully verify historical hashes before writing; batching verifies historical events once per transaction and shares one SQLite commit. Output gives observed elapsed seconds and their ratio, not a universal throughput guarantee. Disk, OS, antivirus, journal conditions and record sizes affect results. The temporary ledgers are removed; no provider/model is contacted. Set TEMP/TMP to an existing checkout-local directory when required by a restricted Windows sandbox.

IT: Lo script offline crea due registri temporanei con gli stessi metadati sintetici: uno usa 200 append con commit singoli, l'altro un batch atomico. Entrambi verificano gli hash prima di scrivere; il batch verifica la storia una volta per transazione e condivide un commit SQLite. L'output riporta secondi osservati e rapporto, non garantisce throughput universale. Disco, OS, antivirus, journaling e dimensione record influiscono. I registri temporanei vengono rimossi; nessun provider/modello viene contattato. Nei sandbox Windows restrittivi imposta TEMP/TMP su una cartella già esistente nel checkout.

Release observations are recorded after running the script in `docs/VERIFICATION_BETA.md`. / Le misure della release vengono registrate dopo l'esecuzione in `docs/VERIFICATION_BETA.md`.
