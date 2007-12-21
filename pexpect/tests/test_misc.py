#!/usr/bin/env python
import pexpect
import unittest
import PexpectTestCase
import time
import os
import re

class TestCaseMisc(PexpectTestCase.PexpectTestCase):
        
    def test_isatty (self):
        child = pexpect.spawn('cat')
        assert child.isatty(), "Not returning True. Should always be True."
    def test_read (self):
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        child.sendeof()
        assert child.read(0) == '', "read(0) did not return ''"
        assert child.read(1) == 'a', "read(1) did not return 'a'"
        assert child.read(1) == 'b', "read(1) did not return 'b'"
        assert child.read(1) == 'c', "read(1) did not return 'c'"
        assert child.read(2) == '\r\n', "read(2) did not return '\\r\\n'"
        assert child.read() == 'abc\r\n', "read() did not return 'abc\\r\\n'"
    def test_readline (self):
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        child.sendline ("123")
        child.sendeof()
        assert child.readline(0) == '', "readline(0) did not return ''"
        assert child.readline() == 'abc\r\n', "readline() did not return 'abc\\r\\n'"
        assert child.readline(2) == 'abc\r\n', "readline(2) did not return 'abc\\r\\n'"
        assert child.readline(1) == '123\r\n', "readline(1) did not return '123\\r\\n'"
        assert child.readline() == '123\r\n', "readline() did not return '123\\r\\n'"
    def test_iter (self):
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        child.sendline ("123")
        child.sendeof()
        # Don't use "".join() because we want to test the ITERATOR.
        page = ""
        for line in child:
            page = page + line
        assert page == 'abc\r\nabc\r\n123\r\n123\r\n', "iterator did not work. page=%s"%repr(page)
    def test_readlines(self):
        child = pexpect.spawn('cat')
        child.sendline ("abc")
        child.sendline ("123")
        child.sendeof()
        page = child.readlines()
        page = ''.join(page)
        assert page == 'abc\r\nabc\r\n123\r\n123\r\n', "readlines() did not work. page=%s"%repr(page)
    def test_write (self):
        child = pexpect.spawn('cat')
        child.write('a')
        child.write('\r')
        assert child.readline() == 'a\r\n', "write() did not work"
    def test_writelines (self):
        child = pexpect.spawn('cat')
        child.writelines(['abc','123','xyz','\r'])
        child.sendeof()
        line = child.readline()
        assert line == 'abc123xyz\r\n', "writelines() did not work. line=%s"%repr(line)
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
    def test_bad_child_pid(self):
        child = pexpect.spawn('cat')
        child.terminate(force=1)
        child.terminated = 0 # Force invalid state to test code
        try:
            child.isalive()
        except pexpect.ExceptionPexpect, e:
            pass
        else:
            self.fail ("child.isalive() should have raised a pexpect.ExceptionPexpect")
        child.terminated = 1 # Force back to valid state so __del__ won't complain
    def test_bad_arguments (self):
        """This tests that we get a graceful error when passing bad arguments."""
        try:
            p = pexpect.spawn(1)
        except pexpect.ExceptionPexpect, e:
            pass
        else:
            self.fail ("pexpect.spawn(1) should have raised a pexpect.ExceptionPexpect.")
        try:
            p = pexpect.spawn('ls', '-la') # should really use pexpect.spawn('ls', ['-ls'])
        except TypeError, e:
            pass
        else:
            self.fail ("pexpect.spawn('ls', '-la') should have raised a TypeError.")
        try:
            p = pexpect.spawn('cat')
            p.close()
            p.read_nonblocking(size=1, timeout=3)
        except ValueError, e:
            pass
        else:
            self.fail ("read_nonblocking on closed spawn object should have raised a ValueError.")
    def test_isalive(self):
        child = pexpect.spawn('cat')
        assert child.isalive(), "child.isalive() did not return True"
        child.sendeof()
        child.expect(pexpect.EOF)
        assert not child.isalive(), "child.isalive() did not return False"
    def test_bad_type_in_expect(self):
        child = pexpect.spawn('cat')
        try:
            child.expect({}) # We don't support dicts yet. Should give TypeError
        except TypeError, e:
            pass
        else:
            self.fail ("child.expect({}) should have raised a TypeError")
    def test_winsize(self):
        child = pexpect.spawn('cat')
        child.setwinsize(10,13)
        assert child.getwinsize()==(10,13), "getwinsize() did not return (10,13)"
    def test_env(self):
        default = pexpect.run('env')
        userenv = pexpect.run('env', env={'foo':'pexpect'})
        assert default!=userenv, "'default' and 'userenv' should be different"
        assert 'foo' in userenv and 'pexpect' in userenv, "'foo' and 'pexpect' should be in 'userenv'"
    def test_cwd (self): # This assumes 'pwd' and '/tmp' exist on this platform.
        default = pexpect.run('pwd')
        tmpdir =  pexpect.run('pwd', cwd='/tmp')
        assert default!=tmpdir, "'default' and 'tmpdir' should be different"
        assert ('tmp' in tmpdir), "'tmp' should be returned by 'pwd' command"
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
        ss = pexpect.searcher_re ([re.compile('this'),re.compile('that'),re.compile('and'),re.compile('the'),re.compile('other')])
        assert ss.__str__() == 'searcher_re:\n    0: re.compile("this")\n    1: re.compile("that")\n    2: re.compile("and")\n    3: re.compile("the")\n    4: re.compile("other")'
        ss = pexpect.searcher_re ([pexpect.TIMEOUT,re.compile('this'),re.compile('that'),re.compile('and'),pexpect.EOF,re.compile('other')])
        assert ss.__str__() == 'searcher_re:\n    0: TIMEOUT\n    1: re.compile("this")\n    2: re.compile("that")\n    3: re.compile("and")\n    4: EOF\n    5: re.compile("other")'
    def test_searcher_string (self):
        ss = pexpect.searcher_string (['this','that','and','the','other'])
        assert ss.__str__() == 'searcher_string:\n    0: "this"\n    1: "that"\n    2: "and"\n    3: "the"\n    4: "other"', repr(ss.__str__())
        ss = pexpect.searcher_string (['this',pexpect.EOF,'that','and','the','other',pexpect.TIMEOUT])
        assert ss.__str__() == 'searcher_string:\n    0: "this"\n    1: EOF\n    2: "that"\n    3: "and"\n    4: "the"\n    5: "other"\n    6: TIMEOUT'

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseMisc,'test')

