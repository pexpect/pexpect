#!/usr/bin/env python
import pexpect
import time

p = pexpect.spawn ('./a.out')
print p.exitstatus
p.expect (pexpect.EOF)
print p.before
time.sleep(1)
print 'exitstatus:', p.exitstatus
print 'isalive',p.isalive()
print 'exitstatus',p.exitstatus
print 'isalive',p.isalive()
print 'exitstatus',p.exitstatus

