#!/usr/bin/env python
import pexpect
import unittest
import PexpectTestCase
class SplitCommandLineTestCase(PexpectTestCase.PexpectTestCase):
    def testSplitSizes(self):
        assert len(pexpect.split_command_line(r'')) == 0
        assert len(pexpect.split_command_line(r'one')) == 1
        assert len(pexpect.split_command_line(r'one two')) == 2
        assert len(pexpect.split_command_line(r'one  two')) == 2
        assert len(pexpect.split_command_line(r'one   two')) == 2
        assert len(pexpect.split_command_line(r'one\ one')) == 1
        assert len(pexpect.split_command_line('\'one one\'')) == 1
        assert len(pexpect.split_command_line(r'one\"one')) == 1
        assert len(pexpect.split_command_line(r'This\' is a\'\ test')) == 3

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(SplitCommandLineTestCase,'test')
