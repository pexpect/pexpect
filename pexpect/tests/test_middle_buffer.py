#!/usr/bin/env python2
import expyct
import time

e = expyct.expyct ('/bin/sh -i')
e.timeout=60
e.expect(['#', '\$'])
e.send ('ls -la /\n')

i = e.expect (['foo','(d[aeiou]v)'])
print '\nRead before match>%s<' % e.before
print 'Matched:>%s<' % e.matched 
print 'index:', i

i = e.expect(['#', '\$'])
print '\nRead before match>%s<' % e.before
print 'Matched:>%s<' % e.matched
print 'index:', i
e.send('exit\n')
print 'Sent exit'
time.sleep(2)
print 'isAlive:', e.isAlive()

# This should test timeout...
i = e.expect ('#####')
print '\nRead before match>%s<' % e.before
print 'Matched:>%s<' % e.matched
print 'index:', i


