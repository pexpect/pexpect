#!/usr/bin/env python
import pexpect
import unittest
import PexpectTestCase
import time

class TestCaseWinsize(PexpectTestCase.PexpectTestCase):
    def setUp(self):
        print self.id()

    def test_winsize (self):
	"""
	This tests that the child process can set and get the windows size.
        This makes use of an external script sigwinch_report.py.
        """
	p1 = pexpect.spawn('%s sigwinch_report.py' % self.PYTHONBIN)
	time.sleep(1)
	p1.setwinsize (11,22)
	p1.expect ('SIGWINCH: \(([0-9]*), ([0-9]*)\)')
	r = p1.match.group(1)
	c = p1.match.group(2)
	assert (r=="11" and c=="22")
	time.sleep(1)
	p1.setwinsize (24,80)
	p1.expect ('SIGWINCH: \(([0-9]*), ([0-9]*)\)')
	r = p1.match.group(1)
	c = p1.match.group(2)
	assert (r=="24" and c=="80")

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseWinsize,'test')

