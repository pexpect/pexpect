#!/usr/bin/env python
"""This demonstrates an FTP "bookmark".
This connects to an ftp site; does a few ftp stuff; and then gives the user
interactive control over the session. In this case the "bookmark" is to a
directory on the OpenBSD ftp server. It puts you in the i386 packages
directory. You can easily modify this for other sites.
"""
import pexpect
import sys

child = pexpect.spawn('/usr/bin/ftp ftp.openbsd.org')
child.expect('Name .*: ')
child.sendline('anonymous')
child.expect('Password:')
child.sendline('pexpect@sf.net')
child.expect('ftp> ')
child.sendline('cd /pub/OpenBSD/3.1/packages/i386')
child.expect('ftp> ')
child.sendline('bin')
child.expect('ftp> ')
child.sendline('prompt')
child.expect('ftp> ')
child.sendline('pwd')
child.expect('ftp> ')
print("Escape character is '^]'.\n")
sys.stdout.write (child.after)
sys.stdout.flush()
child.interact() # Escape character defaults to ^]

if child.isalive():
    child.sendline('bye')
    child.kill(1)
print 'Is Alive: ', child.isalive()

