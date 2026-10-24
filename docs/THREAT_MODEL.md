# Threat model / Modello di minaccia

EN: Intended for one trusted local developer who wants minimized accounting and detection of accidental edits. Trust the local account, Python installation, filesystem permissions, explicitly chosen policy/rates and OS TLS/proxy configuration. The app does not provide OS confinement, multi-user authorization, remote collection, encryption, signed attestations or compliance certification.

IT: Destinato a uno sviluppatore locale fidato che desidera contabilità minimizzata e rilevazione di modifiche accidentali. Si considerano fidati account locale, Python, permessi del filesystem, policy/tariffe scelte e configurazione TLS/proxy del sistema. Non offre isolamento OS, autorizzazione multiutente, raccolta remota, cifratura, attestazioni firmate o certificazioni di conformità.

| Concern / Rischio | Alpha behavior / Comportamento alfa | Limit / Limite |
|---|---|---|
| Prompt/key leakage / Perdita prompt/chiavi | Allowlist usage metadata; discard raw content and exceptions / Solo metadati, scarto contenuti | Prompt/key exist in process memory and provider request / In memoria e richiesta provider |
| Unapproved request / Chiamata non approvata | Default deny, exact model and output limit before network / Controllo prima della rete | Other programs can bypass adapter; no monetary cap / Altri programmi aggirano, nessun tetto monetario |
| Content in imported JSON / Contenuti JSON importato | Ignore non-accounting fields / Scarto campi non contabili | Original input and redirection targets remain user controlled / Input originali e destinazioni sono dell'utente |
| Misleading bill / Fattura fuorviante | Rates snapshot, separate sources, unpriced/unknown counts / Tariffe e fonti esplicite | User rates and imported data may be false; no reconciliation / Possono essere errati; nessuna riconciliazione |
| Database edits / Modifica database | Verified SHA-256 chain and exact schema guards / Catena verificata e schema | Full rewrite/tail deletion needs external trusted head; local owner can forge / Serve testa esterna fidata |
| Duplicate imports / Duplicati | Hashed response ID uniqueness, transaction / Univocità e transazione | New fabricated ID is a different assertion / ID inventati restano nuove dichiarazioni |
| Network ambiguity / Ambiguità rete | One attempt, bounded response, fixed endpoint, no redirects / Un tentativo, risposta limitata | Timeout may occur after billing; no automatic retry / Timeout possibile dopo addebito |
| Account compromise / Account compromesso | OS permissions only / Solo permessi OS | Metadata plaintext; same-user processes can access it / Metadati in chiaro e accessibili allo stesso utente |

EN: Public model IDs and rate dates remain readable metadata. Model syntax excludes arbitrary punctuation and API-key prefixes, but this is not general PII detection; choose public model identifiers. SHA-256 of an ID is pseudonymous correlation, not anonymization. Never add user names or secrets as model IDs. Verification protects stored accounting consistency, not the truth of a provider claim. A malicious local account can fabricate a valid chain and a replacement checkpoint. Back up the closed database and keep its trusted head separately.

IT: ID pubblici dei modelli e date tariffa restano leggibili. La sintassi esclude punteggiatura arbitraria e prefissi delle chiavi, ma non è un rilevatore generale di dati personali: usa identificatori pubblici dei modelli. Il digest è correlazione pseudonima, non anonimizzazione. Non usare nomi o segreti come modelli. La verifica protegge la coerenza del registro, non la verità delle dichiarazioni. Un account locale ostile può fabbricare catena e checkpoint sostitutivi. Esegui backup del database chiuso e conserva separatamente la testa fidata.

EN: The adapter sets `store=false`; it does not promise zero provider retention. Consult the provider's [official data controls](https://developers.openai.com/api/docs/guides/your-data) for the specific account/service. Automatic environment proxies remain OS/user configuration. API requests may incur charges; offline demo and tests do not.

IT: L'adapter imposta `store=false`; non promette conservazione zero dal provider. Consulta i [controlli ufficiali](https://developers.openai.com/api/docs/guides/your-data) per account e servizio. I proxy d'ambiente restano configurazione dell'utente/sistema. Le richieste API possono essere addebitate; demo e test offline no.

## Beta maintenance / Manutenzione beta

EN: Strict bounded JSON/JSONL and HTTP decoding reject duplicate keys, nonfinite numbers including exponent overflow, invalid UTF-8 and excessive nesting. Batch records validate before writing and duplicate conflicts roll back together. Report filters never skip verification of hidden events. Read-only connections reduce accidental writes, not access by other local processes.

IT: Parsing limitato e rigoroso JSON/JSONL e HTTP: rifiuto di chiavi duplicate, numeri non finiti incluso overflow, UTF-8 invalido e profondità eccessiva. Validazione prima della scrittura batch e rollback sui duplicati. I filtri verificano anche eventi nascosti. Connessioni di sola lettura riducono scritture accidentali, non l'accesso di altri processi.

EN: Unsigned prefix checkpoints must be kept separately and protected against replacement; they do not authenticate provider data. Backup refuses existing paths, copies a consistent verified SQLite snapshot and verifies the copy. Failure removes only the output created by that attempt. The same-user account and output custody during operations remain trusted; malicious filesystem replacement is outside this boundary. Backups retain plaintext metadata. No destructive restore or cross-host recovery guarantee. Keep real checkpoints/backups out of Git.

IT: Checkpoint di prefisso non firmati, da conservare separatamente e proteggere da sostituzione; non autenticano i dati provider. Backup senza sovrascrittura, snapshot coerente verificato e controllo della copia. In caso di errore viene rimosso solo l'output creato dal tentativo. Account e custodia dei file durante le operazioni restano fidati; sostituzioni ostili nel filesystem fuori perimetro. Backup con metadati in chiaro. Nessun ripristino distruttivo o garanzia fra host. Checkpoint/backup reali fuori da Git.
