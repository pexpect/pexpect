#!/usr/bin/env python
import pexpect
import unittest
import sys, os

class IsAliveTestCase(unittest.TestCase):
        
    def test_expect_isalive1 (self):
        p = pexpect.spawn('ls')
        p.expect(pexpect.EOF)
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')

    def test_expect_isalive2 (self):
        p = pexpect.spawn('cat', timeout=5)
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        p.kill(1)
        p.expect(pexpect.EOF)
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')

    def test_expect_isalive3 (self):
        p = pexpect.spawn('cat', timeout=3)
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        p.kill(9)
        p.expect(pexpect.EOF)
        if p.isalive():
#            pid, sts = os.waitpid(p.pid, 0)#, os.WNOHANG)
#            print 'p.pid, pid, sts:', p.pid, pid, sts
#            pp = pexpect.spawn('ps -p %d' % p.pid)
#            pp.expect (pexpect.EOF)
#            print pp.before
            self.fail ('Child process is not dead. It should be.')

### Some platforms allow this. Some reset status after call to waitpid.
    def OFF_test_expect_isalive4 (self):
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

