#!/usr/bin/env python
'''This runs "uname" on a remote host using SSH.
    At the prompts enter hostname, user, and password.
'''
import pexpect
import getpass

SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)?'

host = raw_input('Hostname: ')
user = raw_input('User: ')
password = getpass.getpass('Password: ')

child = pexpect.spawn("ssh -l %s %s"%(user, host))
i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, 'password: '])
if i == 1:
	child.sendline ('yes')
	child.expect ('password: ')
child.sendline(password)
i = child.expect (['[#$] ', 'Terminal type?'])
if i == 1:
	child.sendline ('vt100')
	child.expect ('[#$] ')

child.sendline ('uptime')

child.expect ('up ([0-9]+) days?,.*?,\s+([0-9]+) users?,\s+load averages?: ([0-9]+\.[0-9][0-9]), ([0-9]+\.[0-9][0-9]), ([0-9]+\.[0-9][0-9])')
duration, users, av1, av5, av15 = child.match.groups()
print '%s days, %s users, %s (1 min), %s (5 min), %s (15 min)' % (
    duration, users, av1, av5, av15)

child.expect ('[#$] ')
child.sendline ('iostat')
child.expect ('[#$] ')
print child.before
child.sendline ('exit')
child.expect(pexpect.EOF)

print child.before

