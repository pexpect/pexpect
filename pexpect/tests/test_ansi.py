#!/usr/bin/env python

import ansi
import unittest

s1_target='XXXXXXXXXX\n' + \
'XOOOOOOOOX\n' + \
'XO::::::OX\n' + \
'XO:oooo:OX\n' + \
'XO:o..o:OX\n' + \
'XO:o..o:OX\n' + \
'XO:oooo:OX\n' + \
'XO::::::OX\n' + \
'XOOOOOOOOX\n' + \
'XXXXXXXXXX\n'
s2_target = 'XXXXXXXXXXX\n' + \
'XOOOOOOOOOX\n' + \
'XO:::::::OX\n' + \
'XO:ooooo:OX\n' + \
'XO:o...o:OX\n' + \
'XO:o.+.o:OX\n' + \
'XO:o...o:OX\n' + \
'XO:ooooo:OX\n' + \
'XO:::::::OX\n' + \
'XOOOOOOOOOX\n' + \
'XXXXXXXXXXX\n'

class ansiFillTestCase (unittest.TestCase):
    def testansiFill (self):
	s = ansi.screen (10,10)
	s.fill_region (10,1,1,10,'X')
	s.fill_region (2,2,9,9,'O')
	s.fill_region (8,8,3,3,':')
	s.fill_region (4,7,7,4,'o')
	s.fill_region (6,5,5,6,'.')
	assert str(s) == s1_target

	s = ansi.screen (11,11)
	s.fill_region (1,1,11,11,'X')
	s.fill_region (2,2,10,10,'O')
	s.fill_region (9,9,3,3,':')
	s.fill_region (4,8,8,4,'o')
	s.fill_region (7,5,5,7,'.')
	s.fill_region (6,6,6,6,'+')
	assert str(s) == s2_target

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ansiFillTestCase,'test')


