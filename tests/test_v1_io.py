# SPDX-License-Identifier: GPL-3.0-or-later
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentledger import jsonio


class StableIoTests(unittest.TestCase):
    def test_decoder_rejects_wrong_type_with_value_error(self):
        for value in (None, "{}", {"count": 1}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "invalid_json"):
                jsonio.decode_object(value)

    def test_partial_exclusive_write_cleans_only_new_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            with patch.object(jsonio.os, "fsync", side_effect=OSError("synthetic failure")):
                with self.assertRaises(OSError):
                    jsonio.write_new_bytes(output, b"synthetic report")
            self.assertFalse(output.exists())
            output.write_bytes(b"existing bytes")
            with self.assertRaisesRegex(ValueError, "output_exists"):
                jsonio.write_new_bytes(output, b"replacement")
            self.assertEqual(output.read_bytes(), b"existing bytes")

    def test_unicode_scalar_validation_in_keys_values_and_nested_arrays(self):
        for raw in (b'{"x":"\\ud800"}', b'{"\\udfff":1}', b'{"x":["\\ud800"]}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "invalid_json"):
                jsonio.decode_object(raw)
        self.assertEqual(jsonio.decode_object(b'{"x":"\\ud83d\\ude42"}'), {"x": "\U0001f642"})


if __name__ == "__main__":
    unittest.main()
