#!/usr/bin/env python

# This single steps through a log file.

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

fin = open ('log', 'rb')
fout = open ('log2', 'wb')

while 1:
        foo = fin.read(1)
        if foo == '':
                sys.exit(0)
        sys.stdout.write(foo)
        getkey()
        fout.write (foo)
        fout.flush()

