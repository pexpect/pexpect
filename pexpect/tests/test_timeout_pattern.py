#!/usr/bin/env python
import pexpect
import unittest
import sys, os, time

class Exp_TimeoutTestCase(unittest.TestCase):
    def setUp(self):
        print self.id()
        unittest.TestCase.setUp(self)

    def test_matches_exp_timeout (self):
        """This tests that we can raise and catch TIMEOUT_PATTERN.
        """
        try:
            raise pexpect.TIMEOUT_PATTERN("TIMEOUT_PATTERN match test","")
        except pexpect.TIMEOUT_PATTERN:
            pass
            #print "Correctly caught TIMEOUT_PATTERN when raising TIMEOUT_PATTERN."
        else:
            self.fail('TIMEOUT_PATTERN not caught by an except TIMEOUT_PATTERN clause.')

    def test_matches_timeout (self):
        """Verify that rasing an TIMEOUT_PATTERN matches an except TIMEOUT clause."""
        try:
            raise pexpect.TIMEOUT_PATTERN("TIMEOUT match test", "")
        except pexpect.TIMEOUT:
            pass
            #print "Correctly caught TIMEOUT exception when raising TIMEOUT_PATTERN."
        else:
            self.fail('TIMEOUT_PATTERN not caught by an except TIMEOUT clause.')

    def test_pattern_printout (self):
        """Verify that an TIMEOUT_PATTERN returns the proper patterns it is trying to match against.
        Make sure it is returning the pattern from the correct call."""
        try:
            p = pexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Hello')
            p.expect('Goodbye',timeout=5)
        except pexpect.TIMEOUT_PATTERN, expTimeoutInst:
            timeoutAsString = expTimeoutInst.__str__()
            helloCount = timeoutAsString.count('Hello')
            goodbyeCount = timeoutAsString.count('Goodbye') 
            if (helloCount):
                self.fail("Pattern not for correct expect call.")
        else:
            self.fail("Did not generate an TIMEOUT_PATTERN exception.")

    def test_exp_timeout_notThrown (self):
        """Verify that an TIMEOUT_PATTERN is not thrown when we match what we expect."""
        try:
            p = pexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Hello')
        except pexpect.TIMEOUT_PATTERN:
            self.fail("TIMEOUT_PATTERN caught when it shouldn't be raised because we match the proper pattern.")
        
    def test_stacktraceMunging (self):
        """Verify that the stack trace returned with an TIMEOUT_PATTERN instance does not contain references to pexpect."""
        try:
            p = pexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Goodbye',timeout=5)
        except pexpect.TIMEOUT_PATTERN, expTimeoutInst:
            pexpectCount = expTimeoutInst.get_trace().count("pexpect")
            if (pexpectCount):
                self.fail("The TIMEOUT_PATTERN stacktrace referenced pexpect.")

    def test_correctStackTrace (self):
        """Verify that the stack trace returned with an TIMEOUT_PATTERN instance correctly handles function calls."""
        def nestedFunction (spawnInstance):
            spawnInstance.expect("junk",timeout=3)

        try:
            p = pexpect.spawn('cat')
            p.sendline('Hello')
            nestedFunction(p)
        except pexpect.TIMEOUT_PATTERN, expTimeoutInst:
            nestedFunctionCount = expTimeoutInst.get_trace().count("nestedFunction")
            if nestedFunctionCount == 0:
                self.fail("The TIMEOUT_PATTERN stacktrace did not show the call to the nestedFunction function." + str(expTimeoutInst))   

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(Exp_TimeoutTestCase,'test')
