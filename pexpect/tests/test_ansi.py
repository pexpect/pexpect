#!/usr/bin/env python

import ansi
import unittest

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

class ansiTestCase (unittest.TestCase):

    def test_write (self):
        s = ansi.ansi (6,65)
        s.fill('.')
        s.cursor_home()
        for c in write_text:
            s.write (c)
        print str(s)
        assert str(s) == write_target
   # def test_tetris (self):
   #     s = ansi.ansi (24,80)
   #     tetris_text = open ('tetris.data').read()
   #     for c in tetris_text:
   #         s.write (c)
   #     assert str(s) == tetris_target

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ansiTestCase,'test')


