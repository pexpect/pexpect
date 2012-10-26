#!/usr/bin/env python
import pexpect
import pyunit

def main ():
	pid, fd = fooork ('aThelaDSjd','-i')
	print 'pid', pid
	print 'fd', fd
	Xexpect(fd, 'bash.*#',10)
	os.write(fd, 'scp -P 6666 *.py noah@gw.tiered.com:pexpect/\n')
	Xexpect(fd, 'bash.*#',10)
	os.write(fd, 'exit\n')
	print _my_read (fd, 1000, 5)
	sys.exit (1)

