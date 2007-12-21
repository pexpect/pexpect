#!/usr/bin/env python
import pexpect
import unittest
import sys, os, time
import PexpectTestCase

class IsAliveTestCase(PexpectTestCase.PexpectTestCase):

    def test_expect_wait (self):
        """This tests that calling wait on a finished process works as expected.
        """
        p = pexpect.spawn('sleep 3')
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        time.sleep(1)
        p.wait()
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')
        p = pexpect.spawn('sleep 3')
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        p.kill(9)
        time.sleep(1)
        try:
            p.wait()
        except pexpect.ExceptionPexpect, e:
            pass
        else:
            self.fail ('Should have raised ExceptionPython because you can\'t call wait on a dead process.')

    def test_expect_isalive_dead_after_normal_termination (self):
        p = pexpect.spawn('ls')
        p.expect(pexpect.EOF)
        time.sleep(1) # allow kernel status time to catch up with state.
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')

    def test_expect_isalive_dead_after_SIGINT (self):
        p = pexpect.spawn('cat', timeout=5)
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        p.terminate()
        # Solaris is kind of slow.
        # Without this delay then p.expect(...) will not see
        # that the process is dead and it will timeout.
        time.sleep(1)
        p.expect(pexpect.EOF)
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')

    def test_expect_isalive_dead_after_SIGKILL (self):
        p = pexpect.spawn('cat', timeout=3)
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        p.kill(9)
        # Solaris is kind of slow.
        # Without this delay then p.expect(...) will not see
        # that the process is dead and it will timeout.
        time.sleep(1)
        p.expect(pexpect.EOF)
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')

### Some platforms allow this. Some reset status after call to waitpid.
    def test_expect_isalive_consistent_multiple_calls (self):

        """This tests that multiple calls to isalive() return same value.
        """

        p = pexpect.spawn('cat')
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        if not p.isalive():
            self.fail ('Second call. Child process is not alive. It should be.')
        p.kill(9)
        p.expect(pexpect.EOF)
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')
        if p.isalive():
            self.fail ('Second call. Child process is not dead. It should be.')
        
if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(IsAliveTestCase, 'test')

