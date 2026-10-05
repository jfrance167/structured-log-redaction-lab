# Structured Log Redaction Lab

Verified local milestone, October 5, 2026. Coordinator-approved stages 1–4 complete;
authoritative records are structured-log-redaction-lab/STATE.md, REVIEW.md and
docs/verification/final-results.json. No independent audit or hosted result.

Synthetic pre-sink projection builds fresh events from fixed validated fields.
No real logs/secrets/private data, logger integration or existing SIEM change.
Closed CLI errors do not echo argv, raw JSON, keys, paths or exception text.
Nine lexical/decoder tests passed before projection: encoded-string/depth bounds,
UTF-8, slash parity/quotes/braces, escapes, scalars, numeric and duplicate policy.
Cardinality follows parsing; it is not a preallocation bound.

Frozen 16 paired cases/independent utility oracles preceded application code.
Baseline leaks 4/16 canary cases and masks benign values in 1/16 controls.
Minimization leaks zero listed forms in 32 outcomes, preserves 28 events/28
failures/700 ms, rejects four invalid cases. This is finite synthetic coverage,
not universal privacy, PII cleanup or production detector accuracy.

Final: 31 tests PASS normally/optimized on Windows CPython 3.13.7; Bandit zero
findings/errors without exclusions; syntax/local workflow policy pass. A raw-copy
mutation failed the field/leakage oracle and source restored exactly. ECC
self-review reproduced dual closed sinks exit 120, fixed buffers to preserve
exit 2; decoder exception contexts detached, not caller/traceback memory erased.

Reusable minimize(bytes) API, closed-error CLI and fresh frozen-demo generator
are documented in README. Nontransactional output, allowed metadata information,
regular-file races/blocking I/O and no hard RSS/CPU boundary remain. Linux/other
runtimes, hosted CI/CodeQL/protections/security eligibility not verified. Prepared
immutable-pin workflows; dev dependency lacks transitive artifact hashes. No
publication/merge/deployment, remote inference, billing or shared-tool changes.

Research references: [Python JSON](https://docs.python.org/3/library/json.html),
[OWASP Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html),
[structlog](https://github.com/hynek/structlog),
[loggingredactor](https://github.com/armurox/loggingredactor), reviewed October 5.
Next: manual review before expanding schemas/adapters/evidence; no new scope
started. Related: [[Structured Logging Field Minimization]], [[Evidence Integrity]].
