# ECC self-review — October 5, 2026

Scope: entire new project (initial bdeb429 plus current changes), all six app/demo
files, callers, three test modules, frozen fixtures/oracles, CLI/error channels,
CI and documentation. Applied the installed ecc-code-review pinned checklist
and relevant ecc-verification-loop evidence phases. Fixture-freezing guidance
from ecc-eval-harness supplemented ordinary deterministic software tests; no
model grading/evaluation or training occurred. This was Codex self-review, not
an independent review. The native ECC plugin remains uninstalled.

## Concrete defect fixed

**Medium — dirty failed stderr buffer changed CLI exit 2 to 120.** At bdeb429,
log_minimizer/__main__.py:88–94 protected only stdout during shutdown. A subprocess
with both pipe readers closed caused the normal output error, then an unsuccessful
stderr error write; interpreter shutdown retried that buffer and overrode the
documented exit code. Actual before-fix evidence: docs/both-sinks-before-fix.json.
Fix: guard/detach both failed channels before SystemExit. Normal and optimized
test suites verify dual-closed-pipe exit 2. Short stderr writes also return failed
delivery rather than reporting success. No raw fallback was introduced.

Other reviewed corrections before the initial code commit: parser/emit fixed-code
errors are raised outside native exception handlers to avoid attaching raw decoder
objects/OS text in __context__; regression checks parser context is absent. This
does not erase traceback frames/caller memory. Exact frozen fixture bytes are
marked -text in Git; indexed bytes/receipt matched. Error-sink failure explicitly
returns False instead of an empty catch; initial B110 evidence retained.

## Final trust-boundary assessment

Fresh output dictionaries contain only validated fixed fields; no event copy,
free-form message or exception value passes to the sink. All batch semantics are
validated before emitting. Runtime JSON uses raw/depth/string gates, numeric and
duplicate hooks, then explicit post-decode cardinality/scalar admission. Source
has no network logger, arbitrary object conversion, caller regex or raw fallback.
Unknown-key/count information and permitted IDs/timing remain acknowledged limits.

Frozen comparator is intentionally weaker: four canary cases leak. It is isolated
to sealed synthetic fixtures and emits aggregate observations only. No tuning or
corpus edits after the preregistration; evaluation/utility expectations matched.
A deliberate raw-event-copy mutation failed the independent field/leakage oracle;
core source was restored byte-for-byte. Tests protect semantic failure atomicity,
input immutability, malformed/Unicode/argv/internal/OS/output channels and sinks.

Bandit 1.9.4: zero findings/errors, no suppressions or skipped rules. Checks scan
application/demo source; test-only subprocesses run our module and known synthetic
cases, with fixed argument lists and timeouts. No third-party tests ran.

| Severity | Unresolved count | Status |
|---|---:|---|
| Critical | 0 | pass |
| High | 0 | pass |
| Medium | 0 | pass; reproduced sink defect fixed |
| Low | 0 | pass |

Verdict: APPROVE for local synthetic scope. No publication/merge/deployment or
real-data approval. Manual boundary review remains before expanding evidence or
adapters; stable-file races, nontransactional writes, CPU/RSS and finite encoding
coverage limitations are explicit. Linux/hosted checks remain unverified.
