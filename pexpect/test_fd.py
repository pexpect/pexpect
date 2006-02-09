#!/usr/bin/env python
"""This is a quick ad-hoc test of fdexpect.
This is not an automated unit test.
This should probably be removed some day.
"""
import pexpect, fdpexpect, os

def test_fd ():
    fd = os.open ('./tests/TESTDATA.txt', os.O_RDONLY)
    s = fdpexpect.fdspawn (fd)
    s.expect ('This is the end of test data:')
    #print str(s)
    s.expect (pexpect.EOF)
    assert s.before == ' END\n'

test_fd ()
