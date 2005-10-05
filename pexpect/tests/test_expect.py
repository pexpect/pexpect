#!/usr/bin/env python
import pexpect
import unittest
import commands
import sys

# Many of these test cases blindly assume that sequential directory
# listings of the /bin directory will yield the same results.
# This may not be true, but seems adequate for testing now.
# I should fix this at some point.

class ExpectTestCase(unittest.TestCase):
    def setUp(self):
        print self.id()
        unittest.TestCase.setUp(self)

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

    def test_expect_index (self):
        p = pexpect.spawn('cat')
	p.sendline ('1234')
	index = p.expect (['abcd','xyz','1234',pexpect.EOF])
	assert index == 2
	p.sendline ('abcd')
	index = p.expect ([pexpect.TIMEOUT,'abcd','xyz','1234',pexpect.EOF])
	assert index == 1
	p.sendline ('xyz')
	print str(p)
	index = p.expect (['54321',pexpect.TIMEOUT,'abcd','xyz','1234',pexpect.EOF], timeout=5)
	print str(p)
	assert index == 3
	#p.sendline ('$*!@?')
	#index = p.expect (['54321',pexpect.TIMEOUT,'abcd','xyz','1234',pexpect.EOF], timeout=5)
	#assert index == 1
	#p.sendeof ()
	#index = p.expect (['54321',pexpect.TIMEOUT,'abcd','xyz','1234',pexpect.EOF], timeout=5)
	#assert index == 5

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
    def test_expect_eof (self):
        the_old_way = commands.getoutput('ls -l /bin')

        p = pexpect.spawn('ls -l /bin')
        p.expect(pexpect.EOF) # This basically tells it to read everything. Same as pexpect.run() function.
        the_new_way = p.before
        the_new_way = the_new_way.replace('\r','')
        the_new_way = the_new_way[:-1]

        assert the_old_way == the_new_way

    def test_expect_timeout (self):
        p = pexpect.spawn('ed')
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

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

#fout = open('delete_me_1','wb')
#fout.write(the_old_way)
#fout.close
#fout = open('delete_me_2', 'wb')
#fout.write(the_new_way)
#fout.close

