# Execution record / Registro esecuzione

2026-10-23: Seed and adjacent project READMEs inspected. Selected independent local collector; TokenWatch/OpenAgentOS bridges deferred. User authorized definition, implementation and publication together. New seed directory contains no existing Git history; work proceeds in the explicitly selected workspace, without a redundant linked checkout.

Ruling: GPL-3.0-or-later for the complete app follows the current owner standard; older seed-kit license matrix is superseded with an explicit decision in the design. Original SVG and clean noreply history provide visible provenance.

Ruling: no paid provider smoke call during development. Test the real HTTP request contract through the transport seam; disclose live API validation as unperformed.

Preflight: normalized dictionaries are the domain/service seam; storage accepts normalized event records; CLI delegates decisions and totals to service. Rate card values are decimal strings; hash inputs use sorted compact UTF-8 JSON. No runtime third-party dependencies.

Task 1: test_domain initially failed because agentledger did not exist; implemented domain, then 9 tests passed.
Task 2: test_storage initially failed because storage module did not exist. Windows sandbox TEMP was inaccessible; moving TEMP/TMP into ignored checkout-local .test-output/tmp resolved that environmental failure. Test-owned SQLite connections needed explicit closing on Windows; corrected test cleanup. Then 8 storage tests passed, including real concurrent appends and duplicate imports.
Task 3: test_service initially failed because collector/transport modules did not exist; implemented and 9 tests passed.
Task 4: seven CLI tests failed on missing module entrypoint; implemented commands/examples, then full suite passed 33 tests.

Independent review: Important schema validation issue and Minor argparse JSON/privacy issue reproduced. Two storage regression tests failed (version=1 schema without guards and guard removed after open); one argument-error regression failed JSON parsing. Added actual schema validation before open/read/append and fixed JSON argument errors. Restored test guards after intentional tampering so chain/checkpoint tests still exercise hash verification rather than merely schema refusal. All 36 tests then passed. Publication scanner has two additional synthetic tests.

Ruling: exact SQLite schema is the alpha version contract; unexpected indexes/tables/triggers are rejected rather than silently treated as migrations. Cost if wrong: a user must retain a private original and request explicit migration support.

Second review: a user trigger named sqlitex_ignore bypassed SQL LIKE filtering of SQLite internal names and could suppress a decision insert before provider contact. Storage/service regressions first failed; fixed literal prefix filtering with GLOB plus inserted row-count verification. Full suite: 40 passed. Final independent reviewer approved local-alpha scope, independently ran 40 tests and found no remaining material issues. Runtime summary has explicit TypedDict fields after mypy identified overly narrow inferred mixed-dictionary types; static checks then passed seven source files.

Wheel/sdist built and inspected; clean wheel installed without dependencies, outside-source entrypoint demo/report/verify succeeded with expected three events and synthetic USD 0.0057. No real paid provider call performed.

Final packaging check found that scanning an extracted source archive inside a parent Git checkout could inspect zero files. Added a failing source-archive regression, fixed Git-root detection and allowed generated source metadata. Extracted-source scan: 50 files, zero errors. Final full suite: 41 tests passed; static check passed seven source files; core is 563 physical lines. GitHub repository created private before publication.

Publication complete: all four CI jobs passed at initial code commit and exact release-target commit d336c86. Made repository public, enabled private vulnerability reporting, pushed annotated unsigned v0.1.0-alpha.1 tag, published prerelease with wheel/sdist/SHA256SUMS. API digests match local artefacts. Final source archive contains 51 checked files after adding Git attributes; no credential/path findings or account owner metadata in artefacts. Post-release commit only records completed evidence and checklist, so CI is skipped for that documentation-only update.
