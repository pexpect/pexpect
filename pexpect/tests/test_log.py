#!/usr/bin/env python
import pexpect
import unittest
import os
import tempfile 

class TestCaseLog(unittest.TestCase):
    def setUp(self):
        print self.id()
        unittest.TestCase.setUp(self)
        
    def test_log (self):
        log_message = 'This is a test. This is a test.'
        filename = tempfile.mktemp()
        mylog = open (filename, 'w')
        p = pexpect.spawn('echo', [log_message])
        p.setlog (mylog)
        p.expect (pexpect.EOF)
        p.setlog (None)
        mylog.close()
        
        l = open(filename).read()
        l = l[:-2]
        os.unlink (filename)
        assert l == log_message

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseLog,'test')

