#!/usr/bin/env python
'''This runs "ls -l" on a remote host using SSH.
    At the prompts enter hostname, user, and password.
'''
import pexpect
import getpass

host = raw_input('Hostname: ')
user = raw_input('User: ')
password = getpass.getpass('Password: ')

child = pexpect.spawn("/usr/bin/ssh -l %s %s /bin/ls -l"%(user, host))

child.expect('password:')
child.sendline(password)

child.expect_eof()

print child.before

