import time, struct, fcntl, termios, os, sys
import signal, os

def getwinsize():
    s = struct.pack('HHHH', 0, 0, 0, 0)
    x = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
    return struct.unpack('HHHH', x)[0:2]

def handler(signum, frame):
    print 'SIGWINCH:', getwinsize ()

signal.signal(signal.SIGWINCH, handler)

while 1:
        time.sleep(10)

