import os, sys
import select
import signal
import traceback
import time
import re
import struct
from types import *
import posix

import pty
import tty
import termios
import fcntl
class s:
    def __init__(self, command, args=None, timeout=30):

	self.pid = self.child_fd = None
        try:
            self.pid, self.child_fd = posix.forkpty()
            #self.pid, self.child_fd = pty.fork()
        except OSError, e:
            raise Exception('posix.fork() failed: ' + str(e))

        if self.pid == 0: # Child
            os.execvp(command, args)

        # Parent


print '1'
x = s('ls', ['ls'])
time.sleep(5)
print '2'
some = os.read (x.child_fd, 3225)
print '3'
print some
print '4'

