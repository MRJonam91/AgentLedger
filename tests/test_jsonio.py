# SPDX-License-Identifier: GPL-3.0-or-later
import json
import tempfile
import unittest
from pathlib import Path

from agentledger.jsonio import decode_object, read_jsonl, write_new_object


class JsonTests(unittest.TestCase):
    def test_strict_decoding_and_bom(self):
        self.assertEqual(decode_object(b'\xef\xbb\xbf{"count":1}'), {"count": 1})
        for value in [b'{"a":1,"a":2}', b'{"x":NaN}', b'[]', b'\xff', b'{broken',
                      b'{"x":' + b'[' * 80 + b'0' + b']' * 80 + b'}']:
            with self.subTest(value=value[:10]), self.assertRaises(ValueError):
                decode_object(value)

    def test_exclusive_write_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "checkpoint.json"
            write_new_object(path, {"count": 1})
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "output_exists"):
                write_new_object(path, {"count": 2})
            self.assertEqual(path.read_bytes(), before)

    def test_overflow_numbers_are_rejected_in_ignored_nested_fields(self):
        for raw in [b'{"x":1e999}', b'{"x":-1e999}', b'{"x":[{"y":1e999}]}']:
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "invalid_json"):
                decode_object(raw)

    def test_jsonl_blank_lines_and_record_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "batch.jsonl"
            path.write_bytes(b'\xef\xbb\xbf{"one":1}\r\n\n{"two":2}\n')
            self.assertEqual(read_jsonl(path), [{"one": 1}, {"two": 2}])
            for value in [b"\n", b'{}\n' * 1001, b'{}\n{"bad":NaN}',
                          b' ' * (16 * 1024 * 1024 + 1)]:
                path.write_bytes(value)
                with self.assertRaises(ValueError):
                    read_jsonl(path)


if __name__ == "__main__":
    unittest.main()
