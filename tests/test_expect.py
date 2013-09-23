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
from __future__ import with_statement  # bring 'with' stmt to py25
import pexpect
import unittest
import subprocess
import time
import PexpectTestCase
from pexpect import six
import platform
import sys
#import pdb

# Many of these test cases blindly assume that sequential directory
# listings of the /bin directory will yield the same results.
# This may not be true, but seems adequate for testing now.
# I should fix this at some point.

# query: For some reason an extra newline occures under OS X evey
# once in a while. Excessive uses of .replace resolve these

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def hex_dump(src, length=16):
    result=[]
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       printable = s.translate(FILTER)
       result.append("%04X   %-*s   %s\n" % (i, length*3, hexa, printable))
    return ''.join(result)

def hex_diff(left, right):
        diff = ['< %s\n> %s' % (_left, _right,) for _left, _right in zip(
            hex_dump(left).splitlines(), hex_dump(right).splitlines())
            if _left != _right]
        return '\n' + '\n'.join(diff,)


class ExpectTestCase (PexpectTestCase.PexpectTestCase):

    def test_expect_basic (self):
        p = pexpect.spawn('cat')
        p.sendline (six.b('Hello'))
        p.sendline (six.b('there'))
        p.sendline (six.b('Mr. Python'))
        p.expect (six.b('Hello'))
        p.expect (six.b('there'))
        p.expect (six.b('Mr. Python'))
        p.sendeof ()
        p.expect (pexpect.EOF)

    def test_expect_exact_basic (self):
        p = pexpect.spawn('cat')
        p.sendline (six.b('Hello'))
        p.sendline (six.b('there'))
        p.sendline (six.b('Mr. Python'))
        p.expect_exact (six.b('Hello'))
        p.expect_exact (six.b('there'))
        p.expect_exact (six.b('Mr. Python'))
        p.sendeof ()
        p.expect_exact (pexpect.EOF)

    def test_expect_ignore_case(self):
        '''This test that the ignorecase flag will match patterns
        even if case is different using the regex (?i) directive.
        '''
        p = pexpect.spawn('cat')
        p.sendline (six.b('HELLO'))
        p.sendline (six.b('there'))
        p.expect (six.b('(?i)hello'))
        p.expect (six.b('(?i)THERE'))
        p.sendeof ()
        p.expect (pexpect.EOF)

    def test_expect_ignore_case_flag(self):
        '''This test that the ignorecase flag will match patterns
        even if case is different using the ignorecase flag.
        '''
        p = pexpect.spawn('cat')
        p.ignorecase = True
        p.sendline (six.b('HELLO'))
        p.sendline (six.b('there'))
        p.expect (six.b('hello'))
        p.expect (six.b('THERE'))
        p.sendeof ()
        p.expect (pexpect.EOF)

    def test_expect_order (self):
        '''This tests that patterns are matched in the same order as given in the pattern_list.

        (Or does it?  Doesn't it also pass if expect() always chooses
        (one of the) the leftmost matches in the input? -- grahn)
        '''
        p = pexpect.spawn('cat')
        self._expect_order(p)

    def test_expect_order_exact (self):
        '''Like test_expect_order(), but using expect_exact().
        '''
        p = pexpect.spawn('cat')
        p.expect = p.expect_exact
        self._expect_order(p)

    def _expect_order (self, p):
        p.sendline (six.b('1234'))
        p.sendline (six.b('abcd'))
        p.sendline (six.b('wxyz'))
        p.sendline (six.b('7890'))
        p.sendeof ()
        index = p.expect ([
            six.b('1234'),
            six.b('abcd'),
            six.b('wxyz'),
            pexpect.EOF,
            six.b('7890') ])
        assert index == 0, "index="+str(index)
        index = p.expect ([
            six.b('1234'),
            six.b('abcd'),
            six.b('wxyz'),
            pexpect.EOF,
            six.b('7890') ])
        assert index == 0, "index="+str(index)
        index = p.expect ([
            pexpect.EOF,
            pexpect.TIMEOUT,
            six.b('wxyz'),
            six.b('abcd'),
            six.b('1234') ])
        assert index == 3, "index="+str(index)
        index = p.expect ([
            six.b('54321'),
            pexpect.TIMEOUT,
            six.b('1234'),
            six.b('abcd'),
            six.b('wxyz'),
            pexpect.EOF], timeout=5)
        assert index == 3, "index="+str(index)
        index = p.expect ([
            six.b('54321'),
            pexpect.TIMEOUT,
            six.b('1234'),
            six.b('abcd'),
            six.b('wxyz'),
            pexpect.EOF], timeout=5)
        assert index == 4, "index="+str(index)
        index = p.expect ([
            six.b('54321'),
            pexpect.TIMEOUT,
            six.b('1234'),
            six.b('abcd'),
            six.b('wxyz'),
            pexpect.EOF], timeout=5)
        assert index == 4, "index="+str(index)
        index = p.expect ([
            pexpect.EOF,
            six.b('abcd'),
            six.b('wxyz'),
            six.b('7890') ])
        assert index == 3, "index="+str(index)
        index = p.expect ([
            pexpect.EOF,
            six.b('abcd'),
            six.b('wxyz'),
            six.b('7890') ])
        assert index == 3, "index="+str(index)

    def test_waitnoecho (self):

        ''' This tests that we can wait on a child process to set echo mode.
        For example, this tests that we could wait for SSH to set ECHO False
        when asking of a password. This makes use of an external script
        echo_wait.py. '''

        p1 = pexpect.spawn('%s echo_wait.py' % self.PYTHONBIN)
        start = time.time()
        p1.waitnoecho(timeout=10)
        end_time = time.time() - start
        assert end_time < 10 and end_time > 2, "waitnoecho did not set ECHO off in the expected window of time."

        # test that we actually timeout and return False if ECHO is never set off.
        p1 = pexpect.spawn('cat')
        start = time.time()
        retval = p1.waitnoecho(timeout=4)
        end_time = time.time() - start
        assert end_time > 3, "waitnoecho should have waited longer than 2 seconds. retval should be False, retval=%d"%retval
        assert retval==False, "retval should be False, retval=%d"%retval

        # This one is mainly here to test default timeout for code coverage.
        p1 = pexpect.spawn('%s echo_wait.py' % self.PYTHONBIN)
        start = time.time()
        p1.waitnoecho()
        end_time = time.time() - start
        assert end_time < 10, "waitnoecho did not set ECHO off in the expected window of time."

    def test_expect_echo (self):
        '''This tests that echo can be turned on and off.
        '''
        p = pexpect.spawn('cat', timeout=10)
        self._expect_echo(p)

    def test_expect_echo_exact (self):
        '''Like test_expect_echo(), but using expect_exact().
        '''
        p = pexpect.spawn('cat', timeout=10)
        p.expect = p.expect_exact
        self._expect_echo(p)

    def _expect_echo (self, p):
        p.sendline (six.b('1234')) # Should see this twice (once from tty echo and again from cat).
        index = p.expect ([
            six.b('1234'),
            six.b('abcd'),
            six.b('wxyz'),
            pexpect.EOF,
            pexpect.TIMEOUT])
        assert index == 0, "index="+str(index)+"\n"+p.before
        index = p.expect ([
            six.b('1234'),
            six.b('abcd'),
            six.b('wxyz'),
            pexpect.EOF])
        assert index == 0, "index="+str(index)
        p.setecho(0) # Turn off tty echo
        p.sendline (six.b('abcd')) # Now, should only see this once.
        p.sendline (six.b('wxyz')) # Should also be only once.
        index = p.expect ([
            pexpect.EOF,
            pexpect.TIMEOUT,
            six.b('abcd'),
            six.b('wxyz'),
            six.b('1234')])
        assert index == 2, "index="+str(index)
        index = p.expect ([
            pexpect.EOF,
            six.b('abcd'),
            six.b('wxyz'),
            six.b('7890')])
        assert index == 2, "index="+str(index)
        p.setecho(1) # Turn on tty echo
        p.sendline (six.b('7890')) # Should see this twice.
        index = p.expect ([pexpect.EOF,six.b('abcd'),six.b('wxyz'),six.b('7890')])
        assert index == 3, "index="+str(index)
        index = p.expect ([pexpect.EOF,six.b('abcd'),six.b('wxyz'),six.b('7890')])
        assert index == 3, "index="+str(index)
        p.sendeof()

    def test_expect_index (self):
        '''This tests that mixed list of regex strings, TIMEOUT, and EOF all
        return the correct index when matched.
        '''
        #pdb.set_trace()
        p = pexpect.spawn('cat')
        self._expect_index(p)

    def test_expect_index_exact (self):
        '''Like test_expect_index(), but using expect_exact().
        '''
        p = pexpect.spawn('cat')
        p.expect = p.expect_exact
        self._expect_index(p)

    def _expect_index (self, p):
        p.setecho(0)
        p.sendline (six.b('1234'))
        index = p.expect ([six.b('abcd'),six.b('wxyz'),six.b('1234'),pexpect.EOF])
        assert index == 2, "index="+str(index)
        p.sendline (six.b('abcd'))
        index = p.expect ([pexpect.TIMEOUT,six.b('abcd'),six.b('wxyz'),six.b('1234'),pexpect.EOF])
        assert index == 1, "index="+str(index)
        p.sendline (six.b('wxyz'))
        index = p.expect ([six.b('54321'),pexpect.TIMEOUT,six.b('abcd'),six.b('wxyz'),six.b('1234'),pexpect.EOF], timeout=5)
        assert index == 3, "index="+str(index) # Expect 'wxyz'
        p.sendline (six.b('$*!@?'))
        index = p.expect ([six.b('54321'),pexpect.TIMEOUT,six.b('abcd'),six.b('wxyz'),six.b('1234'),pexpect.EOF], timeout=5)
        assert index == 1, "index="+str(index) # Expect TIMEOUT
        p.sendeof ()
        index = p.expect ([six.b('54321'),pexpect.TIMEOUT,six.b('abcd'),six.b('wxyz'),six.b('1234'),pexpect.EOF], timeout=5)
        assert index == 5, "index="+str(index) # Expect EOF

    def test_expect (self):
        the_old_way = subprocess.Popen(args=['ls', '-l', '/bin'],
                stdout=subprocess.PIPE).communicate()[0].rstrip()
        p = pexpect.spawn('ls -l /bin')
        the_new_way = six.b('')
        while 1:
            i = p.expect ([six.b('\n'), pexpect.EOF])
            the_new_way = the_new_way + p.before
            if i == 1:
                break
        the_new_way = the_new_way.rstrip()
        the_new_way = the_new_way.replace(six.b('\r\n'), six.b('\n')
                ).replace(six.b('\r'), six.b('\n')).replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.replace(six.b('\r\n'), six.b('\n')
                ).replace(six.b('\r'), six.b('\n')).replace('\n\n', '\n').rstrip()
        assert the_old_way == the_new_way, hex_diff(the_old_way, the_new_way)

    def test_expect_exact (self):
        the_old_way = subprocess.Popen(args=['ls', '-l', '/bin'],
                stdout=subprocess.PIPE).communicate()[0].rstrip()
        p = pexpect.spawn('ls -l /bin')
        the_new_way = six.b('')
        while 1:
            i = p.expect_exact ([six.b('\n'), pexpect.EOF])
            the_new_way = the_new_way + p.before
            if i == 1:
                break
        the_new_way = the_new_way.replace(six.b('\r\n'), six.b('\n')
                ).replace(six.b('\r'), six.b('\n')).replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.replace(six.b('\r\n'), six.b('\n')
                ).replace(six.b('\r'), six.b('\n')).replace('\n\n', '\n').rstrip()
        assert the_old_way == the_new_way, hex_diff(the_old_way, the_new_way)
        p = pexpect.spawn('echo hello.?world')
        i = p.expect_exact(six.b('.?'))
        self.assertEqual(p.before, six.b('hello'))
        self.assertEqual(p.after, six.b('.?'))

    def test_expect_eof (self):
        the_old_way = subprocess.Popen(args=['/bin/ls', '-l', '/bin'],
                stdout=subprocess.PIPE).communicate()[0].rstrip()
        p = pexpect.spawn('/bin/ls -l /bin')
        p.expect(pexpect.EOF) # This basically tells it to read everything. Same as pexpect.run() function.
        the_new_way = p.before
        the_new_way = the_new_way.replace(six.b('\r\n'), six.b('\n')
                ).replace(six.b('\r'), six.b('\n')).replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.replace(six.b('\r\n'), six.b('\n')
                ).replace(six.b('\r'), six.b('\n')).replace('\n\n', '\n').rstrip()
        assert the_old_way == the_new_way, hex_diff(the_old_way, the_new_way)

    def test_expect_timeout (self):
        p = pexpect.spawn('cat', timeout=5)
        i = p.expect(pexpect.TIMEOUT) # This tells it to wait for timeout.
        self.assertEqual(p.after, pexpect.TIMEOUT)

    def test_unexpected_eof (self):
        p = pexpect.spawn('ls -l /bin')
        try:
            p.expect('_Z_XY_XZ') # Probably never see this in ls output.
        except pexpect.EOF:
            pass
        else:
            self.fail ('Expected an EOF exception.')

    def _before_after(self, p):
        p.timeout = 5

        p.expect(six.b('>>> '))
        self.assertEqual(p.after, six.b('>>> '))
        assert p.before.startswith(six.b('Python ')), p.before

        p.sendline(six.b('list(range(4*3))'))

        p.expect(six.b('5'))
        self.assertEqual(p.after, six.b('5'))
        assert p.before.startswith(six.b('list(range(4*3))')), p.before

        p.expect(six.b('>>> '))
        self.assertEqual(p.after, six.b('>>> '))
        assert p.before.startswith(six.b(', 6, 7, 8')), p.before

    def test_before_after(self):
        '''This tests expect() for some simple before/after things.
        '''
        p = pexpect.spawn(self.PYTHONBIN)
        self._before_after(p)

    def test_before_after_exact(self):
        '''This tests some simple before/after things, for
        expect_exact(). (Grahn broke it at one point.)
        '''
        p = pexpect.spawn(self.PYTHONBIN)
        # mangle the spawn so we test expect_exact() instead
        p.expect = p.expect_exact
        self._before_after(p)

    def _ordering(self, p):
        p.timeout = 5
        p.expect(six.b('>>> '))

        p.sendline('list(range(4*3))')
        self.assertEqual(p.expect([six.b('5,'), six.b('5,')]), 0)
        p.expect(six.b('>>> '))

        p.sendline(six.b('list(range(4*3))'))
        self.assertEqual(p.expect([six.b('7,'), six.b('5,')]), 1)
        p.expect(six.b('>>> '))

        p.sendline(six.b('list(range(4*3))'))
        self.assertEqual(p.expect([six.b('5,'), six.b('7,')]), 0)
        p.expect(six.b('>>> '))

        p.sendline(six.b('list(range(4*5))'))
        self.assertEqual(p.expect([six.b('2,'), six.b('12,')]), 0)
        p.expect(six.b('>>> '))

        p.sendline(six.b('list(range(4*5))'))
        self.assertEqual(p.expect([six.b('12,'), six.b('2,')]), 1)

    def test_ordering(self):
        '''This tests expect() for which pattern is returned
        when many may eventually match. I (Grahn) am a bit
        confused about what should happen, but this test passes
        with pexpect 2.1.
        '''
        p = pexpect.spawn(self.PYTHONBIN)
        self._ordering(p)

    def test_ordering_exact(self):
        '''This tests expect_exact() for which pattern is returned
        when many may eventually match. I (Grahn) am a bit
        confused about what should happen, but this test passes
        for the expect() method with pexpect 2.1.
        '''
        p = pexpect.spawn(self.PYTHONBIN)
        # mangle the spawn so we test expect_exact() instead
        p.expect = p.expect_exact
        self._ordering(p)

    def _greed(self, p):
        p.timeout = 5
        p.expect(six.b('>>> '))
        p.sendline(six.b('import time'))
        p.expect(six.b('>>> '))
        # the newline and sleep will (I hope) guarantee that
        # pexpect is fed two distinct batches of data,
        # "foo\r\n" + "bar\r\n".
        foo_then_bar = six.b('print("f"+"o"+"o") ; time.sleep(1); print("b"+"a"+"r")')

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect([six.b('foo\r\nbar')]), 0)
        p.expect(six.b('>>> '))

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect([six.b('\r\nbar')]), 0)
        p.expect(six.b('>>> '))

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect([six.b('foo\r\nbar'), six.b('foo'), six.b('bar')]), 1)
        p.expect(six.b('>>> '))

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect([six.b('foo'), six.b('foo\r\nbar'), six.b('foo'), six.b('bar')]), 0)
        p.expect(six.b('>>> '))

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect([six.b('bar'), six.b('foo\r\nbar')]), 1)
        p.expect(six.b('>>> '))

        # If the expect works as if we rematch for every new character,
        # 'o\r\nsix.b(' should win over ')oo\r\nba'. The latter is longer and
        # matches earlier in the input, but isn't satisfied until the 'a'
        # arrives.
        # However, pexpect doesn't do that (version 2.1 didn't).
        p.sendline(foo_then_bar)
        self.assertEqual(p.expect([six.b('oo\r\nba'), six.b('o\r\nb')]), 0)
        p.expect(six.b('>>> '))

        # distinct patterns, but both suddenly match when the 'r' arrives.
        p.sendline(foo_then_bar)
        self.assertEqual(p.expect([six.b('foo\r\nbar'), six.b('ar')]), 0)
        p.expect(six.b('>>> '))

        p.sendline(foo_then_bar)
        self.assertEqual(p.expect([six.b('ar'), six.b('foo\r\nbar')]), 1)
        p.expect(six.b('>>> '))

        try:
            p.expect(12345)
            assert False, 'TypeError should have been raised'
        except TypeError:
            err = sys.exc_info()[1]
            e_msg = "pattern is <type 'int'> at position 0, must be one of"
            if hasattr(err, 'message'):
                assert err.message.startswith(e_msg), err.message
            else:
                assert str(err).startswith(e_msg), err

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

#fout = open('delete_me_1','wsix.b(')
#fout.write(the_old_way)
#fout.close
#fout = open(')delete_me_2', 'wsix.b(')
#fout.write(the_new_way)
#fout.close

