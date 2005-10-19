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

class ExpectTestCase (PexpectTestCase.PexpectTestCase):

    def Xtest_expect_basic (self):
        p = pexpect.spawn('cat')
        p.sendline ('Hello')
        p.sendline ('there')
        p.sendline ('Mr. Python')
        p.expect ('Hello')
        p.expect ('there')
        p.expect ('Mr. Python')
        p.sendeof () 
        p.expect (pexpect.EOF)

    def Xtest_expect_ignore_case(self):
        p = pexpect.spawn('cat')
        p.sendline ('HELLO')
        p.sendline ('there')
        p.expect ('(?i)hello')
        p.expect ('(?i)THERE')
        p.sendeof () 
        p.expect (pexpect.EOF)

    def Xtest_expect_order (self):
        """This tests that patterns are matched in the order of the pattern_list.
        """
        p = pexpect.spawn('cat')
        p.setecho(0) # Turn off tty echo
        p.sendline ('1234') # Should see this twice (once from tty echo and again from cat).
        p.sendline ('abcd') # Now, should only see this once.
        p.sendline ('wxyz') # This should also be only once.
        p.sendline ('7890') # Should see this twice.
        p.sendeof () 
        index = p.expect (['1234','abcd','wxyz',pexpect.EOF])
        assert index == 0, "index="+str(index)
        index = p.expect (['1234','abcd','wxyz',pexpect.EOF])
        assert index == 0, "index="+str(index)
        index = p.expect ([pexpect.EOF,pexpect.TIMEOUT,'abcd','wxyz','1234'])
        assert index == 2, "index="+str(index)
        index = p.expect (['54321',pexpect.TIMEOUT,'1234','abcd','wxyz',pexpect.EOF], timeout=5)
        assert index == 3, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 3, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 3, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 0, "index="+str(index)
        
    def test_expect_echo (self):
        """This tests that echo can be turned on and off.
        """
        p = pexpect.spawn('cat', timeout=10)
        p.sendline ('1234') # Should see this twice (once from tty echo and again from cat).
        p.setecho(0) # Turn off tty echo
        p.sendline ('abcd') # Now, should only see this once.
        p.sendline ('wxyz') # This should also be only once.
        p.setecho(1) # Turn on tty echo
        p.sendline ('7890') # Should see this twice.
        #p.sendeof () 
        index = p.expect (['1234','abcd','wxyz',pexpect.EOF,pexpect.TIMEOUT])
        assert index == 0, "index="+str(index)+"\n"+p.before
        index = p.expect (['1234','abcd','wxyz',pexpect.EOF])
        assert index == 0, "index="+str(index)
        index = p.expect ([pexpect.EOF,pexpect.TIMEOUT,'abcd','wxyz','1234'])
        assert index == 2, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 2, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 3, "index="+str(index)
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 3, "index="+str(index)
	p.sendeof()
        index = p.expect ([pexpect.EOF,'abcd','wxyz','7890'])
        assert index == 0, "index="+str(index)
 
    def Xtest_expect_index (self):
        """This tests that mixed list of regex strings, TIMEOUT, and EOF all
        return the correct index when matched.
        """
        #pdb.set_trace()
        p = pexpect.spawn('cat')
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

    def Xtest_expect (self):
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
        assert the_old_way == the_new_way

#    def test_expect_exact (self):
#        the_old_way = commands.getoutput('ls -l /bin')
#
#        p = pexpect.spawn('ls -l /bin')
#        the_new_way = ''
#        while 1:
#                i = p.expect (['\n', pexpect.EOF])
#                the_new_way = the_new_way + p.before
#                if i == 1:
#                        break
#        the_new_way = the_new_way[:-1]
#        the_new_way = the_new_way.replace('\r','\n')
#
#        assert the_old_way == the_new_way
#
    def Xtest_expect_eof (self):
        the_old_way = commands.getoutput('/bin/ls -l /bin')
        p = pexpect.spawn('/bin/ls -l /bin')
        p.expect(pexpect.EOF) # This basically tells it to read everything. Same as pexpect.run() function.
        the_new_way = p.before
        the_new_way = the_new_way.replace('\r','') # Remember, pty line endings are '\r\n'.
        the_new_way = the_new_way[:-1]
        assert the_old_way == the_new_way

    def Xtest_expect_timeout (self):
        p = pexpect.spawn('ed', timeout=10)
        i = p.expect(pexpect.TIMEOUT) # This tells it to wait for timeout.
        assert p.after == pexpect.TIMEOUT

    def Xtest_unexpected_eof (self):
        p = pexpect.spawn('ls -l /bin')
        try:
            p.expect('_Z_XY_XZ') # Probably never see this in ls output.
        except pexpect.EOF, e:
            pass
        else:
            self.fail ('Expected an EOF exception.')

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

#fout = open('delete_me_1','wb')
#fout.write(the_old_way)
#fout.close
#fout = open('delete_me_2', 'wb')
#fout.write(the_new_way)
#fout.close

