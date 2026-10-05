# Structured Log Redaction Lab — proposed implementation contract

**Stages 1–4 approved by coordinator on October 5, 01:31 Eastern.** Tier 3:
new security learning tool handling structured data before a logging sink.
Research and alternatives: RESEARCH.md. Authorization source: STATE.md.

## Problem and success criteria

Demonstrate why recognizing secret patterns is weaker than minimizing data at
the source. One local bounded synthetic JSON batch yields new validated events
for an in-memory/local report sink. Raw fields never enter that sink or an error
message. Preserve a narrow analytic structure: event category, outcome, severity,
approved lab service, correlation ID and timing. No real credentials/logs/private
data, network logger, or universal PII-cleanup claim.

Success: frozen fixture cases with paired benign controls; no invented canary or
its listed encoded forms in any emitted channel under the minimization policy;
expected detection counts/correlation preserved; unknown fields absent; failures
emit only closed error codes and no partial events. Compare a limited denylist
baseline by aggregate fixture metrics. Expected misses are educational outcomes,
not passing privacy protection. No accuracy number until measured.

## Scope and schema

Input: one regular stable local UTF-8 JSON document, version 1, events array.
Only synthetic files documented in the lab. First version supports at most 32
events. Top-level unknown fields are dropped; version must be an actual integer 1.
Each event is a JSON object. Build a fresh projection using explicit paths:

| Output path | Admission rule | Purpose |
|---|---|---|
| event_id | exact lab-event-NNNN syntax, unique within batch | Synthetic correlation |
| event_type | authentication only | Known security category |
| outcome | success/failure only | Failure-count demonstration |
| severity | low/medium only | Filter/grouping |
| service | sshd/lab-api only | Fixed service dimension |
| context.elapsed_ms | optional actual int 0–60000; reject null/bool | Timing usefulness |

No free-form timestamp, username, IP, host, message, stacktrace, exception,
headers, request/query/body, URL, arbitrary extras, arbitrary IDs or custom object
values pass through. This reduces detail relative to SIEM and is intentional.
A caller cannot add allowlist paths/regexes from input. Missing or invalid required
fields rejects the batch; wrong type/invalid recognized optional value rejects.
An absent optional context field remains absent. Unknown nested fields, lists and
subtrees are dropped wholesale, without echoing their names or values. A known
context with wrong type rejects. Exact case-sensitive keys; confusables and
escaped-key aliases receive normal JSON decoding then exact schema treatment.

Outputs include fixed policy version and counts of events/dropped unknown fields
without original names, values, paths or raw-input digests. A raw digest is not
privacy protection and is unnecessary here. Event IDs are validated input data;
the plan does not claim they or allowed timings eliminate covert channels.

## Bounded decoding and architecture

Pipeline: byte admission -> lightweight lexical depth/string bound preflight ->
strict stdlib JSON -> cardinality/schema validation -> fresh projection -> bounded
ASCII serializer -> sink. The preflight tracks quoted strings and escapes so
braces inside strings do not count as containers; it is a gate, not a replacement
JSON parser. Malformed lexical states fail with fixed codes. JSON parser remains
the syntax authority. No arbitrary Python objects/deepcopy/repr.

Proposed fixed ceilings: raw 64 KiB, depth 8 before JSON decode, encoded string
token 512 bytes before decode, integer numeric token 16 characters before int,
32 events, 256 keys across the parsed batch as an admission policy after decode,
array length 32 after decode, final output 64 KiB. Reject floats/nonfinite tokens
and duplicate decoded keys at every level. Input cap bounds total encoded data;
post-parse cardinality checks are **not** preallocation node limits. Document
Python object/Unicode expansion and lack of hard RSS/CPU guarantees. A stricter
preflight design must be reviewed before implementation acceptance; do not expand
into a custom general JSON parser or silently weaken limits.

One atomic batch: assemble/validate/minimize/render within bounds before emitting
events. Invalid or excessive input produces no partial data. Stable input file
assumption has a filesystem race/blocking limitation. Sink writes use stdout or
fresh exclusive local output only if explicitly specified in implementation;
no overwriting existing evidence, input aliases or automatic intermediate dumps.

Error paths: fixed codes such as input.invalid_json, input.limit, schema.invalid,
output.error, internal.error with non-sensitive offsets/counts only when useful.
Never echo raw JSON, arbitrary keys, filename/argv, OS exception text, parse
message, repr/traceback or exception content. Capture stdout/stderr in tests.
CLI argument errors must follow the same closed-error policy. Useful failures
remain visible through status and closed codes; no fallback to raw logging.

