#!/usr/bin/env python
'''
PEXPECT LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012, Noah Spurrier <noah@noah.org>
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''
import pexpect
from pexpect import fdpexpect
import tempfile
import resource
import unittest
from . import PexpectTestCase
import os


class TestFdexpect(PexpectTestCase.PexpectTestCase):
    """
    Test pexpect.fdexpect.fdspawn() wrapper.
    """

    def setUp(self):
        PexpectTestCase.PexpectTestCase.setUp(self)

    def test_fd (self):
        fd = os.open ('TESTDATA.txt', os.O_RDONLY)
        s = fdpexpect.fdspawn (fd)
        s.expect(b'This is the end of test data:')
        s.expect(pexpect.EOF)
        self.assertEqual(s.before, b' END\n')

    def test_maxread (self):
        fd = os.open ('TESTDATA.txt', os.O_RDONLY)
        s = fdpexpect.fdspawn (fd)
        s.maxread = 100
        s.expect('2')
        s.expect ('This is the end of test data:')
        s.expect (pexpect.EOF)
        self.assertEqual(s.before, b' END\n')

    def test_fd_isalive (self):
        fd = os.open ('TESTDATA.txt', os.O_RDONLY)
        s = fdpexpect.fdspawn(fd)
        assert s.isalive()
        os.close(fd)
        assert not s.isalive(), "Should not be alive after close()"

    def test_fd_isatty (self):
        fd = os.open ('TESTDATA.txt', os.O_RDONLY)
        s = fdpexpect.fdspawn (fd)
        assert not s.isatty()
        s.close()

    def test_fileobj(self):
        f = open('TESTDATA.txt', 'r')
        s = fdpexpect.fdspawn(f)  # Should get the fileno from the file handle
        s.expect('2')
        s.close()
        assert not s.isalive()
        s.close()  # Smoketest - should be able to call this again


class DescriptorLeakTestCase(PexpectTestCase.PexpectTestCase):
    """
    Test possibility of file descriptor leakage
    """
    #: ensure we have N number of open files available when limiting the
    #: maximum number of open files for the current process. Prior to
    #: forcefully closing the subprocess pipe on EOF, looping exactly
    #: MAX_FILENO_BUMP is sufficient to reproduce the error.
    MAX_FILENO_BUMP = 10

    def setUp(self):
        # assuming each file we open increments the file descriptor digit by
        # one, create a temporary file, and assume we already have N files
        # open, before setting a new limit of (N + 10).

        # By artificially setting our soft limit, we forcefully cause a
        # "too many open files" if there are any file descriptor leaks much
        # earlier than otherwise.  On OSX, my default is 2,560 -- it would be
        # a very long while until such limit is reached!
        with tempfile.TemporaryFile() as fp:
            MAX_NOFILES = fp.fileno() + self.MAX_FILENO_BUMP
        self.save_limit_nofiles = resource.getrlimit(resource.RLIMIT_NOFILE)
        _, hard = self.save_limit_nofiles
        resource.setrlimit(resource.RLIMIT_NOFILE, (MAX_NOFILES, hard))
        PexpectTestCase.PexpectTestCase.setUp(self)

    def tearDown(self):
        # restore (soft) max. num of open files limit
        resource.setrlimit(resource.RLIMIT_NOFILE, self.save_limit_nofiles)

    def test_donot_reach_max_ptys_caught_EOF(self):
        """
        Ensure spawning many subprocesses does not leak file descriptors.

        Ensure that we do not depend on python's garbage collector to call
        our __del__ method to subsequently "close" the object, and that
        explicitly closing our object at EOF ensures we do not eventually
        meet "pty.fork() failed: out of pty devices."
        """
        for _ in range(self.MAX_FILENO_BUMP * 2):
            child = pexpect.spawn('/bin/cat', timeout=3)
            child.sendeof()
            try:
                child.expect(['something', pexpect.TIMEOUT])
            except pexpect.EOF:
                pass

    def test_donot_reach_max_ptys_expect_exact_EOF(self):
        """
        Ensure spawning many subprocesses does not leak file descriptors.

        Behavior of catching EOF is different when it is .expect()ed directly.
        """
        for _ in range(self.MAX_FILENO_BUMP * 2):
            child = pexpect.spawn('/bin/cat', timeout=3)
            child.sendeof()
            child.expect_exact(pexpect.EOF)

    def test_donot_reach_max_ptys_expect_includes_EOF(self):
        """
        Ensure spawning many subprocesses does not leak file descriptors.

        Behavior of catching EOF is different when it is expected by a list
        of matches where EOF is included.
        """
        for _ in range(self.MAX_FILENO_BUMP * 2):
            child = pexpect.spawn('/bin/cat', timeout=3)
            child.sendline('alpha')
            child.sendline('beta')
            child.sendline('omega')
            child.sendline('gamma')
            child.sendline('delta')
            child.sendeof()

            # match some substrings, with EOF mixed in. We shouldn't
            # yet reach EOF (even though we likely have, internally)
            # in our return patterns.
            assert child.expect([pexpect.EOF, 'alpha', 'beta']) == 1
            assert child.expect(['omega', pexpect.EOF]) == 0
            assert child.expect([pexpect.EOF, 'gamma']) == 1

            # forcefully exhaust our search, reaching EOF
            assert child.expect([pexpect.EOF]) == 0

            # and you'll only get EOF thereon.
            assert child.expect(['delta', pexpect.EOF]) == 1


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestFdexpect, 'test')
