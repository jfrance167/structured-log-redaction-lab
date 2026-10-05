# Research — October 5, 2026

Research only. No project code, dependencies or upstream tests executed.
Connected GitHub search was attempted once; backend transport failed. Used public
GitHub CLI/API and primary web docs as fallback. Firecrawl skill was reviewed,
but calls were deferred without verified zero-cost eligibility. No paid service,
remote drafting or real logs/secrets used.

## Candidate comparison and recommendation

A: allowlisted structured-event minimization before a sink. Validating a narrow
known schema and constructing a fresh object is a stronger learning boundary
than trying to recognize every sensitive key or value in an arbitrary record.
Tradeoff: less diagnostic detail and explicit schema maintenance.

B: frozen synthetic secret-pattern detector evaluation. A fixed invented corpus
can measure misses and false positives for a limited detector, including renamed,
nested and encoded variants. Tradeoff: corpus performance does not establish
general privacy or justify forwarding real logs. Recommend A; include B only as
a deliberately limited comparison inside its evaluation, not a new scanner.
Avoid the CSV owner's terminal-rendering alternative and actual log collection.

## Reuse and local evidence

Read siem-logging-pipeline README, SECURITY and scripts/generator.py. Its synthetic
authentication schema includes event IDs, timestamp, outcome, service, username,
source IP/ports and a free-form message. Its purpose is JSONL transport through
Alloy/Loki and detection in Grafana. Do not run or modify that stack here. Reuse
the conceptual authentication categories, documented-address/fictional-identity
conventions and paired scenario style; a new projection schema must not inherit
message/user/IP fields merely because the SIEM generator emits them.

Bounded Markdown/source searches found no matching implemented minimization lab;
not an exhaustive inventory. Relevant vault notes: Evidence Integrity (keep
original/sanitized/generated evidence distinct) and Python Input and
Serialization Boundaries (admission before parsing, strict numeric/JSON policy).
Home and Codex Integration were consulted. Existing Marshalsea and pickle tests,
reviews and runtime/resource/hosted limitations remain untouched.

## Upstream assessment

Sources saved under research/ as text/base64 snapshots, metadata, observed heads,
open-item inventory and license/CI evidence. Branch files and heads were fetched
separately; this is dated inspection evidence, not a pinned dependency artifact
or attestation that every file belongs to one immutable revision.

| Candidate | Actual evidence | Fit/decision |
|---|---|---|
| [hynek/structlog](https://github.com/hynek/structlog) | Active/not archived; repository pushed October 1. Source _base.py combines context/event kwargs and runs processors in order before calling wrapped logger. test_base.py verifies processor return/call behavior. pyproject requires Python >=3.10; typing-extensions only below 3.11. MIT OR Apache-2.0 in package/source; actual LICENSE-MIT inspected. GitHub license metadata NOASSERTION is not absence of a license. CI, CodeQL and other workflow files exist; execution not verified. Open PR #842 concerns LogRecord attribute collisions, #844 positional mapping formatting; these are open work, not established vulnerabilities. | Good maintained integration framework if a later authorized lab needs real logging adapters. Processor ordering matters: anything adding fields after minimization could reintroduce data. First lab can model the boundary with standard library and an in-memory sink, avoiding an unnecessary runtime dependency. |
| [armurox/loggingredactor](https://github.com/armurox/loggingredactor) | MIT license file inspected; not archived, pushed June 30. setup.py declares Python >=3.7 and no install_requires; build uses setuptools. redacting_filter.py masks keys/regexes recursively across several Python container/object types, copies data, ignores exc_info/exc_text/stack_info and other built-ins, returns original content on deepcopy failure, and retains logging on filtering failures. Actual tests exercise nested containers and hostile object methods; one states filter must let logs through. CI includes lint/tests across Python versions and mutable v2/v3/v4 Action tags. No open items returned by the bounded query, not proof of no bugs/advisories. | Useful denylist/reference alternative, not an implementation of the proposed fail-closed JSON-only contract. Arbitrary objects, repr/deepcopy, ignored exception fields and fail-open handling enlarge the trust boundary. Do not install/run its object fixtures or import this implementation into the lab. Mutable CI tags are a supply-chain observation, not a confirmed exploit. |

Recommendation: **build an original standard-library lab**, not fork either
library. No suitable ready-made exact bounded/synthetic-only projection contract
was established in these searches. Both upstreams remain legitimate alternatives
for their broader logging use cases. If code were borrowed, retain the selected
license/attribution obligations; this plan proposes no borrowed implementation.
No dependency installation, package artifact audit, Scorecard run or hosted test
run occurred. Stars were not evidence of suitability or safety.

## Primary-source findings and limits

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
  identifies access tokens/passwords/keys and other sensitive data as categories
  generally requiring exclusion or suitable protection. It also emphasizes
  useful security-event structure. This is design guidance, not certification
  of any field policy or authority to handle real personal data.
- [structlog processor documentation](https://www.structlog.org/en/stable/processors.html)
  explains event dictionary transformation. The inspected pipeline confirms
  ordering before the wrapped logger; minimization is ineffective if bypassed
  or followed by an unreviewed data-adding processor.
- [Python JSON documentation](https://docs.python.org/3/library/json.html)
  warns of CPU/memory consumption and describes parse_int/parse_constant and
  object_pairs_hook. Hooks can enforce numeric/duplicate-key policy; they do
  not impose a pre-allocation object-count or nesting limit by themselves.

Claims about encoded variants are proposed tests, not measured detector results.
No exhaustive encoding search, PII model, regex-security benchmark, production
logging audit or universal redaction guarantee was performed.

## Worker

Ollama qwen3.5:2b produced the bounded public comparison in 1.141 seconds. Draft
accurately separated minimization from limited detection; reviewed factual
phrasing informed this recommendation. Brief/raw output retained in research/.
Security judgments and specification are Codex-reviewed. No remote worker needed;
Laya's tested categorization/triage schemas do not improve this research.
