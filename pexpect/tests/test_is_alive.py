#!/usr/bin/env python
import pexpect
import unittest
import sys

class IsAliveTestCase(unittest.TestCase):
        
    def test_expect_is_alive1 (self):
        p = pexpect.spawn('/bin/ls')
        p.expect(pexpect.EOF)
        if p.isAlive():
            self.fail ('Child process is not dead. It should be.')

    def test_expect_is_alive2 (self):
        p = pexpect.spawn('/bin/cat')
        if not p.isAlive():
            self.fail ('Child process is not alive. It should be.')
        p.kill(1)
        p.expect(pexpect.EOF)
        if p.isAlive():
            self.fail ('Child process is not dead. It should be.')

    def test_expect_is_alive3 (self):
        p = pexpect.spawn('/bin/cat')
        if not p.isAlive():
            self.fail ('Child process is not alive. It should be.')
        p.kill(9)
        p.expect(pexpect.EOF)
        if p.isAlive():
            self.fail ('Child process is not dead. It should be.')

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(IsAliveTestCase, 'test')

