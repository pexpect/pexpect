#!/usr/bin/env python
'''This connects to an ftp site; does a few ftp stuff; and then gives the user interactive control over the session.
'''
import pexpect
import sys

child = pexpect.spawn('/usr/bin/ftp upload.sourceforge.net')
child.expect('Name .*: ')
child.sendline('anonymous')
child.expect('Password:')
child.sendline('noah@noah.org')
child.expect('ftp> ')
child.sendline('cd /incoming')
child.expect('ftp> ')
child.sendline('bin')
child.expect('ftp> ')
child.sendline('put pexpect-current.tgz')
child.expect('ftp> ')
child.sendline('put pexpect-doc.tgz')
child.expect('ftp> ')
child.sendline('put pexpect-examples.tgz')
child.expect('ftp> ')
child.sendline('ls pexpect*')
child.expect('ftp> ')
print child.before
child.sendline('bye')