## Threat model and comparison baseline

Attacker controls synthetic JSON bytes, keys, nesting, values, encoded canaries
and malformed/error triggers. Protect sink confidentiality within this exact
policy, analytic utility and availability. Unknown fields are hostile to the
projection; allowlisted values are also validated, never implicitly trusted.

Comparison baseline is a tiny documented denylist on fixed sensitive names and
one literal invented-canary pattern, evaluated only on built-in frozen fixtures.
No user regexes, recursive arbitrary decoding, token services or arbitrary code.
Observe renamed/nested/list/JSON-escaped/base64/URL-encoded variants, free-form
messages and exception-shaped fields. Do not emit baseline raw events; report
only predetermined case IDs/counts/outcomes. Listed transforms are evaluation
oracles, not a universal decoder or production secret detector. Include benign
lookalikes to count false positives. Freeze cases/expected labels before tuning.

Residual limits: allowed fields can still convey information, even under strict
grammar; no entropy/privacy theorem, covert-channel prevention, PII classifier,
production adapter guarantee, legal-compliance claim or protection against a
compromised interpreter/host. Nothing validates an actual downstream collector.
No terminal-control rendering or CSV behavior experiment. No live SIEM changes.

## Stages and acceptance

1. Freeze schema, policy decisions, 32 total synthetic cases (16 paired
   canary/benign controls)
   and expected useful-field/count outcomes before code tuning. Review stdlib
   decoder/preflight boundaries, duplicate-key behavior and failure channels.
   Acceptance: every field has a reason, and every case is invented/non-sensitive.
2. Implement bounded admission/projection with standard library only. Tests for
   depth/string/numeric boundaries, escape-aware preflight, unknown fields at all
   selected shapes, duplicate keys including escaped aliases, invalid recognized
   values, bool/null, batch atomicity and input immutability. No raw object leaks.
3. Frozen evaluation and CLI: baseline misses/false positives explicitly separate
   from minimized-output assertions; check original and listed encoded canaries
   against every sink/error channel. Paired controls preserve failure counts,
   grouping and IDs; throw a synthetic internal exception carrying a canary and
   verify no traceback/value emission. File/output failures, broken pipes and
   argument errors use fixed codes. Mutation witness removes one real boundary
   and must fail the corresponding canary/unknown-field guard; source restored.
4. ECC self-review/fixes/affected reruns, Bandit, syntax, staged hygiene/limited
   secret scan, docs/demo/MIT-original license/AI disclosure, STATE/DECISIONS/
   LEARNING and verified knowledge milestone. Prepare immutable-pin Python CI/
   CodeQL baseline if local repository initialization is approved; hosted runs,
   eligibility/protections remain unverified without separate publication scope.

Definitions of done: all declared policy cases/checks pass; educational baseline
results accurately reported; failures retained and fixed; unsupported scope and
unrun checks disclosed. No arbitrary coverage target or new dependency required.
One reusable deterministic fixture/evaluation helper with inputs, usage,
assumptions and verification; raw worker drafts separate from accepted edits.

Learning goals: minimizing data differs from recognizing patterns; unknown keys
are a schema decision; preserving useful detection structure requires explicit
contracts; error logging itself can leak; synthetic metrics have narrow scope.
Offer an optional exercise after implementation: explain why replacing a token
under password is weaker than dropping a whole unknown subtree.

## Approval boundary and worker choice

Coordinator must approve this exact scope before any project code. Local
implementation, checks/docs/review and a separate local repo are the requested
next scope; no publication, network logging, deployment, merge, new chat,
scheduler or shared-tool/config changes. Stop dispatch per existing cutoff.
Local Ollama comparison draft was reviewed; no remote worker or paid call used.
Security/architecture judgments remain Codex. Native ECC plugin remains absent;
use the installed narrow review entry point.

## Incorporated coordinator addendum

Authority: ../.private/coordination/2026-10-05/SUCCESSORS.md, Timeline and
structured-log approvals, 01:31 heartbeat. Freeze all 16 paired cases, independent
utility expectations and the exact baseline before tuning. Test lexical byte
counting, UTF-8, backslash/quote parity, braces within strings, invalid/truncated
escapes and invalid Unicode scalars. Stdlib JSON remains syntax authority; hooks
and post-parse cardinality are not preallocation node limits. No parser expansion.
Semantic errors emit no events; a short/failed/broken sink write is nontransactional
and must return a fixed error without raw fallback/false success. Exercise argv,
internal, OS and output error leakage. Standalone local Git/security files are
approved, preserving parent Git. No publication or further scope authorized.
