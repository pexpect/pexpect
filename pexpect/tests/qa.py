#!/usr/bin/env python
import unittest
import commands
import sys
import gc
import os

import select
import signal
import traceback
import re
import struct
from types import *
import pty
import tty
import termios
import fcntl

class spawn:
    def __init__(self, command, args=None, timeout=30):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

	self.pid = self.child_fd = None
        try:
            self.pid, self.child_fd = pty.fork()
        except OSError, e:
            raise ExceptionPexpect('Pexpect: pty.fork() failed: ' + str(e))

        if self.pid == 0: # Child
            os.execvp(self.command, self.args)

        # Parent

    def __del__(self):
        if self.child_fd is not -1:
            os.close (self.child_fd)


def getstatusoutput(cmd, prf):
	"""Return (status, output) of executing cmd in a shell."""
	pipe = os.popen('{ ' + cmd + '; } 2>&1', 'r')
	text = pipe.read()
	if prf:
		print text
		print str (pipe)
	sys.stdout.flush()
	sts = pipe.close()
	if sts is None: sts = 0
	if text[-1:] == '\n': text = text[:-1]
	return sts, text

class ExpectTestCase(unittest.TestCase):
    def test_1 (self):
        the_old_way = getstatusoutput('/bin/ls -l', 0)[1]
	the_old_way = None
        p = spawn('/bin/ls -l')
	p = None
	gc.collect()

    def test_2 (self):
        #the_old_way = commands.getoutput('/bin/ls -l')
        the_old_way = getstatusoutput('/bin/ls -l', 1)[1]
	the_old_way = None

        p = spawn('/bin/ls -l')
	p = None
	gc.collect()
        
if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

#fout = open('delete_me_1','wb')
#fout.write(the_old_way)
#fout.close
#fout = open('delete_me_2', 'wb')
#fout.write(the_new_way)
#fout.close
foo = '''

    def test_expect (self):
        the_old_way = commands.getoutput('/bin/ls -l')

        p = spawn('/bin/ls -l')
        the_new_way = ''
        try:
                while 1:
                        p.expect ('\n')
                        the_new_way = the_new_way + p.before
        except:
                the_new_way = the_new_way[:-1]
                the_new_way = the_new_way.replace('\r','\n')

        assert the_old_way == the_new_way

    def test_unexpected_eof (self):
        p = spawn('/bin/ls -l')
        try:
            p.expect('ZXYXZ') # Probably never see this in ls output.
        except pexqa.EOF, e:
            pass
        else:
            self.fail ('Expected an EOF exception.')

'''
