#!/usr/bin/env python
import pexpect
import unittest
import sys

class IsAliveTestCase(unittest.TestCase):
        
    def test_expect_isalive1 (self):
        p = pexpect.spawn('ls')
        p.expect(pexpect.EOF)
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')

    def test_expect_isalive2 (self):
        p = pexpect.spawn('cat')
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        p.kill(1)
        p.expect(pexpect.EOF)
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')

    def test_expect_isalive3 (self):
        p = pexpect.spawn('cat')
        if not p.isalive():
            self.fail ('Child process is not alive. It should be.')
        p.kill(9)
        p.expect(pexpect.EOF)
        if p.isalive():
            self.fail ('Child process is not dead. It should be.')

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(IsAliveTestCase, 'test')

