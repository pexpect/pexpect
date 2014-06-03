#!/usr/bin/env python
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

import pexpect
import unittest
import PexpectTestCase
import sys

if sys.version_info[0] >= 3:
    def byte(i):
        return bytes([i])
else:
    byte = chr


class TestCtrlChars(PexpectTestCase.PexpectTestCase):

    def test_control_chars(self):
        '''This tests that we can send all 256 8-bit characters to a child
        process.'''
        child = pexpect.spawn('python getch.py')
        child.expect('READY', timeout=5)
        for i in range(1,256):
            child.send(byte(i))
            child.expect(str(i) + '*')

        # This needs to be last, as getch.py exits on \x00
        child.send(byte(0))
        child.expect(str(0) + '*')
        child.expect(pexpect.EOF)

    def test_sendintr (self):
        child = pexpect.spawn('python getch.py')
        child.expect('READY', timeout=5)
        child.sendintr()
        child.expect(str(child._INTR) + '*')

    def test_sendeof(self):
        child = pexpect.spawn('python getch.py')
        child.expect('READY', timeout=5)
        child.sendeof()
        child.expect(str(child._EOF) + '*')

    def test_bad_sendcontrol_chars (self):
        '''This tests that sendcontrol will return 0 for an unknown char. '''

        child = pexpect.spawn('python getch.py')
        retval = child.sendcontrol('1')
        assert retval == 0, "sendcontrol() should have returned 0 because there is no such thing as ctrl-1."

    def test_sendcontrol(self):
        '''This tests that we can send all special control codes by name.
        '''
        child = pexpect.spawn('python getch.py')
        # On slow machines, like Travis, the process is not ready in time to
        # catch the first character unless we wait for it.
        child.expect('READY', timeout=5)
        child.delaybeforesend = 0.05
        for ctrl in 'abcdefghijklmnopqrstuvwxyz':
            assert child.sendcontrol(ctrl) == 1
            val = ord(ctrl) - ord('a') + 1
            try:
                child.expect(str(val) + '*', timeout=2)
            except:
                print(ctrl)
                raise

        # escape character
        assert child.sendcontrol('[') == 1
        child.expect (str(27) + '*')
        assert child.sendcontrol('\\') == 1
        child.expect (str(28) + '*')
        # telnet escape character
        assert child.sendcontrol(']') == 1
        child.expect (str(29) + '*')
        assert child.sendcontrol('^') == 1
        child.expect (str(30) + '*')
        # irc protocol uses this to underline ...
        assert child.sendcontrol('_') == 1
        child.expect (str(31) + '*')
        # the real "backspace is delete"
        assert child.sendcontrol('?') == 1
        child.expect (str(127) + '*')
        # NUL, same as ctrl + ' '
        assert child.sendcontrol('@') == 1
        child.expect (str(0) + '*')
        # 0 is sentinel value to getch.py
        child.expect (pexpect.EOF)
        assert child.isalive() == False
        assert child.exitstatus == 0

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCtrlChars,'test')

