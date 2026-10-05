# Frozen evaluation contract — October 5, before application code

32 total cases: 16 canary/benign pairs, each containing one authentication event.
Canonical invented canary: LAB_CANARY:invented/only+42. No real credential pattern
or data. Base event: lab-event-0001, authentication, failure, medium, sshd,
context.elapsed_ms 25. Expected projection is exactly those fields, independent
of the implementation. Valid cases retain one failure, medium severity, sshd
and 25 ms. Invalid recognized values reject with zero emitted events.

Exact baseline: case-sensitive keys password/token/api_key masked wholesale;
recursively traverse JSON dictionaries/lists; replace the literal canary only in
string VALUES. Never change keys, decode extra layers, or resolve objects.
No tuning of keys/pattern after observing results. Expected benign masking:
only password case changes an innocuous extra value (1/16); not a general false
positive metric. Minimized unknown fields are purposefully excluded by policy.

| Pair | Canary location/form | Minimized canary case | Baseline leak |
|---|---|---|---|
| password | password, literal | retained useful event | no |
| renamed | other_name, literal | retained | no |
| nested | extras.deep.value, literal | retained | no |
| list | extras list, literal | retained | no |
| message | free-form message, literal | retained | no |
| exception | exception.message, literal | retained | no |
| base64 | message, Base64 | retained | yes |
| url | message, percent-encoded | retained | yes |
| escaped-wire | message, JSON Unicode-escaped wire bytes | retained | no (JSON decode restores literal) |
| double-escaped | message contains literal backslash-u text | retained | yes |
| key | unknown KEY containing literal | retained | yes |
| service | recognized service replaced by literal | reject | no |
| event-id | recognized ID replaced by literal | reject | no |
| timing | elapsed_ms replaced by literal string | reject | no |
| context-type | recognized context replaced by list containing literal | reject | no |
| headers | headers.authorization, literal | retained | no |

All benign paired controls retain the base projection (16/16). Canary events:
12/16 retained, 4/16 rejected. Total utility: 28 retained failure events with
elapsed sum 700 ms, exactly expected field values. Minimized canary leakage:
zero over all 32 output/error outcomes and listed finite forms. Baseline: 4/16
canary-case leaks, evaluated after rendering/JSON round-trip; benign masking
1/16. These are preregistered expectations, not measured results.

Listed leak oracles: literal, Base64, percent-encoded and character-wise
backslash-u form; JSON rendering may escape backslashes, so inspect decoded
strings/keys as well as serialized text. No universal encoding coverage claim.
Expected pairs/fields will be saved in fixtures/cases.json with a SHA-256 receipt
before implementation. Preserve raw run outputs and corrections; no model grader,
repeated inference evaluation, training or remote worker is involved.
