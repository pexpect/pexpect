#!/usr/bin/env python
import pexpect
import unittest
import commands

class ExpectTestCase(unittest.TestCase):
    #def runTest (self):
    def test_expectExact (self):
        the_old_way = commands.getoutput('/bin/ls -l')

	p = pexpect.spawn('/bin/ls -l')
	try:
		the_new_way = ''
		while 1:
			p.expect_exact ('\n')
			the_new_way = the_new_way + p.before# + '\n'
	except:
		the_new_way = the_new_way[:-1]
		the_new_way = the_new_way.replace('\r','\n')

	print type(the_old_way)
	print the_old_way
	print the_new_way

	fout = open('kill1','wb')
	fout.write(the_old_way)
	fout.close
	fout = open('kill2', 'wb')
	fout.write(the_new_way)
	fout.close
	assert the_old_way == the_new_way


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

