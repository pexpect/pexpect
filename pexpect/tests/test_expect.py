#!/usr/bin/env python
import pexpect
import unittest
import commands
import sys

class ExpectTestCase(unittest.TestCase):
    def setUp(self):
        print self.id()
    def test_exp (self):
        p = pexpect.spawn('cat')
        p.sendline ('Hello')
        p.sendline ('there')
        p.sendline ('Mr. Python')
        p.expect (['Hello'])
        p.expect (['there'])
        p.expect (['Mr. Python'])
        p.sendeof () 
        p.expect (pexpect.EOF)

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

    def test_expect_exact (self):
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

    def test_expect_eof (self):
        the_old_way = commands.getoutput('ls -l /bin')

        p = pexpect.spawn('ls -l /bin')
        p.expect(pexpect.EOF) # This basically tells it to read everything.
        the_new_way = p.before
        the_new_way = the_new_way.replace('\r','')
        the_new_way = the_new_way[:-1]

        assert the_old_way == the_new_way

    def test_expect_timeout (self):
        the_old_way = commands.getoutput('ls -l /bin')

        #p = pexpect.spawn('ls -l /bin')
        p = pexpect.spawn('ed')
        i = p.expect(pexpect.TIMEOUT) # This tells it to wait for timeout.
	assert p.after == pexpect.TIMEOUT

    def test_unexpected_eof (self):
        p = pexpect.spawn('ls -l /bin')
        try:
            p.expect('ZXYXZ') # Probably never see this in ls output.
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

