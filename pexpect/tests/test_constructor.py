#!/usr/bin/env python
import pexpect
import unittest

class TestCaseConstructor(unittest.TestCase):
    #def runTest (self):
        
    def test_constructor (self):
	"""This tests that the constructor will work and give
	the same results for different styles of invoking __init__().
	This assumes that the root directory / is static during the test.
	"""
        p1 = pexpect.spawn('/bin/ls -l /')
        p2 = pexpect.spawn('/bin/ls' ,['-l', '/'])
	p1.expect (pexpect.EOF)
	p2.expect (pexpect.EOF)

        assert (p1.before == p2.before)


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseConstructor,'test')

