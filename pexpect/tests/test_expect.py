#!/usr/bin/env python
import pexpect
import unittest
import commands
import sys
import PexpectTestCase
#import pdb

# Many of these test cases blindly assume that sequential directory
# listings of the /bin directory will yield the same results.
# This may not be true, but seems adequate for testing now.
# I should fix this at some point.

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def hex_dump(src, length=16):
    result=[]
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       printable = s.translate(FILTER)
       result.append("%04X   %-*s   %s\n" % (i, length*3, hexa, printable))
    return ''.join(result)

class ExpectTestCase (PexpectTestCase.PexpectTestCase):

    def test_expect_basic (self):
        p = pexpect.spawn('cat')
        p.sendline ('Hello')
        p.sendline ('there')
        p.sendline ('Mr. Python')
        p.expect ('Hello')
        p.expect ('there')
        p.expect ('Mr. Python')
        p.sendeof () 
        p.expect (pexpect.EOF)

    def test_expect_exact_basic (self):
        p = pexpect.spawn('cat')
        p.sendline ('Hello')
        p.sendline ('there')
        p.sendline ('Mr. Python')
        p.expect_exact ('Hello')
        p.expect_exact ('there')
        p.expect_exact ('Mr. Python')
        p.sendeof () 
        p.expect_exact (pexpect.EOF)

    def test_expect_ignore_case(self):
        """This test that the ignorecase flag will match patterns
        even if case is different using the regex (?i) directive.
        """
        p = pexpect.spawn('cat')
        p.sendline ('HELLO')
        p.sendline ('there')
        p.expect ('(?i)hello')
        p.expect ('(?i)THERE')
        p.sendeof () 
        p.expect (pexpect.EOF)

    def test_expect_ignore_case_flag(self):
        """This test that the ignorecase flag will match patterns
        even if case is different using the ignorecase flag.
        """
        p = pexpect.spawn('cat')
        p.ignorecase = True
        p.sendline ('HELLO')
        p.sendline ('there')
        p.expect ('hello')
        p.expect ('THERE')
        p.sendeof () 
        p.expect (pexpect.EOF)

    def test_expect_order (self):
        """This tests that patterns are matched in the same order as given in the pattern_list.

        (Or does it?  Doesn't it also pass if expect() always chooses
        (one of the) the leftmost matches in the input? -- grahn)
        """
        p = pexpect.spawn('cat')
        self._expect_order(p)

    def test_expect_order_exact (self):
        """Like test_expect_order(), but using expect_exact().
        """
        p = pexpect.spawn('cat')
        p.expect = p.expect_exact
        self._expect_order(p)

    def _expect_order (self, p):
        p.sendline ('1234') 
        p.sendline ('abcd') 
        p.sendline ('wxyz') 
        p.sendline ('7890') 
        p.sendeof () 
        index = p.expect (['1234','abcd','wxyz',pexpect.EOF,'7890'])
        assert index == 0, "index="+str(index)
        index = p.expect (['1234','abcd','wxyz',pexpect.EOF,'7890'])
        assert index == 0, "index="+str(index)
        index = p.expect ([pexpect.EOF,pexpect.TIMEOUT,'wxyz','abcd','1234'])
        assert index == 3, "index="+str(index)
        index = p.expect (['54321',pexpect.TIMEOUT,'1234','abcd','wxyz',pexpect.EOF], timeout=5)
        assert index == 3, "index="+str(index)
        index = p.expect (['54321',pexpect.TIMEOUT,'1234','abcd','wxyz',pexpect.EOF], timeout=5)
        assert index == 4, "index="+str(index)
        index = p.expect (['54321',pexpect.TIMEOUT,'1234','abcd','wxyz',pexpect.EOF], timeout=5)
        assert index == 4, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 3, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 3, "index="+str(index)
        
    def test_waitnoecho (self):
        
        """ This tests that we can wait on a child process to set echo mode.
        For example, this tests that we could wait for SSH to set ECHO False
        when asking of a password. This makes use of an external script
        echo_wait.py. """

        p1 = pexpect.spawn('%s echo_wait.py' % self.PYTHONBIN)
        start = time.time()
        p1.waitnoecho(timeout=10)
        end_time = time.time() - start
        assert end_time < 10 and end_time > 2, "waitnoecho did not set ECHO off in the expected time window" 

    def test_expect_echo (self):
        """This tests that echo can be turned on and off.
        """
        p = pexpect.spawn('cat', timeout=10)
        self._expect_echo(p)

    def test_expect_echo_exact (self):
        """Like test_expect_echo(), but using expect_exact().
        """
        p = pexpect.spawn('cat', timeout=10)
        p.expect = p.expect_exact
        self._expect_echo(p)

    def _expect_echo (self, p):
        p.sendline ('1234') # Should see this twice (once from tty echo and again from cat).
        index = p.expect (['1234','abcd','wxyz',pexpect.EOF,pexpect.TIMEOUT])
        assert index == 0, "index="+str(index)+"\n"+p.before
        index = p.expect (['1234','abcd','wxyz',pexpect.EOF])
        assert index == 0, "index="+str(index)
        p.setecho(0) # Turn off tty echo
        p.sendline ('abcd') # Now, should only see this once.
        p.sendline ('wxyz') # Should also be only once.
        index = p.expect ([pexpect.EOF,pexpect.TIMEOUT,'abcd','wxyz','1234'])
        assert index == 2, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 2, "index="+str(index)
        p.setecho(1) # Turn on tty echo
        p.sendline ('7890') # Should see this twice.
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 3, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 3, "index="+str(index)
        p.sendeof()
 
    def test_expect_index (self):
        """This tests that mixed list of regex strings, TIMEOUT, and EOF all
        return the correct index when matched.
        """
        #pdb.set_trace()
        p = pexpect.spawn('cat')
        self._expect_index(p)

    def test_expect_index_exact (self):
        """Like test_expect_index(), but using expect_exact().
        """
        p = pexpect.spawn('cat')
        p.expect = p.expect_exact
        self._expect_index(p)

    def _expect_index (self, p):
        p.setecho(0)
        p.sendline ('1234')
        index = p.expect (['abcd','wxyz','1234',pexpect.EOF])
        assert index == 2, "index="+str(index)
        p.sendline ('abcd')
        index = p.expect ([pexpect.TIMEOUT,'abcd','wxyz','1234',pexpect.EOF])
        assert index == 1, "index="+str(index)
        p.sendline ('wxyz')
        index = p.expect (['54321',pexpect.TIMEOUT,'abcd','wxyz','1234',pexpect.EOF], timeout=5)
        assert index == 3, "index="+str(index) # Expect 'wxyz'
        p.sendline ('$*!@?')
        index = p.expect (['54321',pexpect.TIMEOUT,'abcd','wxyz','1234',pexpect.EOF], timeout=5)
        assert index == 1, "index="+str(index) # Expect TIMEOUT
        p.sendeof ()
        index = p.expect (['54321',pexpect.TIMEOUT,'abcd','wxyz','1234',pexpect.EOF], timeout=5)
        assert index == 5, "index="+str(index) # Expect EOF

    def test_expect (self):
        the_old_way = commands.getoutput('ls -l /bin')
        p = pexpect.spawn('ls -l /bin')
        the_new_way = ''
        while 1:
            i = p.expect (['\n', pexpect.EOF])
            the_new_way = the_new_way + p.before
            if i == 1:
                break
        the_new_way = the_new_way[:-1]
        the_new_way = the_new_way.replace('\r','\n')
        # For some reason I get an extra newline under OS X evey once in a while.
        # I found it by looking through the hex_dump().
        assert the_old_way == the_new_way, hex_dump(the_new_way) + "\n" + hex_dump(the_old_way)

    def test_expect_exact (self):
        the_old_way = commands.getoutput('ls -l /bin')
        p = pexpect.spawn('ls -l /bin')
        the_new_way = ''
        while 1:
            i = p.expect_exact (['\n', pexpect.EOF])
            the_new_way = the_new_way + p.before
            if i == 1:
                break
        the_new_way = the_new_way[:-1]
        the_new_way = the_new_way.replace('\r','\n')
        assert the_old_way == the_new_way, repr(the_old_way) + '\n' + repr(the_new_way)
        p = pexpect.spawn('echo hello.?world')
        i = p.expect_exact('.?')
        assert p.before == 'hello' and p.after == '.?'

    def test_expect_eof (self):
        the_old_way = commands.getoutput('/bin/ls -l /bin')
        p = pexpect.spawn('/bin/ls -l /bin')
        p.expect(pexpect.EOF) # This basically tells it to read everything. Same as pexpect.run() function.
        the_new_way = p.before
        the_new_way = the_new_way.replace('\r','') # Remember, pty line endings are '\r\n'.
        the_new_way = the_new_way[:-1]
        assert the_old_way == the_new_way

    def test_expect_timeout (self):
        p = pexpect.spawn('ed', timeout=10)
        i = p.expect(pexpect.TIMEOUT) # This tells it to wait for timeout.
        assert p.after == pexpect.TIMEOUT

    def test_unexpected_eof (self):
        p = pexpect.spawn('ls -l /bin')
        try:
            p.expect('_Z_XY_XZ') # Probably never see this in ls output.
        except pexpect.EOF, e:
            pass
        else:
            self.fail ('Expected an EOF exception.')

    def _before_after(self, p):
        p.timeout = 5

        p.expect('>>> ')
        self.assertEqual(p.after, '>>> ')
        self.assert_(p.before.startswith('Python '))

        p.sendline('range(4*3)')

        p.expect('5')
        self.assertEqual(p.after, '5')
        self.assert_(p.before.startswith('range(4*3)'))

        p.expect('>>> ')
        self.assertEqual(p.after, '>>> ')
        self.assert_(p.before.startswith(', 6, 7, 8'))

    def test_before_after(self):
        """This tests expect() for some simple before/after things.
        """
        p = pexpect.spawn(self.PYTHONBIN)
        self._before_after(p)

    def test_before_after_exact(self):
        """This tests some simple before/after things, for
        expect_exact(). (Grahn broke it at one point.)
        """
        p = pexpect.spawn(self.PYTHONBIN)
        # mangle the spawn so we test expect_exact() instead
        p.expect = p.expect_exact
        self._before_after(p)

    def _ordering(self, p):
        p.timeout = 5
        p.expect('>>> ')

        p.sendline('range(4*3)')
        self.assertEqual(p.expect(['5,', '5,']), 0)
        p.expect('>>> ')

        p.sendline('range(4*3)')
        self.assertEqual(p.expect(['7,', '5,']), 1)
        p.expect('>>> ')

        p.sendline('range(4*3)')
        self.assertEqual(p.expect(['5,', '7,']), 0)
        p.expect('>>> ')

        p.sendline('range(4*5)')
        self.assertEqual(p.expect(['2,', '12,']), 0)
        p.expect('>>> ')

        p.sendline('range(4*5)')
        self.assertEqual(p.expect(['12,', '2,']), 1)

    def test_ordering(self):
        """This tests expect() for which pattern is returned
        when many may eventually match. I (Grahn) am a bit
        confused about what should happen, but this test passes
        with pexpect 2.1.
        """
        p = pexpect.spawn(self.PYTHONBIN)
        self._ordering(p)

    def test_ordering_exact(self):
        """This tests expect_exact() for which pattern is returned
        when many may eventually match. I (Grahn) am a bit
        confused about what should happen, but this test passes
        for the expect() method with pexpect 2.1.
        """
        p = pexpect.spawn(self.PYTHONBIN)
        # mangle the spawn so we test expect_exact() instead
        p.expect = p.expect_exact
        self._ordering(p)

    def _greed(self, p):
        p.timeout = 5
        p.expect('>>> ')
        p.sendline('import time')
        p.expect('>>> ')
        # the newline and sleep will (I hope) guarantee that
        # pexpect is fed two distinct batches of data,
        # "foo\r\n" + "bar\r\n".
        foo_then_bar = 'print "f"+"o"+"o" ; time.sleep(3); print "b"+"a"+"r"'

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect(['foo\r\nbar']), 0)
        p.expect('>>> ')

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect(['\r\nbar']), 0)
        p.expect('>>> ')

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect(['foo\r\nbar', 'foo', 'bar']), 1)
        p.expect('>>> ')

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect(['foo', 'foo\r\nbar', 'foo', 'bar']), 0)
        p.expect('>>> ')

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect(['bar', 'foo\r\nbar']), 1)
        p.expect('>>> ')

        # If the expect works as if we rematch for every new character,
        # 'o\r\nb' should win over 'oo\r\nba'. The latter is longer and
        # matches earlier in the input, but isn't satisfied until the 'a'
        # arrives.
        # However, pexpect doesn't do that (version 2.1 didn't).
        p.sendline(foo_then_bar)
        self.assertEqual(p.expect(['oo\r\nba', 'o\r\nb']), 0)
        p.expect('>>> ')

        # distinct patterns, but both suddenly match when the 'r' arrives.
        p.sendline(foo_then_bar)
        self.assertEqual(p.expect(['foo\r\nbar', 'ar']), 0)
        p.expect('>>> ')

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect(['ar', 'foo\r\nbar']), 1)
        p.expect('>>> ')

    def test_greed(self):
        p = pexpect.spawn(self.PYTHONBIN)
        self._greed(p)

    def test_greed_exact(self):
        p = pexpect.spawn(self.PYTHONBIN)
        # mangle the spawn so we test expect_exact() instead
        p.expect = p.expect_exact
        self._greed(p)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

#fout = open('delete_me_1','wb')
#fout.write(the_old_way)
#fout.close
#fout = open('delete_me_2', 'wb')
#fout.write(the_new_way)
#fout.close

