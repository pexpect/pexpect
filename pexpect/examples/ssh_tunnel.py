import pexpect
import getpass
import time

tunnel_command = 'ssh -C -n -L 25:%(host)s:25 -L 110:%(host)s:110 %(user)s@%(host)s -f nothing.sh'
nothing_script = """#!/bin/sh
while true; do sleep 53; done
"""
host = 'spruce.he.net' #'example.com'
user = raw_input('Username: ')
X = getpass.getpass('Password: ')

def start_tunnel ():
    ssh_tunnel = pexpect.spawn (tunnel_command % globals())
    ssh_tunnel.expect ('password:')
    time.sleep (0.1)
    ssh_tunnel.sendline (X)
    time.sleep (60)
    ssh_tunnel.expect (pexpect.EOF)

while 1:
    ps = pexpect.spawn ('ps')
    time.sleep (1)
    index = ps.expect (['/usr/bin/ssh', pexpect.EOF, pexpect.TIMEOUT])
    if index == 2:
	print 'TIMEOUT in ps command...'
        print ps.before
	print ps.after
	print '^^^^^'
    if index == 1:
        print 'restarting tunnel'
        start_tunnel ()
        time.sleep (1)
    else:
        print 'tunnel OK'
        time.sleep (1)

