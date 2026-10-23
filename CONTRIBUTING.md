# Contributing / Contribuire

EN: Open an issue with the problem, expected behavior and a minimal **synthetic** reproduction. Agree scope/design before changing interfaces or event schemas. Add a failing behavior test, implement it, then run `python -m unittest discover -s tests -v` and `python scripts/check_project.py`. Keep both READMEs synchronized, runtime standard-library-only and core below 1,500 physical lines. See AGENTS.md and architecture/threat model. Never upload actual ledgers, prompts, keys, private paths or raw error bodies.

IT: Apri una issue con problema, risultato atteso e riproduzione **sintetica** minima. Concorda scope/design prima di cambiare interfacce o schema. Aggiungi test del comportamento, implementalo e lancia `python -m unittest discover -s tests -v` e `python scripts/check_project.py`. Mantieni README sincronizzati, esecuzione solo standard library e core sotto 1.500 righe fisiche. Vedi AGENTS.md, architettura e modello di minaccia. Mai caricare registri reali, prompt, chiavi, percorsi privati o corpi di errore grezzi.

EN: By contributing you confirm you have the right to submit the material and license it under GPL-3.0-or-later. Sign off commits with `git commit -s`, declaring the [Developer Certificate of Origin](https://developercertificate.org/). Use a public/noreply identity suitable for permanent Git history. No CLA is required.

IT: Contribuendo dichiari di avere il diritto di inviare il materiale e distribuirlo sotto GPL-3.0-or-later. Aggiungi `git commit -s` dichiarando il [Developer Certificate of Origin](https://developercertificate.org/). Usa identità pubblica/noreply adatta alla cronologia permanente. Nessun CLA richiesto.
