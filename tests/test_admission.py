"""Byte/escape/decoder boundaries using invented data only."""

import json
import unittest

from log_minimizer.admission import LabError, lexical_gate, parse


class AdmissionTests(unittest.TestCase):
    def rejected(self, raw, code):
        with self.assertRaises(LabError) as caught:
            parse(raw)
        self.assertEqual(caught.exception.code, code)

    def test_utf8_and_unicode_scalars(self):
        self.assertEqual(parse('"é😀"'.encode()), "é😀")
        self.assertEqual(parse(b'"\\ud83d\\ude00"'), "😀")
        for raw in (b'"\xff"', b'"\xed\xa0\x80"', b'"\\ud800"', b'{"\\udfff":0}'):
            self.rejected(raw, "input.encoding")

    def test_encoded_string_exact_boundary(self):
        self.assertEqual(len(parse(b'"' + b"x" * 512 + b'"')), 512)
        self.rejected(b'"' + b"x" * 513 + b'"', "input.limit")
        self.assertEqual(len(parse(('"' + 'é' * 256 + '"').encode())), 256)
        self.rejected(('"' + 'é' * 257 + '"').encode(), "input.limit")
        self.assertEqual(len(parse(b'"' + b'\\u0061' * 85 + b'"')), 85)
        self.rejected(b'"' + b'\\u0061' * 86 + b'"', "input.limit")

    def test_quote_backslash_parity_and_braces_in_strings(self):
        for value in ('[{' * 100, '\\"' * 20, '\\\\' * 20, '"}][{\\'):
            self.assertEqual(parse(json.dumps(value).encode()), value)
        for n in range(8):
            # Even slash count permits delimiter; odd count escapes it and
            # leaves a truncated string. Stdlib remains syntax authority.
            raw = b'"' + b'\\' * n + b'"'
            if n % 2 == 0:
                self.assertEqual(parse(raw), '\\' * (n // 2))
            else:
                self.rejected(raw, "input.invalid_json")

    def test_invalid_truncated_escapes_and_control(self):
        for raw in (b'"\\x"', b'"\\u123"', b'"\\uQQQQ"', b'"abc\\', b'"a\nb"', b'[}'):
            self.rejected(raw, "input.invalid_json")

    def test_depth_precedes_decode(self):
        self.assertEqual(parse(b"[" * 8 + b"0" + b"]" * 8), [[[[[[[[0]]]]]]]])
        self.rejected(b"[" * 9 + b"0" + b"]" * 9, "input.limit")
        lexical_gate(b'"' + b"[" * 500 + b'"')

    def test_raw_byte_bound_before_parser(self):
        self.rejected(b" " * 65537, "input.limit")
        self.assertEqual(parse(b" " * 65535 + b"0"), 0)

    def test_duplicate_keys_and_escaped_aliases(self):
        self.rejected(b'{"a":1,"\\u0061":2}', "input.duplicate")
        self.rejected(b'{"nested":{"x":1,"x":2}}', "input.duplicate")

    def test_numeric_hooks_and_strict_json(self):
        self.assertEqual(parse(b"1234567890123456"), 1234567890123456)
        self.rejected(b"12345678901234567", "input.number")
        for raw in (b"NaN", b"Infinity", b"-Infinity", b"1.0", b"1e1000"):
            self.rejected(raw, "input.number")
        for raw in (b"0 0", b"", b'\xef\xbb\xbf{}'):
            self.rejected(raw, "input.invalid_json")

    def test_post_parse_cardinality(self):
        self.rejected(json.dumps([0] * 33).encode(), "input.limit")
        self.rejected(json.dumps({str(i): 0 for i in range(257)}).encode(), "input.limit")

    def test_parser_errors_do_not_retain_raw_exception_context(self):
        for raw in (b'"invented-canary\xff"', b'{"invented-canary":}'):
            with self.assertRaises(LabError) as caught:
                parse(raw)
            self.assertIsNone(caught.exception.__context__)
            self.assertEqual(caught.exception.args, (caught.exception.code,))


if __name__ == "__main__":
    unittest.main()
