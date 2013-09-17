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
            #self.pid, self.child_fd = posix.forkpty()
            self.pid, self.child_fd = pty.fork()
        except OSError as e:
            raise Exception('pty fork() failed: ' + str(e))

        if self.pid == 0: # Child
            os.execvp(command, args)

        # Parent


print '1'
x = s('ls', ['ls'])
time.sleep(5)
print '2'
result = os.read (x.child_fd, 5555)
print '3'
print result
print '4'

