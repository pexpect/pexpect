#!/usr/bin/env python
import pexpect
import unittest
import os
import tempfile 

class TestCaseLog(unittest.TestCase):
    #def runTest (self):
        
    def test_log (self):
	log_message = 'This is a test.'
	filename = tempfile.mktemp()
        p = pexpect.spawn('/bin/echo', [log_message])
	p.log_open (filename)
	p.expect (pexpect.EOF)
	p.log_close()
	l = file(filename).read()
	l = l[:-2]
	os.unlink (filename)
	assert l == log_message

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseLog,'test')

