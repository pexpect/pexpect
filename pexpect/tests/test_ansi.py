#!/usr/bin/env python

import ansi
import unittest

fill1_target='XXXXXXXXXX\n' + \
'XOOOOOOOOX\n' + \
'XO::::::OX\n' + \
'XO:oooo:OX\n' + \
'XO:o..o:OX\n' + \
'XO:o..o:OX\n' + \
'XO:oooo:OX\n' + \
'XO::::::OX\n' + \
'XOOOOOOOOX\n' + \
'XXXXXXXXXX\n'
fill2_target = 'XXXXXXXXXXX\n' + \
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
put_target = '\\.3.5.7.9/\n' + \
'.........2\n' + \
'3.........\n' + \
'.........4\n' + \
'5...\\/....\n' + \
'..../\\...6\n' + \
'7.........\n' + \
'.........8\n' + \
'9.........\n' + \
'/2.4.6.8.\\\n'
scroll_target = '\\.3.5.7.9/\n' + \
'\\.3.5.7.9/\n' + \
'\\.3.5.7.9/\n' + \
'\\.3.5.7.9/\n' + \
'5...\\/....\n' + \
'..../\\...6\n' + \
'/2.4.6.8.\\\n' + \
'/2.4.6.8.\\\n' + \
'/2.4.6.8.\\\n' + \
'/2.4.6.8.\\\n'
write_target = 'I\'ve got a ferret sticking up my nose.                           \n' +\
'(He\'s got a ferret sticking up his nose.)                        \n' +\
'How it got there I can\'t tell                                    \n' +\
'But now it\'s there it hurts like hell                            \n' +\
'And what is more it radically affects my sense of smell.         \n' +\
'(His sense of smell.)                                            \n'
write_text = 'I\'ve got a ferret sticking up my nose.\n' + \
'(He\'s got a ferret sticking up his nose.)\n' + \
'How it got there I can\'t tell\n' + \
'But now it\'s there it hurts like hell\n' + \
'And what is more it radically affects my sense of smell.\n' + \
'(His sense of smell.)\n' + \
'I can see a bare-bottomed mandril.\n' + \
'(Slyly eyeing his other nostril.)\n' + \
'If it jumps inside there too I really don\'t know what to do\n' + \
'I\'ll be the proud posessor of a kind of nasal zoo.\n' + \
'(A nasal zoo.)\n' + \
'I\'ve got a ferret sticking up my nose.\n' + \
'(And what is worst of all it constantly explodes.)\n' + \
'"Ferrets don\'t explode," you say\n' + \
'But it happened nine times yesterday\n' + \
'And I should know for each time I was standing in the way.\n' + \
'I\'ve got a ferret sticking up my nose.\n' + \
'(He\'s got a ferret sticking up his nose.)\n' + \
'How it got there I can\'t tell\n' + \
'But now it\'s there it hurts like hell\n' + \
'And what is more it radically affects my sense of smell.\n' + \
'(His sense of smell.)'

TETRIS_TARGET='                           XX            XXXX    XX                             \n' +\
'                           XXXXXX    XXXXXXXX    XX                             \n' +\
'                           XXXXXX    XXXXXXXX    XX                             \n' +\
'                           XX  XX    XX  XXXX    XX                             \n' +\
'                           XXXXXX  XXXX  XXXX    XX                             \n' +\
'                           XXXXXXXXXX    XXXX    XX                             \n' +\
'                           XX  XXXXXX      XX    XX                             \n' +\
'                           XXXXXX          XX    XX                             \n' +\
'                           XXXX    XXXXXX  XX    XX                             \n' +\
'                           XXXXXX    XXXX  XX    XX                             \n' +\
'                           XX  XX    XXXX  XX    XX                             \n' +\
'                           XX  XX      XX  XX    XX                             \n' +\
'                           XX  XX    XXXX  XXXX  XX                             \n' +\
'                           XXXXXXXX  XXXX  XXXX  XX                             \n' +\
'                           XXXXXXXXXXXXXX  XXXXXXXX                             \n' +\
'                           XX    XXXXXXXX  XX    XX                             \n' +\
'                           XXXXXXXXXXXXXX  XX    XX                             \n' +\
'                           XX  XXXX    XXXXXX    XX                             \n' +\
'                           XXXXXX          XXXXXXXX                             \n' +\
'                           XXXXXXXXXX      XX    XX                             \n' +\
'                           XXXXXXXXXXXXXXXXXXXXXXXX                             \n' +\
'                                                                                \n' +\
'  J->LEFT  K->ROTATE  L->RIGHT  SPACE->DROP  P->PAUSE  Q->QUIT                  \n' +\
'                                                                                \n'

class ansiFillTestCase (unittest.TestCase):

    def make_screen_with_put (self):
        s = ansi.screen(10,10)
        s.fill ('.')
        for r in range (1,s.rows + 1):
            if r % 2:
                s.put (r, 1, str(r))
            else:
                s.put (r, s.cols, str(r))
        for c in range (1,s.cols + 1):
            if c % 2:
                s.put (1, c, str(c))
            else:
                s.put (s.rows, c, str(c))
        s.put(1,1, '\\')
        s.put(1,s.cols, '/')
        s.put(s.rows,1,'/')
        s.put(s.rows, s.cols, '\\')
        s.put(5,5,'\\')
        s.put(5,6,'/')
        s.put(6,5,'/')
        s.put(6,6,'\\')
        return s

    def test_fill (self):
        s = ansi.screen (10,10)
        s.fill_region (10,1,1,10,'X')
        s.fill_region (2,2,9,9,'O')
        s.fill_region (8,8,3,3,':')
        s.fill_region (4,7,7,4,'o')
        s.fill_region (6,5,5,6,'.')
        assert str(s) == fill1_target

        s = ansi.screen (11,11)
        s.fill_region (1,1,11,11,'X')
        s.fill_region (2,2,10,10,'O')
        s.fill_region (9,9,3,3,':')
        s.fill_region (4,8,8,4,'o')
        s.fill_region (7,5,5,7,'.')
        s.fill_region (6,6,6,6,'+')
        assert str(s) == fill2_target
    def test_put (self):
        s = self.make_screen_with_put()
        assert str(s) == put_target
    def test_scroll (self):
        s = self.make_screen_with_put()
        s.scroll_screen_rows (1,4)
        s.scroll_down(); s.scroll_down(); s.scroll_down()
        s.scroll_down(); s.scroll_down(); s.scroll_down()
        s.scroll_screen_rows (7,10)
        s.scroll_up(); s.scroll_up(); s.scroll_up()
        s.scroll_up(); s.scroll_up(); s.scroll_up()
        assert str(s) == scroll_target
    def test_write (self):
        s = ansi.screen (6,65)
        s.fill('.')
        s.cursor_home()
        for c in write_text:
            s.write (c)
        assert str(s) == write_target
    def test_tetris (self)
        s = ansi.screen (24,80)
        tetris_text = open ('tetris.data').read()
        for c in tetris_text:
            s.write (c)
        assert str(s) == tetris_target

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ansiFillTestCase,'test')


