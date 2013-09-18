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
import pexpect
import unittest
import PexpectTestCase
import time

class TestCaseWinsize(PexpectTestCase.PexpectTestCase):

    def test_winsize (self):
        '''
        This tests that the child process can set and get the windows size.
        This makes use of an external script sigwinch_report.py.
        '''
        p1 = pexpect.spawn('%s sigwinch_report.py' % self.PYTHONBIN)
        time.sleep(10)
        p1.setwinsize (11,22)
        time.sleep(3)
        index = p1.expect ([pexpect.TIMEOUT, b'SIGWINCH: \(([0-9]*), ([0-9]*)\)'], timeout=30)
        if index == 0:
            self.fail ("TIMEOUT -- this platform may not support sigwinch properly.\n" + str(p1))
        r = p1.match.group(1)
        c = p1.match.group(2)
        assert (r==b"11" and c==b"22")
        time.sleep(1)
        p1.setwinsize (24,80)
        index = p1.expect ([pexpect.TIMEOUT, b'SIGWINCH: \(([0-9]*), ([0-9]*)\)'], timeout=10)
        if index == 0:
            self.fail ("TIMEOUT -- this platform may not support sigwinch properly.\n" + str(p1))
        r = p1.match.group(1)
        c = p1.match.group(2)
        assert (r==b"24" and c==b"80")
        p1.close()

#    def test_parent_resize (self):
#        pid = os.getpid()
#        p1 = pexpect.spawn('%s sigwinch_report.py' % self.PYTHONBIN)
#        time.sleep(10)
#        p1.setwinsize (11,22)
#        os.kill (pid, signal.SIGWINCH)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseWinsize,'test')


