#!/usr/bin/env python
'''Change passwords on the named machines.
    passmass host1 host2 host3 . . .
Note that login shell prompt on remote machine must end in # or $.
'''

import pexpect
import sys, getpass

USAGE = '''passmass host1 host2 host3 . . .'''
SHELL_PROMPT = '[#\$] '

def login(host, user, password):
    child = pexpect.spawn('ssh %s@%s'%(user, host))
    child.log_open('LOG')
    child.expect('password:')
    child.sendline(password)
    i = child.expect(['Permission denied', SHELL_PROMPT, 'Terminal type'])
    if i == 0:
        print 'Permission denied on host:', host
        return None
    elif i == 2:
        child.sendline('vt100')
        i = child.expect('[#\$] ')
    return child

def change_password(child, user, oldpassword, newpassword):
    child.sendline('passwd %s'%user)
    i = child.expect(['Old password', 'New password'])
    # Root does not require old password, so it gets to bypass the next step.
    if i == 0:
        child.sendline(oldpassword)
        child.expect('New password')
    child.sendline(newpassword)
    i = child.expect(['New password', 'Retype new password'])
    if i == 0:
        print 'Host did not like new password. Here is what it said...'
        print child.before
        child.sendline('') # This should tell remote passwd command to quit.
        return
    child.sendline(newpassword)

def main():
    if len(sys.argv) <= 1:
        print USAGE
        return 1

    user = raw_input('Username: ')
    password = getpass.getpass('Current Password: ')
    newpassword = getpass.getpass('New Password: ')
    newpasswordconfirm = getpass.getpass('Confirm New Password: ')
    if newpassword != newpasswordconfirm:
        print 'New Passwords do not match.'
        return 1

    for host in sys.argv[1:]:
        child = login(host, user, password)
        if child == None:
            print 'Could not login to host:', host
            continue
        print 'Changing password on host:', host
        change_password(child, user, password, newpassword)
        child.expect(SHELL_PROMPT)
        child.sendline('exit')

if __name__ == '__main__':
    try:
        main()
    except pexpect.ExceptionPexpect, e:
        print str(e)


