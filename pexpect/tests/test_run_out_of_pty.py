#!/usr/bin/env python
import pexpect
import unittest
import commands
import sys
import PexpectTestCase

class ExpectTestCase(PexpectTestCase.PexpectTestCase):
    # This takes too long to run and isn't all that interesting of a test.
    def OFF_test_run_out_of_pty (self):
        """This assumes that the tested platform has < 10000 pty devices.
        This test currently does not work under Solaris.
        Under Solaris it runs out of file descriptors first and
        ld.so starts to barf:
            ld.so.1: pt_chmod: fatal: /usr/lib/libc.so.1: Too many open files
        """
        plist=[]
        for count in range (0,10000):
                try:
                        plist.append (pexpect.spawn('ls -l'))
                except pexpect.ExceptionPexpect, e:
                        for c in range (0,count):
                            plist[c].close()
                        return
                except Exception, e:
                        self.fail ('Expected ExceptionPexpect. ' + str(e))
        self.fail ('Could not run out of pty devices. This may be OK.')

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

