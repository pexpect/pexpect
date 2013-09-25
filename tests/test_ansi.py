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
from pexpect import ANSI
import unittest
import PexpectTestCase

write_target = 'I\'ve got a ferret sticking up my nose.                           \n' +\
'(He\'s got a ferret sticking up his nose.)                        \n' +\
'How it got there I can\'t tell                                    \n' +\
'But now it\'s there it hurts like hell                            \n' +\
'And what is more it radically affects my sense of smell.         \n' +\
'(His sense of smell.)                                            '

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

tetris_target='                           XX            XXXX    XX                             \n' +\
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
'                                                                                '

torture_target='+--------------------------------------------------------------------------------+\n' +\
'|a`opqrs`      This is the       `srqpo`a                                        |\n' +\
'|VT100 series Torture Test Demonstration.                                        |\n' +\
'|VT100 series Torture Test Demonstration.                                        |\n' +\
'|This is a normal line __________________________________________________y_      |\n' +\
'|This is a bold line (normal unless the Advanced Video Option is installed)      |\n' +\
'|This line is underlined _ "       "       "       "       "       "    _y_      |\n' +\
'|This is a blinking line _ "       "       "       "       "       "    _y_      |\n' +\
'|This is inverse video _ (underlined if no AVO and cursor is underline) _y_      |\n' +\
'|Normal gjpqy Underline   Blink   Underline+Blink gjpqy                          |\n' +\
'|Bold   gjpqy Underline   Blink   Underline+Blink gjpqy                          |\n' +\
'|Inverse      Underline   Blink   Underline+Blink                                |\n' +\
'|Bold+Inverse Underline   Blink   Underline+Blink                                |\n' +\
'|This is double width                                                            |\n' +\
'|This is double height                                                           |\n' +\
'|This is double height                                                           |\n' +\
'|_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ioy                                        |\n' +\
'|_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ioy                                        |\n' +\
'|_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ioy                                        |\n' +\
'|`abcdefghijklmnopqrstuvwxyz{|}~ lqwqk                                           |\n' +\
'|`abcdefghijklmnopqrstuvwxyz{|}~ tqnqu                                           |\n' +\
'|`abcdefghijklmnopqrstuvwxyz{|}~ tqnqu                                           |\n' +\
'|`abcdefghijklmnopqrstuvwxyz{|}~ mqvqj                                           |\n' +\
'|   This test created by Joe Smith, 8-May-85                                     |\n' +\
'|                                                                                |\n' +\
'+--------------------------------------------------------------------------------+\n'

class ansiTestCase (PexpectTestCase.PexpectTestCase):
    def test_write (self):
        s = ANSI.ANSI (6,65)
        s.fill('.')
        s.cursor_home()
        for c in write_text:
            s.write (c)
        assert str(s) == write_target

    def test_torturet (self):
        s = ANSI.ANSI (24,80)
        with open('torturet.vt') as f:
            sample_text = f.read()
        for c in sample_text:
            s.process (c)
        assert s.pretty() == torture_target, 'processed: \n' + s.pretty() + '\nexpected:\n' + torture_target

    def test_tetris (self):
        s = ANSI.ANSI (24,80)
        with open('tetris.data') as f:
            tetris_text = f.read()
        for c in tetris_text:
            s.process (c)
        assert str(s) == tetris_target

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ansiTestCase,'test')

