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
child.sendline('pexpect@sourceforge.net')
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
# At this point this script blocks until the user presses the escape character
# or until the child exits. The human user and the child should be talking
# to each other now.

# At this point the script is running again.
print 'Left interact mode.'

#
# The rest is not strictly necessary. This just demonstrates a few functions.
# This makes sure the child is dead; although it would be killed when Python exits.
#
if child.isalive():
    child.sendline('bye') # Try to ask ftp child to exit.
    child.kill(1) # Then try to force it.
# Print the final state of the child. Normally isalive() should be FALSE.
print
if child.isalive():
    print 'Child did not exit gracefully.'
else:
    print 'Child exited gracefully.'


