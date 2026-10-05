# Security model

Synthetic local JSON only. No real credentials/logs/private data, network logging,
live SIEM changes, production PII classifier or universal redaction guarantee.
The application projects into fresh dictionaries from a fixed field/value policy.
It never emits baseline events, raw input/digests, arbitrary keys or exception text.

Threats: attacker-controlled synthetic keys/values, renamed/nested/encoded tokens,
JSON resource abuse, invalid required values and error/sink disclosures. Byte,
depth/string/numeric gates precede or participate in parsing; array/key limits
follow parsing and are not preallocation object bounds. Syntax authority remains
stdlib JSON. Frozen finite canary forms are evaluation oracles, not a general
secret detector or decoder. Allowlisted fields/counts may still carry information.

Atomic semantics only: no events on validation errors. Short/failed writes are
nontransactional and can leave a minimized prefix. CLI reports fixed failure,
without raw fallback; if stderr also fails the status remains failure. Both
buffered channels are guarded against shutdown retries changing exit 2 to 120.
Error args/codes exclude raw data; Python traceback frames/caller memory may
still retain it. API callers must not serialize locals/tracebacks/raw input.

Regular-file checks do not close stat/open races, symlink/device swaps or blocking
I/O. Choose stable synthetic files on a local filesystem. Python allocations and
Unicode object overhead can exceed encoded bytes. No hard RSS/CPU timeout or OS
sandbox exists in the CLI. The host, interpreter and local project source are
trusted; fixture hash detects accidental changes, not a compromised host.

No upstream package installation, arbitrary Python object handling, repr/deepcopy,
caller-supplied regexes, schema extension or logging adapters. Fixtures/mutation
logs intentionally contain invented canaries and are not real incident evidence.
Future real adapters/data require new scope, appropriate isolation and manual
review. Do not weaken fixed rules or claim compliance to accommodate real logs.

No hosted reporting endpoint/release exists. Report issues to the owner through
an authorized private channel once available; do not post real logs/secrets.
