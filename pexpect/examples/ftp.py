#!/usr/bin/env python
'''This connects to an ftp site; does a few ftp stuff; and then gives the user interactive control over the session.
'''
import pexpect
import sys

child = pexpect.spawn('/usr/bin/ftp ftp.openbsd.org')
child.expect('Name .*: ')
child.sendline('anonymous')
child.expect('Password:')
child.sendline('noah@noah.org')
child.expect('ftp> ')
child.sendline('cd /pub/OpenBSD/2.9/packages/i386')
child.expect('ftp> ')
child.sendline('bin')
child.expect('ftp> ')
child.sendline('prompt')
child.expect('ftp> ')
child.sendline('pwd')
child.expect('ftp> ')
print("Escape character is '^]'.\n")
sys.stdout.write (child.matched)
sys.stdout.flush()
child.interact() # Escape character defaults to ^]

if child.isAlive():
    child.sendline('bye')
    child.kill(1)
print 'Is Alive: ', child.isAlive()

