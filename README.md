# Structured Log Redaction Lab

Learn what should reach a log sink by building fresh events from validated known
fields. Unknown fields, free-form messages and exceptions are dropped before
output. This is an **offline synthetic lab**, not a production PII-cleanup tool.
No real logs, credentials, network logger or existing SIEM changes are involved.

## Run

Tested on Windows CPython 3.13.7; no runtime third-party dependencies. From this
directory:

```powershell
py -3.13 -m log_minimizer --evaluate
py -3.13 scripts/make_demo.py demo-inputs
py -3.13 -m log_minimizer demo-inputs/password-canary.json
py -3.13 -m log_minimizer demo-inputs/service-canary.json
py -3.13 -m unittest discover -v
py -3.13 -O -m unittest discover -v
```

The demo helper requires a **fresh** destination; repeats refuse existing folders
and preserve their files. Inputs contain invented canaries deliberately. A later
fixture write error can leave a partial new directory; it never overwrites one.
The CLI emits only minimized events or aggregate evaluation, with errors on stderr.

Exit 0: minimized batch/evaluation pass. Exit 1: frozen evaluation mismatch.
Exit 2: fixed error code, including parse, schema, argument, internal and I/O errors.
The service-canary example rejects with `schema.invalid` and no event output.

## Frozen experiment

16 canary/benign pairs were frozen **before application code**, with independent
expected useful fields/counts and exact baseline rules. Fixture bytes have a
receipt and compiled-in hash; Git preserves them without newline conversion.
See [FROZEN-EVALUATION.md](docs/FROZEN-EVALUATION.md) for cases and denominator.

| Measured result | Observation |
|---|---:|
| Limited denylist leaks | 4 / 16 canary cases |
| Benign baseline masking | 1 / 16 benign cases |
| Minimized output/error leakage of listed forms | 0 / 32 cases |
| Projected events retained | 28 / 32 cases |
| Invalid recognized values rejected | 4 / 32 cases |
| Useful fields/counts matching independent oracle | 32 / 32 outcomes |
| Retained authentication failures / elapsed sum | 28 / 700 ms |

The baseline masks exact password/token/api_key keys and a literal invented token
in string values. It misses Base64, percent-encoding, double-escaped text and a
token in a key. Ordinary JSON Unicode escapes are decoded before masking. These
are deliberate limits of this baseline, not a benchmark of upstream libraries.
Baseline events never reach the sink; only aggregate results are emitted.

No universal encoding coverage, detector accuracy or privacy guarantee follows
from this corpus. Benign masking is a recorded behavior, not a general false
positive rate. Raw fixtures and mutation-failure evidence contain invented data
by design; the no-leak assertions concern application output/error channels.

## Projection contract

Input is one UTF-8 JSON object with actual integer schema_version 1 and an events
array. Every event must satisfy the fixed rules. Required field errors reject the
whole batch. Unknown fields at supported positions are dropped wholesale; known
optional fields with invalid types/values reject. Null and absence differ.

| Retained field | Accepted values |
|---|---|
| event_id | lab-event-NNNN, four ASCII digits, unique in batch |
| event_type | authentication |
| outcome | success or failure |
| severity | low or medium |
| service | sshd or lab-api |
| context.elapsed_ms | optional actual integer 0–60000 |

Empty/unknown-only context is omitted. No timestamps, user/IP/host identifiers,
message, exception/stack data, headers, URL/query/body or arbitrary extras pass.
Dropped-field counts count unknown keys at schema positions, not every nested
key inside a dropped subtree. Allowed IDs/timing/counts still convey information;
this contract is not covert-channel prevention or a privacy theorem.

The public function `log_minimizer.core.minimize(raw_bytes)` returns a fresh native
dict or raises LabError with a closed code. API callers must not log raw input,
tracebacks or frame locals themselves; the supplied CLI handles errors without
those disclosures. `render(result)` is for trusted projection/evaluation results.

## Architecture and bounds

Raw byte cap → byte-level lexical gate → strict standard-library JSON →
schema/cardinality validation → fresh projection → bounded ASCII JSON → stdout.
No logging adapter can add data after this boundary because this lab has no
network/stdlib logger integration. Real adapters require a separate review.

| Fixed limit | Value / timing |
|---|---|
| Raw input/output | 64 KiB; input before decoding, output before emitting |
| Container depth | 8 before JSON parsing |
| Encoded string body | 512 bytes before parsing; excludes quotes, includes escapes/UTF-8 bytes |
| Numeric text | 16 characters before integer conversion; floats/nonfinite reject |
| Array length | 32, checked after JSON parsing |
| Total keys | 256, checked after JSON parsing |

Duplicate decoded keys reject, including escaped aliases. Strict UTF-8 and valid
Unicode scalars are required. The lexical gate handles slash/quote parity and
ignores brackets within strings; **stdlib JSON remains syntax authority**.
Post-parse cardinality is not a preallocation bound. See [ADMISSION.md](docs/ADMISSION.md).

Semantic failures emit no events. Sink writes are nontransactional: short/failed
writes may leave a prefix of already minimized output, then exit 2. There is no
raw fallback. Both failed stdout/stderr buffers are detached at shutdown to
preserve exit 2. Errors use closed codes, not raw keys, values, filenames or
exception messages. JSON ASCII escaping protects output structure; this lab does
not explore terminal-control rendering or CSV interpretation.

## Verification and limitations

**31 tests pass normally and under -O**, on Windows CPython 3.13.7. Frozen
comparison matches every expected outcome. Bandit 1.9.4 has zero findings/errors
and no exclusions. A raw-field-pass-through mutation was detected and source
restored exactly. Review fixed the reproduced dual-closed-pipe exit 120 bug and
removed raw decoder exception contexts from API errors. ECC review was Codex
self-review, not an independent audit. See [REVIEW.md](REVIEW.md) and
[VERIFICATION.md](VERIFICATION.md) for evidence and unrun checks.

Stable local regular files are assumed: stat/fstat/byte checks do not isolate
filesystem races or blocking mounts/devices. No hard process memory/CPU deadline,
real-data/PII guarantee or compromised-host protection. Original data remains in
caller memory and approved synthetic fixture files. See [SECURITY.md](SECURITY.md).

Linux/other-runtime and hosted CI/CodeQL were not run. Immutable-pin tests/Bandit,
CodeQL and Dependabot files are prepared; repository protections/security
eligibility remain unverified. No remote repository, push, merge or deployment.
Optional `requirements-dev.txt` pins Bandit directly; transitive hashes are not
locked. Existing installed tooling was used without downloading dependencies.

## Sources and assistance

Original implementation: MIT, Jake Franciosa. Source comparison in [RESEARCH.md](RESEARCH.md):
[structlog](https://github.com/hynek/structlog) (MIT OR Apache-2.0) and
[loggingredactor](https://github.com/armurox/loggingredactor) (MIT). Neither is a
dependency; no upstream code or tests were executed. Primary references:
[Python JSON](https://docs.python.org/3/library/json.html),
[OWASP Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).
Research text snapshots/licenses and raw worker drafts are retained separately.

Codex implemented and self-reviewed the project, with small reviewed local
Ollama comparison/README drafts. No remote inference or additional spending.
[DECISIONS.md](DECISIONS.md) and [LEARNING.md](LEARNING.md) capture the tradeoffs.
Optional exercise: explain why dropping an unknown subtree differs from masking
password, and what useful information this narrow projection deliberately loses.

## Publication status

See [publication review](PUBLICATION.md) for the October 5 source snapshot, fresh local checks, evidence boundaries and current hosted-check distinction.
