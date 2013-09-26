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
from __future__ import print_function
from __future__ import unicode_literals

import pexpect
import unittest
import PexpectTestCase

class InteractTestCase (PexpectTestCase.PexpectTestCase):

    def test_interact (self):
        p = pexpect.spawn(str('%s interact.py' % (self.PYTHONBIN,)))
        p.expect('<in >')
        p.sendline (b'Hello')
        p.sendline (b'there')
        p.sendline (b'Mr. Python')
        p.expect (b'<out>Hello')
        p.expect (b'<out>there')
        p.expect (b'<out>Mr. Python')
        assert p.isalive()
        p.sendeof ()
        p.expect (pexpect.EOF)
        assert not p.isalive()
        assert p.exitstatus == 0, (p.exitstatus, p.before)

    def test_interact_unicode (self):
        p = pexpect.spawnu(str('%s interact_unicode.py' % (self.PYTHONBIN,)))
        try:
            p.expect('<in >')
            p.sendline ('Hello')
            p.sendline ('theré')
            p.sendline ('Mr. Pyþon')
            p.expect ('<out>Hello')
            p.expect ('<out>theré')
            p.expect ('<out>Mr. Pyþon')
            assert p.isalive()
            p.sendeof ()
            p.expect (pexpect.EOF)
            assert not p.isalive()
            assert p.exitstatus == 0, (p.exitstatus, p.before)
        except:
            print(p.before)
            raise


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(InteractTestCase, 'test')

