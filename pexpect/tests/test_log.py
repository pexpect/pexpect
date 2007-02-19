#!/usr/bin/env python
import pexpect
import unittest
import os
import tempfile 
import PexpectTestCase

class TestCaseLog(PexpectTestCase.PexpectTestCase):
    def test_log (self):
        log_message = 'This is a test.'
        filename = tempfile.mktemp()
        mylog = open (filename, 'w')
        p = pexpect.spawn('echo', [log_message])
        p.logfile = mylog
        p.expect (pexpect.EOF)
        p.logfile = None
        mylog.close()
        lf = open(filename).read()
        lf = lf[:-2]
        os.unlink (filename)
        assert lf == log_message
    def test_log2 (self):
        log_message = 'This is a test.'
        filename = tempfile.mktemp()
        mylog = open (filename, 'w')
        p = pexpect.spawn('cat')
        p.logfile = mylog
        p.sendline(log_message)
        p.sendeof()
        p.expect (pexpect.EOF)
        p.logfile = None
        mylog.close()
        lf = open(filename).read()
        os.unlink (filename)
        lf = lf.replace(chr(4),'')
        assert lf == 'This is a test.\nThis is a test.\r\nThis is a test.\r\n', repr(lf)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseLog,'test')

