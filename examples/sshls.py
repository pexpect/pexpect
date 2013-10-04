#!/usr/bin/env python

'''This runs 'ls -l' on a remote host using SSH.
At the prompts enter hostname, username, and password.

PEXPECT LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012, Noah Spurrier <noah@noah.org>
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''

from __future__ import print_function

from __future__ import absolute_import

import pexpect
import getpass, os


try:
    raw_input
except NameError:
    raw_input = input


def ssh_command (user, host, password, command):

    '''This runs a command on the remote host. This could also be done with the
    pxssh class, but this demonstrates what that class does at a simpler level.
    This returns a pexpect.spawn object. This handles the case when you try to
    connect to a new host and ssh asks you if you want to accept the public key
    fingerprint and continue connecting. '''

    ssh_newkey = 'Are you sure you want to continue connecting'
    child = pexpect.spawn('ssh -l %s %s %s'%(user, host, command))
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
    if i == 0: # Timeout
        print('ERROR!')
        print('SSH could not login. Here is what SSH said:')
        print(child.before, child.after)
        return None
    if i == 1: # SSH does not have the public key. Just accept it.
        child.sendline ('yes')
        child.expect ('password: ')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0: # Timeout
            print('ERROR!')
            print('SSH could not login. Here is what SSH said:')
            print(child.before, child.after)
            return None
    child.sendline(password)
    return child

def main ():

    host = raw_input('Hostname: ')
    user = raw_input('User: ')
    password = getpass.getpass('Password: ')
    child = ssh_command (user, host, password, '/bin/ls -l')
    child.expect(pexpect.EOF)
    print(child.before)

if __name__ == '__main__':

    try:
        main()
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        os._exit(1)

