#!/usr/bin/env python
import pexpect
import unittest
import commands
import sys

class ExpectTestCase(unittest.TestCase):
    #def runTest (self):
        
    def test_expect (self):
        the_old_way = commands.getoutput('ls -l')

        p = pexpect.spawn('ls -l')
        the_new_way = ''
        try:
                while 1:
                        p.expect ('\n')
                        the_new_way = the_new_way + p.before
        except:
                the_new_way = the_new_way[:-1]
                the_new_way = the_new_way.replace('\r','\n')

        assert the_old_way == the_new_way

    def test_expect_exact (self):
        the_old_way = commands.getoutput('ls -l')

        p = pexpect.spawn('ls -l')
        try:
                the_new_way = ''
                while 1:
                        p.expect_exact ('\n')
                        the_new_way = the_new_way + p.before
        except:
                the_new_way = the_new_way[:-1]
                the_new_way = the_new_way.replace('\r','\n')

        assert the_old_way == the_new_way

    def test_expect_eof (self):
        the_old_way = commands.getoutput('ls -l')

        p = pexpect.spawn('ls -l')
        p.expect(pexpect.EOF) # This basically tells it to read everything.
        the_new_way = p.before
        the_new_way = the_new_way.replace('\r','')
        the_new_way = the_new_way[:-1]

        assert the_old_way == the_new_way

    def test_unexpected_eof (self):
        p = pexpect.spawn('ls -l')
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

