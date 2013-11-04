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
import unittest
import PexpectTestCase
import os, sys
import re
import signal
import time

# the program cat(1) may display ^D\x08\x08 when \x04 (EOF, Ctrl-D) is sent
_CAT_EOF = b'^D\x08\x08'

class TestCaseMisc(PexpectTestCase.PexpectTestCase):

    def test_isatty (self):
        child = pexpect.spawn('cat')
        assert child.isatty(), "Not returning True. Should always be True."

    def test_read (self):
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        child.sendeof()
        self.assertEqual(child.read(0), b'')
        self.assertEqual(child.read(1), b'a')
        self.assertEqual(child.read(1), b'b')
        self.assertEqual(child.read(1), b'c')
        self.assertEqual(child.read(2), b'\r\n')
        remaining = child.read().replace(_CAT_EOF, b'')
        self.assertEqual(remaining, b'abc\r\n')

    def test_readline (self):
        '''See the note in test_readlines() for an explaination as to why
        I allow line3 and line4 to return multiple patterns.
        Basically, this is done to handle a valid condition on slow systems.
        '''
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        time.sleep(0.5)
        child.sendline ("123")
        time.sleep(0.5)
        child.sendeof()
        line1 = child.readline(0)
        line2 = child.readline()
        line3 = child.readline(2)
        line4 = child.readline(1)
        line5 = child.readline()
        time.sleep(1) # time for child to "complete" ;/
        assert not child.isalive(), child.isalive()
        assert child.exitstatus == 0, child.exitstatus
        self.assertEqual(line1, b'')
        self.assertEqual(line2, b'abc\r\n')
        assert (line3 == b'abc\r\n' or line3 == b'123\r\n'), line3
        assert (line4 == b'123\r\n' or line4 == b'abc\r\n'), line4
        self.assertEqual(line5, b'123\r\n')

    def test_iter (self):
        '''See the note in test_readlines() for an explaination as to why
        I allow line3 and line4 to return multiple patterns.
        Basically, this is done to handle a valid condition on slow systems.
        '''
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        time.sleep(0.5)
        child.sendline ("123")
        time.sleep(0.5)
        child.sendeof()
        # Don't use ''.join() because we want to test the ITERATOR.
        page = b''
        for line in child:
            page += line
        page = page.replace(_CAT_EOF, b'')
        # This is just a really bad test all together, we should write our
        # own 'cat' utility that only writes to stdout after EOF is recv,
        # this must take into consideration all possible platform impl.'s
        # of `cat', and their related terminal and line-buffer handling
        assert (page == b'abc\r\nabc\r\n123\r\n123\r\n' or
                page == b'abc\r\n123\r\nabc\r\n123\r\n' or
                page == b'abc\r\n123abc\r\n\r\n123\r\n') , \
               "iterator did not work. page=%r"(page,)

    def test_readlines(self):
        '''Note that on some slow or heavily loaded systems that the lines
        coming back from 'cat' may come even after the EOF.
        We except to see two copies of the lines we send 'cat'.
        The first line is the TTY echo, the second line is from 'cat'.
        Usually 'cat' will respond with 'abc' before we have a chance to
        send the second line, '123'. If this does not happen then the
        lines may appear out of order. This is technically not an error.
        That's just the nature of asynchronous communication.
        This is why the assert will allow either of the two possible
        patterns to be returned by lineslined(). The (lame) alternative is
        to put a long sleep between the two sendline() calls, but then
        I have to make assumptions about how fast 'cat' can reply.
        '''
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        time.sleep(0.5)
        child.sendline ("123")
        time.sleep(0.5)
        child.sendeof()
        page = b''.join(child.readlines()).replace(_CAT_EOF, b'')
        assert (page == b'abc\r\nabc\r\n123\r\n123\r\n' or
                page == b'abc\r\n123\r\nabc\r\n123\r\n'), (
               "readlines() did not work. page=%r" % (page,))

        time.sleep(1) # time for child to "complete" ;/
        assert not child.isalive(), child.isalive()
        assert child.exitstatus == 0, child.exitstatus

    def test_write (self):
        child = pexpect.spawn('cat')
        child.write('a')
        child.write('\r')
        self.assertEqual(child.readline(), b'a\r\n')

    def test_writelines (self):
        child = pexpect.spawn('cat')
        child.writelines(['abc','123','xyz','\r'])
        child.sendeof()
        line = child.readline()
        assert line == b'abc123xyz\r\n', (
            "writelines() did not work. line=%r" % (line,))

    def test_eof(self):
        child = pexpect.spawn('cat')
        child.sendeof()
        try:
            child.expect ('the unexpected')
        except:
            pass
        assert child.eof(), "child.eof() did not return True"

    def test_terminate(self):
        child = pexpect.spawn('cat')
        child.terminate(force=1)
        assert child.terminated, "child.terminated is not True"

    def test_sighup(self):
        # If a parent process sets an Ignore handler for SIGHUP (as on Fedora's
        # build machines), this test breaks. We temporarily restore the default
        # handler, so the child process will quit. However, we can't simply
        # replace any installed handler, because getsignal returns None for
        # handlers not set in Python code, so we wouldn't be able to restore
        # them.
        if signal.getsignal(signal.SIGHUP) == signal.SIG_IGN:
            signal.signal(signal.SIGHUP, signal.SIG_DFL)
            restore_sig_ign = True
        else:
            restore_sig_ign = False

        try:
            child = pexpect.spawn(sys.executable + ' getch.py', ignore_sighup=True)
            child.expect('READY')
            child.kill(signal.SIGHUP)
            for _ in range(10):
                if not child.isalive():
                    raise AssertionError('Child should not have exited.')
                time.sleep(0.1)

            child = pexpect.spawn(sys.executable + ' getch.py', ignore_sighup=False)
            child.expect('READY')
            child.kill(signal.SIGHUP)
            for _ in range(10):
                if not child.isalive():
                    break
                time.sleep(0.1)
            else:
                raise AssertionError('Child should have exited.')

        finally:
            if restore_sig_ign:
                signal.signal(signal.SIGHUP, signal.SIG_IGN)

    def test_bad_child_pid(self):
        child = pexpect.spawn('cat')
        child.terminate(force=1)
        child.terminated = 0 # Force invalid state to test code
        try:
            child.isalive()
        except pexpect.ExceptionPexpect:
            pass
        else:
            self.fail ("child.isalive() should have raised a pexpect.ExceptionPexpect")
        child.terminated = 1 # Force back to valid state so __del__ won't complain
    def test_bad_arguments (self):
        '''This tests that we get a graceful error when passing bad arguments.'''
        try:
            p = pexpect.spawn(1)
        except pexpect.ExceptionPexpect:
            pass
        else:
            self.fail ("pexpect.spawn(1) should have raised a pexpect.ExceptionPexpect.")
        try:
            p = pexpect.spawn('ls', '-la') # should really use pexpect.spawn('ls', ['-ls'])
        except TypeError:
            pass
        else:
            self.fail ("pexpect.spawn('ls', '-la') should have raised a TypeError.")
        try:
            p = pexpect.spawn('cat')
            p.close()
            p.read_nonblocking(size=1, timeout=3)
        except ValueError:
            pass
        else:
            self.fail ("read_nonblocking on closed spawn object should have raised a ValueError.")
    def test_isalive(self):
        child = pexpect.spawn('cat')
        assert child.isalive(), child.isalive()
        child.sendeof()
        child.expect(pexpect.EOF)
        assert not child.isalive(), child.isalive()
    def test_bad_type_in_expect(self):
        child = pexpect.spawn('cat')
        try:
            child.expect({}) # We don't support dicts yet. Should give TypeError
        except TypeError:
            pass
        else:
            self.fail ("child.expect({}) should have raised a TypeError")

    def test_env(self):
        default = pexpect.run('env')
        userenv = pexpect.run('env', env={'foo':'pexpect'})
        assert default!=userenv, "'default' and 'userenv' should be different"
        assert b'foo' in userenv and b'pexpect' in userenv, "'foo' and 'pexpect' should be in 'userenv'"

    def test_cwd (self): # This assumes 'pwd' and '/tmp' exist on this platform.
        default = pexpect.run('pwd')
        tmpdir =  pexpect.run('pwd', cwd='/tmp')
        assert default!=tmpdir, "'default' and 'tmpdir' should be different"
        assert (b'tmp' in tmpdir), "'tmp' should be returned by 'pwd' command"

    def test_which (self):
        p = os.defpath
        ep = os.environ['PATH']
        os.defpath = ":/tmp"
        os.environ['PATH'] = ":/tmp"
        wp = pexpect.which ("ticker.py")
        assert wp == 'ticker.py', "Should return a string. Returned %s" % wp
        os.defpath = "/tmp"
        os.environ['PATH'] = "/tmp"
        wp = pexpect.which ("ticker.py")
        assert wp == None, "Executable should not be found. Returned %s" % wp
        os.defpath = p
        os.environ['PATH'] = ep

    def test_searcher_re (self):
        # This should be done programatically, if we copied and pasted output,
        # there wouldnt be a whole lot to test, really, other than our ability
        # to copy and paste correctly :-)
        ss = pexpect.searcher_re ([
            re.compile('this'), re.compile('that'),
            re.compile('and'), re.compile('the'),
            re.compile('other') ])
        out = ('searcher_re:\n    0: re.compile("this")\n    '
               '1: re.compile("that")\n    2: re.compile("and")\n    '
               '3: re.compile("the")\n    4: re.compile("other")')
        assert ss.__str__() == out, (ss.__str__(), out)
        ss = pexpect.searcher_re ([
            pexpect.TIMEOUT, re.compile('this'),
            re.compile('that'), re.compile('and'),
            pexpect.EOF,re.compile('other')
            ])
        out = ('searcher_re:\n    0: TIMEOUT\n    1: re.compile("this")\n    '
               '2: re.compile("that")\n    3: re.compile("and")\n    '
               '4: EOF\n    5: re.compile("other")')
        assert ss.__str__() == out, (ss.__str__(), out)

    def test_searcher_string (self):
        ss = pexpect.searcher_string ([
            'this', 'that', 'and', 'the', 'other' ])
        out = ('searcher_string:\n    0: "this"\n    1: "that"\n    '
               '2: "and"\n    3: "the"\n    4: "other"')
        assert ss.__str__() == out, (ss.__str__(), out)
        ss = pexpect.searcher_string ([
            'this', pexpect.EOF, 'that', 'and',
            'the', 'other', pexpect.TIMEOUT ])
        out = ('searcher_string:\n    0: "this"\n    1: EOF\n    '
               '2: "that"\n    3: "and"\n    4: "the"\n    '
               '5: "other"\n    6: TIMEOUT')
        assert ss.__str__() == out, (ss.__str__(), out)

    def test_nonnative_pty_fork(self):
        class spawn_ourptyfork(pexpect.spawn):
            def _spawn(self, command, args=[]):
                self.use_native_pty_fork = False
                pexpect.spawn._spawn(self, command, args)

        p = spawn_ourptyfork('cat')
        p.sendline('abc')
        p.expect('abc')
        p.sendeof()

    def test_exception_tb(self):
        p = pexpect.spawn('sleep 1')
        try:
            p.expect('BLAH')
        except pexpect.ExceptionPexpect as e:
            # get_trace should filter out frames in pexpect's own code
            tb = e.get_trace()
            assert 'raise ' not in tb, tb
        else:
            assert False, "Should have raised an exception."

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseMisc,'test')

