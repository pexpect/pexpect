#!/usr/bin/env python
import pexpect
import unittest
import sys, os, time

class Exp_TimeoutTestCase(unittest.TestCase):
    def setUp(self):
        print self.id()
        unittest.TestCase.setUp(self)

    def test_matches_timeout (self):
        # Verify that rasing an EXP_TIMEOUT matches an except TIMEOUT clause.
        try:
            raise pexpect.EXP_TIMEOUT("TIMEOUT match test", "")
        except pexpect.TIMEOUT:
            pass
            #print "Correctly caught TIMEOUT exception when raising EXP_TIMEOUT."
        else:
            self.fail('EXP_TIMEOUT not caught by an except TIMEOUT clause.')

    def test_matches_exp_timeout (self):
        #This test should be trivial, I'm not sure how it could break but just including it for completeness.
        try:
            raise pexpect.EXP_TIMEOUT("EXP_TIMEOUT match test","")
        except pexpect.EXP_TIMEOUT:
            pass
            #print "Correctly caught EXP_TIMEOUT when raising EXP_TIMEOUT."
        else:
            self.fail('EXP_TIMEOUT not caught by an except EXP_TIMEOUT clause.')

    def test_pattern_printout (self):
        #Verify that an EXP_TIMEOUT returns the proper patterns it is trying to match against.
        # Make sure it is returning the pattern from the correct call.
        try:
            p = pexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Hello')
            p.expect('Goodbye',timeout=5)
        except pexpect.EXP_TIMEOUT, expTimeoutInst:
            timeoutAsString = expTimeoutInst.__str__()
            helloCount = timeoutAsString.count('Hello')
            goodbyeCount = timeoutAsString.count('Goodbye') 
            if (helloCount):
                self.fail("Pattern not for correct expect call.")
        else:
            self.fail("Did not generate an EXP_TIMEOUT exception.")

    def test_exp_timeout_notThrown (self):
        #Verify that an EXP_TIMEOUT is not thrown when we match what we expect.
        try:
            p = pexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Hello')
        except pexpect.EXP_TIMEOUT:
            self.fail("EXP_TIMEOUT caught when it shouldn't be raised because we match the proper pattern.")
        
    def test_stacktraceMunging (self):
        #Verify that the stack trace returned with an EXP_TIMEOUT instance does not contain references to pexpect.
        try:
            p = pexpect.spawn('cat')
            p.sendline('Hello')
            p.expect('Goodbye',timeout=5)
        except pexpect.EXP_TIMEOUT, expTimeoutInst:
            pexpectCount = expTimeoutInst.get_trace().count("pexpect")
            if (pexpectCount):
                self.fail("The EXP_TIMEOUT stacktrace referenced pexpect.")

    def test_correctStackTrace (self):
        #Verify that the stack trace returned with an EXP_TIMEOUT instance correctly handles function calls.
        def nestedFunction (spawnInstance):
            spawnInstance.expect("junk",timeout=3)

        try:
            p = pexpect.spawn('cat')
            p.sendline('Hello')
            nestedFunction(p)
        except pexpect.EXP_TIMEOUT, expTimeoutInst:
            nestedFunctionCount = expTimeoutInst.get_trace().count("nestedFunction")
            if not nestedFunctionCount:
                self.fail("The EXP_TIMEOUT stacktrace did not show the call to the nestedFunction function.")   

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(Exp_TimeoutTestCase,'test')
