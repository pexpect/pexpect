"""Exercise incremental decoding at real subprocess EOF."""
import sys
import unittest

import pexpect
from pexpect.popen_spawn import PopenSpawn


class DecoderEOFTests(unittest.TestCase):
    def spawn(self, payload, errors='strict', encoding='utf-8', maxread=2000):
        child = PopenSpawn(
            [sys.executable, '-c', 'import os; os.write(1, {!r})'.format(payload)],
            encoding=encoding, codec_errors=errors, maxread=maxread, timeout=5,
        )
        self.addCleanup(child.proc.stdout.close)
        self.addCleanup(child.proc.stdin.close)
        self.addCleanup(child.wait)
        return child

    def test_truncated_sequence_is_rejected(self):
        child = self.spawn(b'hello\xe2\x82')
        with self.assertRaises(UnicodeDecodeError):
            child.expect(pexpect.EOF)

    def test_truncated_sequence_uses_error_handler(self):
        for errors, expected in [('replace', 'hello\ufffd'), ('ignore', 'hello')]:
            with self.subTest(errors=errors):
                child = self.spawn(b'hello\xe2\x82', errors=errors, maxread=1)
                self.assertEqual(child.read(), expected)
                self.assertEqual(child.read(), '')

    def test_complete_sequence_and_bytes_are_unchanged(self):
        self.assertEqual(self.spawn(b'hello\xe2\x82\xac', maxread=1).read(), 'hello\u20ac')
        self.assertEqual(self.spawn(b'hello\xe2\x82', encoding=None).read(), b'hello\xe2\x82')
