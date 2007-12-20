import signal, time, struct, fcntl, termios, os, sys

def getwinsize():
    """This returns the window size of the child tty.
    The return value is a tuple of (rows, cols).
    """
    if 'TIOCGWINSZ' in dir(termios):
        TIOCGWINSZ = termios.TIOCGWINSZ
    else:
        TIOCGWINSZ = 1074295912L # Assume
    s = struct.pack('HHHH', 0, 0, 0, 0)
    x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
    return struct.unpack('HHHH', x)[0:2]

def handler(signum, frame):
    print 'signal'
    sys.stdout.flush()
    print 'SIGWINCH:', getwinsize ()
    sys.stdout.flush()

print "setting handler for SIGWINCH"
signal.signal(signal.SIGWINCH, handler)

while 1:
    sys.stdout.flush()
    time.sleep(1)

