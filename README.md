# AgentLedger

Local agent audit ledger: permissions, token usage and reproducible cost calculations.

[Italiano](README.it.md) · [Alpha release](https://github.com/MRJonam91/AgentLedger/releases) · [Architecture](docs/ARCHITECTURE.md)

![Offline trial: allow, account, deny, verify](docs/assets/demo.svg)

**0.1.0a1 — usable local alpha.** Python 3.11+, Windows/Linux/macOS, no runtime dependencies. CLI only. External pilot validation and a paid live-provider smoke test remain unperformed; see [verification](docs/VERIFICATION.md).

## Try it without an account

From a checkout:

```sh
python -m agentledger demo
python -m agentledger report --format markdown
python -m agentledger verify
```

The offline demo records one allowed request, 1,000 input tokens (200 cached), 500 output tokens and one denied request. **USD 0.0057 is a synthetic calculation using synthetic rates; no request is sent and no money is spent.** Re-running the demo appends another trial. Data stays in `.agentledger/ledger.sqlite3`, relative to your current directory.

Install the CLI from source with `python -m pip install .`, or download the wheel from the release and run `python -m pip install ./agentledger_local-0.1.0a1-py3-none-any.whl`. The installed command is `agentledger`. The package is distributed through GitHub Releases, not PyPI.

## Collect a real response

```sh
python -m agentledger --db .agentledger/imports.sqlite3 import-response examples/response.json --rates examples/rates.demo.json
python -m agentledger --db .agentledger/imports.sqlite3 report
```

Replace the fixture with a locally saved **OpenAI Responses API** object. The example is synthetic. The collector retains only token counters, model/status and a SHA-256 digest of the response ID. It drops message content, prompts, headers and extra fields. Imports are labeled `imported`: their origin and truth are not authenticated. Duplicate response IDs are rejected within the database; re-importing cannot change an existing rate snapshot. Original input files remain your responsibility.

Without `--rates`, usage is recorded as **unpriced**. Adapt the example rate card to the **exact returned model** and your applicable USD text rates per million tokens; record an effective date. A model mismatch is unpriced. Cards are user assertions, not independently verified price feeds. Each priced event retains its card and hash. Cached input is not counted twice:

```text
USD = ((input - cached) × input_rate + cached × cached_rate + output × output_rate) / 1,000,000
```

Reports separate `demo`, `imported` and `live`; amounts are **priced subtotals**, excluding unpriced usage, unknown outcomes, pending calls, tool/image/audio fees and taxes. Provider invoice reconciliation is outside this alpha.

## Run the minimal agent

`run` sends a single text generation request to OpenAI. It reads a UTF-8 prompt from stdin and `OPENAI_API_KEY` from the environment. It emits accounting and discards generated text. There is no general tool execution or autonomous loop.

Create a private `policy.json` based on `examples/policy.demo.json`: replace `demo-model` with an available model ID you have chosen and set the output-token ceiling. Configure matching real rates if desired. Then, with a key already in your environment:

```sh
python -m agentledger run --model YOUR_MODEL --policy policy.json --max-output-tokens 512 < prompt.txt
```

PowerShell 7: `Get-Content -Raw -Encoding utf8 prompt.txt | python -m agentledger run --model YOUR_MODEL --policy policy.json`. Set `$OutputEncoding = [System.Text.UTF8Encoding]::new()` when using older PowerShell. Keep keys out of shell history and the repository. A live request may incur provider charges. There is no monetary budget cap.

Omitting the policy denies the request. The exact model and requested output limit must pass before network access; the decision is durably logged first. There are no automatic retries or redirects. Failed/malformed responses produce `unknown`, not a zero-cost result; interrupted calls appear as pending. The adapter uses `store=false`; provider-side retention is separate from this local ledger ([official data controls](https://developers.openai.com/api/docs/guides/your-data)).

## Export and verify

```sh
python -m agentledger report > report.json
python -m agentledger report --format markdown > report.md
python -m agentledger verify --expected-head SAVED_64_CHARACTER_HASH
```

Save the report's `checkpoint` separately. The last command requires an unchanged ledger head; appending legitimate events also changes the head. A hash chain detects edits to stored events; a separately trusted checkpoint detects tail deletion or replacement. **Without an external checkpoint, rewriting the whole chain or deleting the tail may pass verification.** The database is plaintext, protected by your filesystem/account permissions, not encrypted or an OS sandbox. Other agents can bypass this adapter. See [threat model](docs/THREAT_MODEL.md).

Inputs: JSON ≤ 2 MiB, prompt ≤ 64 KiB, one bounded response ≤ 2 MiB, 60-second HTTP timeout. Only text Responses usage with completed/incomplete status is supported; missing usage and cache-write billing are rejected. Read commands refuse missing/corrupt databases. Exit codes: `0` completed, `2` input/local failure or request not sent, `3` policy deny, `4` incomplete/unknown provider outcome. Errors are JSON on stderr; successful results are JSON on stdout unless Markdown is selected. Argument errors return the fixed JSON code `invalid_arguments_use_help`.

## Develop and extend

```sh
python -m unittest discover -s tests -v
python scripts/check_project.py
python -m pip install build mypy
python -m mypy --check-untyped-defs agentledger
python -m build
```

Tests create isolated temporary databases and never contact a paid provider. In restricted Windows sandboxes set `TEMP`/`TMP` to an existing checkout-local directory first. [Design and plan](docs/superpowers/specs/2026-10-23-alpha-design.md), [architecture](docs/ARCHITECTURE.md), [schema](docs/EVENTS.md), [roadmap](docs/ROADMAP.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md) and [security](SECURITY.md) establish the next analysis/design/implementation steps. TokenWatch/OpenAgentOS integration and a dashboard are future work, not current features.

## License and attribution

Copyright 2026 MRJonam91. [GPL-3.0-or-later](LICENSE), including original docs and SVG. [Licensing](LICENSING.md), [notices](NOTICE), [third-party inventory](THIRD_PARTY_NOTICES.md). Project names and third-party trademarks are not granted by the software license; no OpenAI affiliation is implied. The original [seed](SEED.md) records idea provenance.

## Support the project

If useful, support maintenance through the repository Sponsor button, [GitHub Sponsors](https://github.com/sponsors/MRJonam91), [Ko-fi](https://ko-fi.com/mrjonam), [Buy Me a Coffee](https://buymeacoffee.com/mrjonam) or [PayPal](https://paypal.me/manorollo). Support is voluntary and grants no additional license or rights.
