'''
This currently just holds some notes.
This is not expected to be working code.

$Revision$
$Date$
'''

import tty, termios, sys

def getkey():
    file = sys.stdin.fileno()
    mode = termios.tcgetattr(file)
    try:
        tty.setraw(file, termios.TCSANOW)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(file, termios.TCSANOW, mode)
    return ch

def test_typing ():
    s = screen (10,10)
    while 1:
        ch = getkey()
        s.type(ch)
        print str(s)
        print

