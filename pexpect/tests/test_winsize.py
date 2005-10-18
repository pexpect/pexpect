#!/usr/bin/env python
import pexpect
import unittest
import PexpectTestCase
import time
import sys

class TestCaseWinsize(PexpectTestCase.PexpectTestCase):
    def setUp(self):
        print self.id()
        PexpectTestCase.PexpectTestCase.setUp(self)

    def test_winsize (self):
        """
        This tests that the child process can set and get the windows size.
        This makes use of an external script sigwinch_report.py.
        """
        print self.PYTHONBIN
        p1 = pexpect.spawn('%s sigwinch_report.py' % self.PYTHONBIN)
        time.sleep(1)
        p1.setwinsize (11,22)
        index = p1.expect ([pexpect.TIMEOUT, 'SIGWINCH: \(([0-9]*), ([0-9]*)\)'], timeout=10)
        if index == 0:
            self.fail ("TIMEOUT -- this platform may not support sigwinch properly.")
        r = p1.match.group(1)
        c = p1.match.group(2)
        assert (r=="11" and c=="22")
        time.sleep(1)
        p1.setwinsize (24,80)
        index = p1.expect ([pexpect.TIMEOUT, 'SIGWINCH: \(([0-9]*), ([0-9]*)\)'], timeout=10)
        if index == 0:
            self.fail ("TIMEOUT -- this platform may not support sigwinch properly.")
        r = p1.match.group(1)
        c = p1.match.group(2)
        assert (r=="24" and c=="80")
        #p1.send('\x03')
        p1.close(force=True)
        print p1.exitstatus

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseWinsize,'test')

