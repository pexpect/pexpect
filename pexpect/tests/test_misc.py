#!/usr/bin/env python
import pexpect
import unittest
import PexpectTestCase
import time

class TestCaseMisc(PexpectTestCase.PexpectTestCase):
    def test_isatty (self):
        child = pexpect.spawn('cat')
        assert child.isatty(), "Not returning True. Should always be True."
    def test_read (self):
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        child.sendeof()
        assert child.read(0) == '', "read(0) did not return ''"
        assert child.read(1) == 'a', "read(1) did not return 'a'"
        assert child.read(1) == 'b', "read(1) did not return 'b'"
        assert child.read(1) == 'c', "read(1) did not return 'c'"
        assert child.read(2) == '\r\n', "read(2) did not return '\\r\\n'"
        assert child.read() == 'abc\r\n', "read() did not return 'abc\\r\\n'"

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseDestructor,'test')

