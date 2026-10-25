# AgentLedger alpha design / Progetto alfa

## Intent / Intento

IT: Dal seed a una prima versione locale utilizzabile da uno sviluppatore: ricostruire autorizzazioni, consumo e costo calcolato di un singolo agente OpenAI senza registrare prompt, risposte o chiavi. L'utente ha richiesto esplicitamente definizione, implementazione, creazione repository e pubblicazione nella stessa sessione. Utente pilota assunto: sviluppatore locale; validazione con utilizzatori esterni ancora da fare.

EN: Turn the seed into a usable local tool for a developer: reconstruct permissions, usage and calculated cost for one OpenAI agent without recording prompts, responses or keys. The user explicitly requested definition, implementation, repository creation and publication in this session. Assumed pilot: a local developer; external user validation remains future work.

## Alternatives / Alternative

1. **Selected: local CLI + SQLite.** No runtime dependencies, portable records and repeatable offline trial; no graphical dashboard.
2. Extend TokenWatch: useful for proxy-level traffic, but run/decision accounting has a different boundary. Future bridge through normalized records.
3. Extend OpenAgentOS: useful for runtime-wide policy; couples this first collector to a broader agent runtime. Future read-only adapter.

## Contract / Contratto

- Python 3.11+; standard library only at runtime. One local user, no listening server or telemetry.
- Commands: `demo`, `import-response`, `run`, `report`, `verify`. JSON output is machine-readable; reports also support Markdown.
- `demo` exercises an allowed generation, a denied generation and synthetic usage with synthetic rates, offline.
- `import-response` reads one bounded OpenAI Responses JSON, extracts only usage, model and a SHA-256 digest of response ID. It records **imported**, unverified provider data and refuses duplicates atomically. Input/output text, headers, paths and arbitrary extra properties never enter storage.
- `run` is a one-step text agent. Prompt arrives on stdin (maximum 64 KiB); API key arrives via `OPENAI_API_KEY`. It posts to the fixed HTTPS OpenAI Responses endpoint with `store=false`, no tools, no redirects or automatic retries. Live output is deliberately discarded. The CLI emits accounting only.
- Default deny. A strict versioned JSON policy must allow the exact model and requested output-token limit before any network call. Policy snapshot is included in the decision record. This governs this adapter only, not unrelated agents or OS processes.
- Provider usage is validated as bounded nonnegative integers; cached input is a subset of input and total equals input plus output. Unsupported cache-write billing fails closed. Completed and incomplete responses with valid usage can be accounted for; failures/missing usage are explicitly unknown, never zero cost.
- Rates are optional, user supplied, exact-model USD text-token rates per million: uncached input, cached input and output. Decimal arithmetic, snapshot, effective date and hash make the calculation repeatable. No bundled market prices, invoice claims, monetary hard cap, automatic price fetch, paid smoke test, images/audio/tool fees or billing reconciliation.
- Formula: `((input-cached)*input_rate + cached*cached_rate + output*output_rate)/1000000`. A missing or mismatching rate card produces unpriced usage. Demo/import/live sources remain separate in reports.
- SQLite transaction serializes appends; schema is versioned. Events have monotonic sequence, UTC timestamp, run UUID, kind, allowlisted data, previous hash and SHA-256 hash of canonical UTF-8 JSON. Accidental updates/deletes are blocked by triggers. Reports verify the chain before reading.
- `verify --expected-head HASH` checks against a separately saved checkpoint. Without a checkpoint a tail deletion, full rewrite or replaced database cannot be detected. SQLite is plaintext; metadata, token counts, timestamps and model identifiers are visible to the local account. No signature, external timestamp, sandbox or security certification.
- Local database path is explicit or `.agentledger/ledger.sqlite3`; generated data is ignored by Git. Read commands refuse a missing database rather than silently creating it. Schema mismatch and damaged chain fail closed.
- Export writes to stdout; redirection is controlled by the user. No provider content is exported. A report includes aggregate usage, priced/unpriced counts, unknown outcomes, decision totals, events and a checkpoint.

## Components / Componenti

`domain.py`: normalized usage, rate cards and policy validation. `storage.py`: transactional hash-chain ledger. `provider.py`: fixed-endpoint HTTP transport. `service.py`: decisions, collection and accounting. `cli.py`: input/output and commands. `__main__.py`: module entrypoint. Tests use real SQLite and a transport seam; no live paid calls.

## Success / Successo

From a clean checkout, run demo, inspect both policy outcomes and the exact synthetic USD calculation, restart and import a response, export JSON/Markdown, reject duplicate imports, verify a saved checkpoint, detect tampering, and prove denied/error paths do not leak payloads or contact the provider when denied. Build and install the release wheel in isolation, inspect shipped licensing, run Windows checks and GitHub CI before public release.

## Project foundation / Fondamenta

Bilingual README, architecture, threat model, roadmap, release evidence, contributing/security/support documents; compact AGENTS guidance and versioned design/plan for future changes. Preserve seed as historical provenance. New public repository uses noreply Git identity and clean history; inspect all reachable commits before publishing. Create private first, publish after checks.

Licensing decision: GPL-3.0-or-later for this complete local application, following the owner's current general repository standard. This explicitly supersedes the older seed kit's Apache/AGPL matrix for this repository. Documentation and original SVG demo are covered by the same license; no third-party creative assets. Auditable Git history and release checksums document provenance. CLI does not interrupt automation for sponsorship; support links are in help and documentation. A Python CLI uses pip/module entrypoints rather than the seed kit's frontend/npx template. No web hosting is necessary for this CLI release.
