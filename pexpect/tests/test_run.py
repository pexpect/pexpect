#!/usr/bin/env python
import pexpect
import unittest
import commands
import sys

# Many of these test cases blindly assume that sequential
# listing of the /bin directory will yield the same results.
# This may not always be true, but seems adequate for testing now.
# I should fix this at some point.

class ExpectTestCase(unittest.TestCase):
    def setUp(self):
        print self.id()
        unittest.TestCase.setUp(self)

    def test_run (self):
        the_old_way = commands.getoutput('ls -l /bin')
        (the_new_way, exitstatus) = pexpect.run ('ls -l /bin', withexitstatus=1)
        the_new_way = the_new_way.replace('\r','')[:-1]
        assert the_old_way == the_new_way
        assert exitstatus == 0

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

