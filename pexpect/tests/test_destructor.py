#!/usr/bin/env python
import pexpect
import unittest
import gc

class TestCaseDestructor(unittest.TestCase):
    #def runTest (self):
        
    def test_destructor (self):
        p1 = pexpect.spawn('ls -l')
        p2 = pexpect.spawn('ls -l')
        p3 = pexpect.spawn('ls -l')
        fd_t1 = (p1.child_fd,p2.child_fd,p3.child_fd)
        p1 = None
        p2 = None
        p3 = None
        gc.collect()
        p1 = pexpect.spawn('ls -l')
        p2 = pexpect.spawn('ls -l')
        p3 = pexpect.spawn('ls -l')
        fd_t2 = (p1.child_fd,p2.child_fd,p3.child_fd)
        del (p1)
        del (p3)
        del (p2)
        gc.collect()
        p1 = pexpect.spawn('ls -l')
        p2 = pexpect.spawn('ls -l')
        p3 = pexpect.spawn('ls -l')
        fd_t3 = (p1.child_fd,p2.child_fd,p3.child_fd)

        assert (fd_t1 == fd_t2 == fd_t3)


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseDestructor,'test')

