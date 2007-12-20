#!/usr/bin/env python
import signal, time, struct, fcntl, termios, os, sys

# a dumb PAM will print the password prompt first then set ECHO
# False. What it should do it set ECHO False first then print the
# prompt. Otherwise, if we see the password prompt and type out
# password real fast before it turns off ECHO then some or all of
# our password might be visibly echod back to us. Sounds unlikely?
# It happens.

print "fake password:"
sys.stdout.flush()
time.sleep(3)
attr = termios.tcgetattr(sys.stdout)
attr[3] = attr[3] & ~termios.ECHO
termios.tcsetattr(sys.stdout, termios.TCSANOW, attr)
time.sleep(12)
attr[3] = attr[3] | termios.ECHO
termios.tcsetattr(sys.stdout, termios.TCSANOW, attr)
time.sleep(2)
