# Learning

Field minimization is a purpose/schema decision. Pattern recognition asks whether
a value resembles a known secret; it misses unfamiliar names/encodings and may
mask harmless values. A fresh projection can exclude whole unknown subtrees
without guessing what they contain, at the cost of diagnostic detail.

Allowlisted values also need validation. An unrestricted service name or ID can
carry a secret. This lab uses closed service/outcome categories and synthetic ID
grammar; even that does not eliminate information/covert channels.

Pre-parse byte/depth/encoded-string gates differ from post-parse cardinality.
JSON hooks can reject duplicates and long numeric text but cannot reverse
allocations already made. Count escape spelling bytes, not decoded characters.
Braces inside strings and slash parity must not alter depth. Stdlib remains the
syntax parser; invalid scalar values are a separate admission rule.

Error handling is part of the data boundary. argv, parser exceptions, filenames,
tracebacks and fallback logging can expose excluded fields. Fixed codes preserve
failure observability. Python exception contexts can retain raw decoder objects;
detaching them does not erase traceback frames or caller memory.

Validation can be all-or-nothing before emission; writes cannot. Both broken
stdout and stderr buffers require shutdown handling, or CPython may turn a
deliberate exit 2 into 120. A real subprocess regression made that distinction
observable. Mutation testing demonstrated that raw pass-through defeats the
frozen projection oracle, then restored source bytes.

Reusable APIs/helpers: core.minimize(bytes) for validated new records; public CLI
for fixed-code output; scripts/make_demo.py FRESH_DIRECTORY for five frozen
invented inputs, refusing existing folders. Existing shared worker tools reused,
not rebuilt. Detailed usage/assumptions/checks are in README.
