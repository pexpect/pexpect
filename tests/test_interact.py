#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
PEXPECT LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012, Noah Spurrier <noah@noah.org>
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''
import pexpect
import unittest
import PexpectTestCase

class InteractTestCase (PexpectTestCase.PexpectTestCase):

    def test_interact (self):
        p = pexpect.spawn('%s interact.py' % (self.PYTHONBIN,))
        p.sendline (b'Hello')
        p.sendline (b'there')
        p.sendline (b'Mr. Python')
        p.expect (b'Hello')
        p.expect (b'there')
        p.expect (b'Mr. Python')
        assert p.isalive()
        p.sendeof ()
        p.expect (pexpect.EOF)
        assert not p.isalive()
        assert p.exitstatus == 0, (p.exitstatus, p.before)

    def test_interact_unicode (self):
        p = pexpect.spawnu('%s interact_unicode.py' % (self.PYTHONBIN,))
        p.sendline (u'Hello')
        p.sendline (u'theré')
        p.sendline (u'Mr. Pyþon')
        p.expect (u'Hello')
        p.expect (u'theré')
        p.expect (u'Mr. Pyþon')
        assert p.isalive()
        p.sendeof ()
        p.expect (pexpect.EOF)
        assert not p.isalive()
        assert p.exitstatus == 0, (p.exitstatus, p.before)


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(InteractTestCase,'test')

