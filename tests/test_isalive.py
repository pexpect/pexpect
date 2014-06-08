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
import signal
import sys
import time
from . import PexpectTestCase

class IsAliveTestCase(PexpectTestCase.PexpectTestCase):

    def test_expect_wait (self):
        '''This tests that calling wait on a finished process works as expected.
        '''
        p = pexpect.spawn('sleep 3')
        assert p.isalive()
        p.wait()
        assert not p.isalive()

        p = pexpect.spawn('sleep 3')
        assert p.isalive()
        p.kill(9)
        time.sleep(1)
        with self.assertRaises(pexpect.ExceptionPexpect):
            p.wait()

    def test_signal_wait(self):
        '''Test calling wait with a process terminated by a signal.'''
        if not hasattr(signal, 'SIGALRM'):
            return 'SKIP'
        p = pexpect.spawn(sys.executable, ['alarm_die.py'])
        p.wait()
        assert p.exitstatus is None
        self.assertEqual(p.signalstatus, signal.SIGALRM)

    def test_expect_isalive_dead_after_normal_termination (self):
        p = pexpect.spawn('ls', timeout=15)
        p.expect(pexpect.EOF)
        assert not p.isalive()

    def test_expect_isalive_dead_after_SIGHUP(self):
        p = pexpect.spawn('cat', timeout=5, ignore_sighup=False)
        assert p.isalive()
        force = False
        if sys.platform.lower().startswith('sunos'):
            # On Solaris (SmartOs), and only when executed from cron(1), SIGKILL
            # is required to end the sub-process. This is done using force=True
            force = True
        assert p.terminate(force) == True
        p.expect(pexpect.EOF)
        assert not p.isalive()

    def test_expect_isalive_dead_after_SIGINT(self):
        p = pexpect.spawn('cat', timeout=5)
        assert p.isalive()
        force = False
        if sys.platform.lower().startswith('sunos'):
            # On Solaris (SmartOs), and only when executed from cron(1), SIGKILL
            # is required to end the sub-process. This is done using force=True
            force = True
        assert p.terminate(force) == True
        p.expect(pexpect.EOF)
        assert not p.isalive()

    def test_expect_isalive_dead_after_SIGKILL(self):
        p = pexpect.spawn('cat', timeout=5)
        assert p.isalive()
        p.kill(9)
        p.expect(pexpect.EOF)
        assert not p.isalive()

    def test_forced_terminate(self):
        p = pexpect.spawn(sys.executable, ['needs_kill.py'])
        p.expect('READY')
        assert p.terminate(force=True) == True
        p.expect(pexpect.EOF)
        assert not p.isalive()

### Some platforms allow this. Some reset status after call to waitpid.
### probably not necessary, isalive() returns early when terminate is False.
    def test_expect_isalive_consistent_multiple_calls (self):
        '''This tests that multiple calls to isalive() return same value.
        '''
        p = pexpect.spawn('cat')
        assert p.isalive()
        assert p.isalive()
        p.kill(9)
        p.expect(pexpect.EOF)
        assert not p.isalive()
        assert not p.isalive()

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(IsAliveTestCase, 'test')

