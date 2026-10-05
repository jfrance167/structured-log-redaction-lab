# Stage 1 admission contract

Raw bytes limited to 64 KiB before any decoder. A linear byte scan gates
container depth 8 and string-body encoded length 512 bytes before JSON parsing.
Quote delimiters do not count; all body bytes do, including UTF-8 multibyte
spelling, backslashes, escaped quotes and all six bytes of a backslash-u escape.
An escaped quote is body data. Slash parity prevents braces/quotes in strings
from changing structural depth. This gate is not a JSON parser: matching bracket
types and escape grammar are validated by json.loads. Incomplete lexical states
fail closed; invalid/truncated escape examples are tested through both stages.

UTF-8 decoding is strict after the raw lexical gate. Raw invalid encodings and
escaped lone surrogates reject. A valid escaped surrogate pair decodes to a valid
Unicode scalar. Post-decode traversal checks every string/key, even dropped data.
parse_int gates numeric token length before conversion. Floats/nonfinite numbers
reject without conversion; duplicate decoded keys reject at every nesting level.
Key totals 256 and arrays 32 are post-parse admission checks, not preallocation
node bounds. JSON syntax authority remains the standard library.

No input content, keys, filenames or parser exception text are attached to public
error codes. Python object/Unicode overhead can exceed raw size. No hard process
RSS/time limit or hostile-host isolation is claimed. Only synthetic local evidence.
