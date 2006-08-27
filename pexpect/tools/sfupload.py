#!/usr/bin/env python
'''This uploads the latest pexpect package to sourceforge.
'''
import pexpect
import sys

child = pexpect.spawn('ftp upload.sourceforge.net')
child.logfile = sys.stdout
child.expect('Name .*: ')
child.sendline('anonymous')
child.expect('Password:')
child.sendline('noah@noah.org')
child.expect('ftp> ')
child.sendline('cd /incoming')
child.expect('ftp> ')
child.sendline('lcd dist')
child.expect('ftp> ')
child.sendline('bin')
child.expect('ftp> ')
child.sendline('prompt')
child.expect('ftp> ')
child.sendline('mput pexpect-*.tar.gz')
child.expect('ftp> ')
child.sendline('ls pexpect*')
child.expect('ftp> ')
print child.before
child.sendline('bye')

