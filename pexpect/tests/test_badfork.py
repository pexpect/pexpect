#!/usr/bin/env python
import select
import os,sys, struct
import errno
import time
import pty, tty, termios, fcntl
import traceback
import re
from types import *

def main ():
	pid, fd = fooork ('aThelaDSjd','-i')
	print 'pid', pid
	print 'fd', fd
	Xexpect(fd, 'bash.*#',10)
	os.write(fd, 'scp -P 6666 *.py noah@gw.tiered.com:expyct/\n')
	Xexpect(fd, 'bash.*#',10)
	os.write(fd, 'exit\n')
	print _my_read (fd, 1000, 5)
	sys.exit (1)

def setwinsize(r,c):
        # Assume ws_xpixel and ws_ypixel are zero.
        s = struct.pack("HHHH", r,c,0,0)
        x = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, s)

def fooork (command, args):
	'''This is fooork -- Foo Ork. Ork foo.
	'''
	pid, fd = pty.fork()
	if pid == 0: # Child
		setwinsize (80,24)
		os.execlp (command, command, args)
		print 'Well, something went wrong. Here I am after an execlp.' 
	return (pid, fd)

def _my_read (fd, n, timeout=None):
	'''This is a non-blocking wrapper around os.read.
	it uses select.select to supply a timeout. Note that if
	this is called with timeout=None (the default) then this
	actually MAY block.
	'''
	try:
		(r,w,e) = select.select ([fd], [], [], timeout)
		if not r:
			print 'TIMEOUT'
			return -1
		if fd in r:
			temp = os.read(fd, n)
			if temp == '':
				#print 'EOF'
				pass
			return temp
		print 'Something weird happened.'
		return -2
	except Exception, e:
		print 'Exception in _read'
		print str(e)
	return -3

def expect_eof (fd, timeout=None):
	pass

def __expect_posix (fd, re_list, timeout=None):
	done = 0
	result = ""	

#	blocking (fin)
	while not done:
		try:
			partial = _my_read(fd, 1, timeout)
			result = result + partial
			index = 0
			for cre in re_list:
				match_result = cre.search(result)
				if match_result is not None:
					done = cre.pattern
					matched_pattern = cre.pattern
					done = 1
					print 'found!'
				else:
					index = index + 1
					
				#done = 1
				#print 'Weird NOT found!'
		except:
			done = 1
			print 'NOT found EXCEPT!'
#			sys.stderr = sys.stdout
			traceback.print_exc()
			time.sleep (10)

	#nonblocking (fin)
	return result

def Xexpect (fin, pattern, timeout=None):
	"""This searches through the stream for a pattern. 
	The search is non-blocking so this works with pipes.
	The input pattern may be a string or a list of strings.
	The first pattern matched will cause a return.
	The reuturn value is a tuple (i,pat) where i is the
	index of the pattern in the list and pat is the
	actual matched pattern. If no pattern is matched then
	i will be -1 and pat will be None.
	"""

	if type(pattern) is ListType:
		cpat_list = map (lambda x: re.compile(x[0]), pattern)
	elif type(pattern) is StringType:
		cpat_list = [ re.compile(pattern) ]
	else:
		raise TypeError, 'pattern argument is not a string or list.'

	# This is not strictly correct since pty is not POSIX. Alas...
	if os.name == 'posix':
		return __expect_posix (fin, cpat_list, 10)
	else:
		raise OSError, 'Pypect will not work with this operating system: "%s".' % os.name
	

if __name__ == '__main__':
	main()
