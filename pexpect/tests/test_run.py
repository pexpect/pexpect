#!/usr/bin/env python
import pexpect
import unittest
import commands
import sys
import PexpectTestCase

# TODO Many of these test cases blindly assume that sequential
# TODO listing of the /bin directory will yield the same results.
# TODO This may not always be true, but seems adequate for testing for now.
# TODO I should fix this at some point.

def timeout_callback (d):
#    print d["event_count"],
    if d["event_count"]>5:
        return 1
    return 0

class ExpectTestCase(PexpectTestCase.PexpectTestCase):
    def test_run_exit (self):
        (data, exitstatus) = pexpect.run ('python exit1.py', withexitstatus=1)
        assert exitstatus == 1, "Exit status of 'python exit1.py' should be 1."

    def test_run (self):
        the_old_way = commands.getoutput('ls -l /bin')
        (the_new_way, exitstatus) = pexpect.run ('ls -l /bin', withexitstatus=1)
        the_new_way = the_new_way.replace('\r','')[:-1]
        assert the_old_way == the_new_way
        assert exitstatus == 0

    def test_run_callback (self): # TODO it seems like this test could block forever if run fails...
        pexpect.run("cat", timeout=1, events={pexpect.TIMEOUT:timeout_callback})

    def test_run_bad_exitstatus (self):
        (the_new_way, exitstatus) = pexpect.run ('ls -l /najoeufhdnzkxjd', withexitstatus=1)
        assert exitstatus != 0

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

