#!/usr/bin/env python
import pexpect
import unittest
import PexpectTestCase
import gc
import time

class TestCaseDestructor(PexpectTestCase.PexpectTestCase):
    def test_destructor (self):
        p1 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p2 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p3 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p4 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        fd_t1 = (p1.child_fd,p2.child_fd,p3.child_fd,p4.child_fd)
        p1.expect(pexpect.EOF)
        p2.expect(pexpect.EOF)
        p3.expect(pexpect.EOF)
        p4.expect(pexpect.EOF)
        p1.kill(9)
        p2.kill(9)
        p3.kill(9)
        p4.kill(9)
        p1 = None
        p2 = None
        p3 = None
        p4 = None
        gc.collect()
        time.sleep(3) # Some platforms are slow at gc... Solaris!

        p1 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p2 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p3 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p4 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        fd_t2 = (p1.child_fd,p2.child_fd,p3.child_fd,p4.child_fd)
        p1.kill(9)
        p2.kill(9)
        p3.kill(9)
        p4.kill(9)
        del (p1)
        del (p2)
        del (p3)
        del (p4)
        gc.collect()
        time.sleep(3)

        p1 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p2 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p3 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        p4 = pexpect.spawn('%s hello_world.py' % self.PYTHONBIN)
        fd_t3 = (p1.child_fd,p2.child_fd,p3.child_fd,p4.child_fd)

        assert (fd_t1 == fd_t2 == fd_t3), "pty file descriptors not properly garbage collected (fd_t1,fd_t2,fd_t3)=(%s,%s,%s)" % (str(fd_t1),str(fd_t2),str(fd_t3))


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseDestructor,'test')

