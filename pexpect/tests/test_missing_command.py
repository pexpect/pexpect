#!/usr/bin/env python
import pexpect
import unittest

class MissingCommandTestCase (unittest.TestCase):
    def testMissingCommand(self):
        try:
	    i = pexpect.spawn ('ZXQYQZX')
        except Exception:
            pass
        else:
            fail('expected an Exception')
    
if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(MissingCommandTestCase,'test')

