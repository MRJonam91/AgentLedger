# 1.0 verification / Verifiche 1.0

Release verification date / Data verifiche release: 2026-10-25. Package / Pacchetto: 1.0.0. Published tag / Tag pubblicato: v1.0.0. Design began / Progettazione avviata: 2026-10-24.

EN: Stable refers to the documented local CLI and v1 storage contract. Evidence is recorded after execution; it does not imply independent security certification or provider billing validation. / IT: Stabile riguarda CLI locale e contratto storage v1; evidenze registrate dopo le prove, senza certificazione di sicurezza o validazione della fatturazione.

- Baseline: all **72 beta tests** passed on Windows/Python 3.14.3 before changes. New regressions first failed on missing init/export, invalid requests creating a ledger and JSON wrong-type handling.
- Initial 1.0 suite: **85 tests passed**, including actual loopback HTTP contract/redirect/strict decoding/bounded response and separate-process concurrent batch dedupe. Mypy passed eight runtime modules; project check found zero issues, core **803 physical lines** at this stage.
- Windows sandbox blocks loopback socket connections with WinError 10013; HTTP tests were rerun with local-network access. They use only a local synthetic server, never the paid provider. / Il sandbox blocca il loopback; prove ripetute con accesso locale e server sintetico.
- No paid provider smoke, external pilot, invoice reconciliation, third-party security audit or cross-host disaster-recovery certification. These remain explicit validation activities. / Non eseguiti: provider a pagamento, pilota esterno, riconciliazione, audit esterno, certificazione recupero fra host.

## Release checks / Controlli release

- Final local suite / Suite finale locale: **87 tests passed**, Windows/Python 3.14.3. The four loopback tests require local-network permission in this sandbox; the full suite passed when granted access to the synthetic loopback server. No paid-provider traffic. / Quattro prove richiedono permesso di rete locale nel sandbox; suite completa superata sul server sintetico, nessun traffico provider a pagamento.
- Independent review approved the local CLI scope. Earlier findings on preserving empty/foreign existing files during init and rejecting unpaired Unicode surrogates were fixed with regressions. Reviewer independently ran six CLI and three I/O tests, all passing; no unresolved material findings. / Revisione approvata; corretti init su file esistenti e Unicode con regressioni, nove test mirati rieseguiti senza rilievi materiali.
- `python -m mypy --check-untyped-defs agentledger`: passed eight runtime files. Project check: **811 physical core lines**, **70 public source/documentation files**, zero findings in its defined scope. / Controlli statici su otto moduli superati, core 811 righe fisiche e 70 file pubblici.
- Full reachable history and candidate publication paths inspected before committing: five existing commits, noreply authorship, zero findings in the configured secret/email/local-path scan. Private operational material is excluded from the public distribution contract. / Cronologia e percorsi controllati prima del commit; identità noreply e nessun rilievo nel perimetro dichiarato. Materiale operativo privato escluso dalla distribuzione pubblica.
- Architecture, compatibility, current-release pointers, security/support policy, development plan and EN/IT READMEs aligned with stable 1.0; historical alpha/beta evidence retained. / Architettura, compatibilità, riferimenti correnti, sicurezza/supporto, piano e README allineati; evidenze storiche conservate.

- Built wheel and source archive with the documented build tooling. Wheel: **16 entries**, required LICENSE/NOTICE/THIRD_PARTY_NOTICES included, no runtime dependency declarations. Archive inspection found zero configured-scan findings and empty owner/group metadata; public source paths only. / Wheel e sorgenti costruiti e controllati: licenze incluse, nessuna dipendenza runtime, percorsi pubblici e metadati proprietario/gruppo vuoti.
- Installed the wheel with `--no-deps --no-index` into a new venv and exercised it outside the source tree. Version **1.0.0**, **8 events**, **2 imported** records and **synthetic USD 0.0114**; idempotent initialization, exclusive JSON/Markdown exports, prefix verification and backup all passed. Existing destinations and initialized data stayed byte-identical; an invalid request created no ledger directory. / Installazione pulita e flusso completo verificati, destinazioni preservate e nessun registro per richieste invalide.
- Extracted-source project check inspected **72 distributed files** with zero findings, and the full extracted-source suite passed **87 tests**. / Controllati 72 file distribuiti nell'archivio estratto e superati 87 test dai sorgenti.

- Final archive comparison against the release commit matched **all 70 tracked source files** and **all eight runtime modules**; only newline normalization was allowed. The exact final wheel was reinstalled without dependencies and repeated the complete installed-package workflow successfully. / Confrontati tutti i 70 file tracciati e otto moduli con il commit; ammessa solo normalizzazione dei fine riga. Wheel finale reinstallato e flusso completo ripetuto.

## Published stable release / Release stabile pubblicata

- [Repository](https://github.com/MRJonam91/AgentLedger) verified **public**, default branch `main`. Release code commit: **a6574c4b25549ec0eaa03e19fd75ce509a4a03ad**. Integrated by fast-forward with no history rewriting. / Repository pubblica, integrazione fast-forward senza riscrittura della cronologia.
- [Release-branch CI 40183375561](https://github.com/MRJonam91/AgentLedger/actions/runs/40183375561) and [main CI 40183558311](https://github.com/MRJonam91/AgentLedger/actions/runs/40183558311) succeeded on that exact revision. Each run passed all four Windows/Linux and Python 3.11/3.14 jobs, including tests, static/project/history checks, build/install and installed init/export/checkpoint/backup workflow. / Entrambe le CI superate sulla revisione esatta, quattro combinazioni ciascuna.
- [v1.0.0](https://github.com/MRJonam91/AgentLedger/releases/tag/v1.0.0) is the latest stable GitHub release, **not a draft or prerelease**. Annotated unsigned tag resolves to the verified code commit; all three published asset digests match local files. / Release stabile più recente, non bozza o prerelease; tag annotato non firmato e tre digest corrispondenti.
- Complete prepublication history check covered six reachable commits after candidate creation with zero findings in its declared scope. Current and historical public source paths were inspected; local operational material remains outside the distribution. / Verificati sei commit raggiungibili e percorsi pubblici correnti/storici, senza rilievi nel perimetro dichiarato.
- The post-release default-branch commit only completes documentation, checklists and release links. Runtime, tag and release artefacts remain unchanged. / Il commit successivo completa solo documenti, checklist e link; runtime, tag e artefatti invariati.

| Asset | SHA-256 |
|---|---|
| `agentledger_local-1.0.0-py3-none-any.whl` | `5458eb0a3b66c5946a02b6fd38eef442ab4d84037ab2fe231525ef3bc88be0c9` |
| `agentledger_local-1.0.0.tar.gz` | `ef20e4f9e8bc11acaf06d28d1275a6a7ce6d3b86186b75775ac58d1205381c7b` |
| `SHA256SUMS.txt` | `325bd48f512e1bff7f76e3b1a1520381e03de80913004c103c84364b4042b826` |
