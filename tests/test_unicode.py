# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import io, tempfile

import pexpect
import unittest
import PexpectTestCase

class UnicodeTests(PexpectTestCase.PexpectTestCase):
    def test_expect_basic (self):
        p = pexpect.spawnu('cat')
        p.sendline('Hello')
        p.sendline('there')
        p.sendline('Mr. þython') # þ is more like th than p, but never mind
        p.expect('Hello')
        p.expect('there')
        p.expect('Mr. þython')
        p.sendeof ()
        p.expect (pexpect.EOF)

    def test_expect_exact_basic (self):
        p = pexpect.spawnu('cat')
        p.sendline('Hello')
        p.sendline('there')
        p.sendline('Mr. þython')
        p.expect_exact('Hello')
        p.expect_exact('there')
        p.expect_exact('Mr. þython')
        p.sendeof()
        p.expect_exact (pexpect.EOF)

    def test_expect_echo (self):
        '''This tests that echo can be turned on and off.
        '''
        p = pexpect.spawnu('cat', timeout=10)
        self._expect_echo(p)

    def test_expect_echo_exact (self):
        '''Like test_expect_echo(), but using expect_exact().
        '''
        p = pexpect.spawnu('cat', timeout=10)
        p.expect = p.expect_exact
        self._expect_echo(p)

    def _expect_echo (self, p):
        p.sendline('1234') # Should see this twice (once from tty echo and again from cat).
        index = p.expect (['1234', 'abcdé', 'wxyz', pexpect.EOF, pexpect.TIMEOUT])
        assert index == 0, "index="+str(index)+"\n"+p.before
        index = p.expect (['1234', 'abcdé', 'wxyz',pexpect.EOF])
        assert index == 0, "index="+str(index)
        p.setecho(0) # Turn off tty echo
        p.sendline('abcdé') # Now, should only see this once.
        p.sendline('wxyz') # Should also be only once.
        index = p.expect ([pexpect.EOF,pexpect.TIMEOUT, 'abcdé', 'wxyz', '1234'])
        assert index == 2, "index="+str(index)
        index = p.expect ([pexpect.EOF, 'abcdé', 'wxyz', '7890'])
        assert index == 2, "index="+str(index)
        p.setecho(1) # Turn on tty echo
        p.sendline ('7890') # Should see this twice.
        index = p.expect ([pexpect.EOF, 'abcdé', 'wxyz', '7890'])
        assert index == 3, "index="+str(index)
        index = p.expect ([pexpect.EOF, 'abcdé', 'wxyz', '7890'])
        assert index == 3, "index="+str(index)
        p.sendeof()

    def test_log_unicode(self):
        msg = "abcΩ÷"
        filename_send = tempfile.mktemp()
        filename_read = tempfile.mktemp()
        p = pexpect.spawnu('cat')
        p.logfile_send = io.open(filename_send, 'w', encoding='utf-8')
        p.logfile_read = io.open(filename_read, 'w', encoding='utf-8')
        p.sendline(msg)
        p.sendeof()
        p.expect(pexpect.EOF)
        p.close()
        p.logfile_send.close()
        p.logfile_read.close()

        with io.open(filename_send, encoding='utf-8') as f:
            self.assertEqual(f.read(), msg+'\n\x04')

        with io.open(filename_read, encoding='utf-8', newline='') as f:
            self.assertEqual(f.read(), (msg+'\r\n')*2 )


    def test_spawn_expect_ascii_unicode(self):
        # A bytes-based spawn should be able to handle ASCII-only unicode, for
        # backwards compatibility.
        p = pexpect.spawn('cat')
        p.sendline('Camelot')
        p.expect('Camelot')

        p.sendline('Aargh')
        p.expect_exact('Aargh')

        p.sendeof()
        p.expect(pexpect.EOF)

    def test_spawn_send_unicode(self):
        # A bytes-based spawn should be able to send arbitrary unicode
        p = pexpect.spawn('cat')
        p.sendline('3½')
        p.sendeof()
        p.expect(pexpect.EOF)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(UnicodeTests, 'test')