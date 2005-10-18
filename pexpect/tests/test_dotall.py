#!/usr/bin/env python
import pexpect
import unittest
import os
import re
import PexpectTestCase

testdata = 'BEGIN\nHello world\nEND'
class TestCaseDotall(PexpectTestCase.PexpectTestCase):
    def test_dotall (self):
        p = pexpect.spawn('echo "%s"' % testdata)
        i = p.expect (['BEGIN(.*)END', pexpect.EOF])
        assert i==0, 'DOTALL does not seem to be working.'

    def test_precompiled (self):
        p = pexpect.spawn('echo "%s"' % testdata)
        pat = re.compile('BEGIN(.*)END') # This overrides the default DOTALL.
        i = p.expect ([pat, pexpect.EOF])
        assert i==1, 'Precompiled pattern to override DOTALL does not seem to be working.'

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseDotall,'test')

