#!/usr/bin/env python
'''This runs some commands on a remote host using SSH.
    At the prompts enter hostname, user, and password.

   It works like this:
        Login via SSH (This is the hardest part).
        Run and parse 'uptime'.
        Run 'iostat'.
        Run 'vmstat'.
	Run 'netstat'
        Run 'free'.
        Exit the remote host.

'''
import pexpect
import getpass

#
# Some constants. These are regular expressions.
#
TERMINAL_PROMPT = 'Terminal type?'
TERMINAL_TYPE = 'vt100'
COMMAND_PROMPT = '[$#] ' ### This is way too simple for industrial use :-) ...
              # This is the prompt we get if SSH does not have 
              # the remote host's public key stored in the cache.
SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)?'
PASSWORD_PROMPT_MYSQL = 'Enter password: '

print 'Enter the host that you wish to monitor.'
host = raw_input('Hostname: ')
user = raw_input('User: ')
password = getpass.getpass('Password: ')
password_mysql = getpass.getpass('MySQL Password [None]: ')

#
# Login via SSH
#
child = pexpect.spawn('ssh -l %s %s'%(user, host))
i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, 'password: '])
if i == 0: # Timeout
        print 'ERROR!'
        print 'SSH could not login. Here is what SSH said:'
        print child.before, child.after
        sys.exit (1)
if i == 1: # SSH does not have the public key. Just accept it.
        child.sendline ('yes')
        child.expect ('password: ')
child.sendline(password)
        # Now we are either at the command prompt or
        # the login process is asking for our terminal type.
i = child.expect ([COMMAND_PROMPT, TERMINAL_PROMPT])
if i == 1:
        child.sendline (TERMINAL_TYPE)
        child.expect (COMMAND_PROMPT)

#
# Now we should be at the command prompt and ready to run some commands.
#
print
print '---------------------------------------'
print 'Report of commands run on remote host.'

# Run and parse 'uptime'.
child.sendline ('uptime')
child.expect ('up ([0-9]+) days?,.*?,\s+([0-9]+) users?,\s+load averages?: ([0-9]+\.[0-9][0-9]), ([0-9]+\.[0-9][0-9]), ([0-9]+\.[0-9][0-9])')
duration, users, av1, av5, av15 = child.match.groups()
print
print 'Uptime: %s days, %s users, %s (1 min), %s (5 min), %s (15 min)' % (
    duration, users, av1, av5, av15)
child.expect (COMMAND_PROMPT)

# Run iostat.
child.sendline ('iostat')
child.expect (COMMAND_PROMPT)
print
print child.before

# Run vmstat.
child.sendline ('vmstat')
child.expect (COMMAND_PROMPT)
print
print child.before

# Run netstat
child.sendline ('netstat')
child.expect (COMMAND_PROMPT)
print
print child.before

# Run free.
child.sendline ('free') # Linux systems only.
child.expect (COMMAND_PROMPT)
print
print child.before

# Run df.
child.sendline ('df')
child.expect (COMMAND_PROMPT)
print
print child.before

# Run MySQL show status.
child.sendline ('mysql -p -e "SHOW STATUS;"')
child.expect (PASSWORD_PROMPT_MYSQL)
child.sendline (password_mysql)
child.expect (COMMAND_PROMPT)
print
print child.before

# Now exit the remote host.
child.sendline ('exit')
child.expect(pexpect.EOF)


