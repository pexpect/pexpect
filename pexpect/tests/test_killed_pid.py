#!/usr/bin/env python
import os, time, signal
import expyct

e = expyct.expyct ('/bin/sh', '-i')
print 'pid,fd:', e.pid, e.fd
print 'isAlive:', e.isAlive()
# Treat it brusquely.
print 'sending SIGKILL...'
os.kill (e.pid, signal.SIGKILL)
time.sleep (1)
print os.read(e.fd, 1000)
print 'isAlive:', e.isAlive()
e.expect('\#')
e.send ('ls -la /\n')
r,m,i = e.expect ('\#')
print r
