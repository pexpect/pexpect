#!/usr/bin/env python
"""This starts an SSH tunnel to a given host.
If the SSH process ever dies then this script will detect that and restart it.
I use this under Cygwin to keep open encrypted tunnels to
port 110 (POP3) and port 25 (SMTP). I set my mail client to talk to
localhost and I keep this script running in the background.
"""
import pexpect
import getpass
import time

#tunnel_command = 'ssh -C -N  -L 25:%(host)s:25 -L 110:%(host)s:110 %(user)s@%(host)s'
tunnel_command = 'ssh -C -n -L 25:%(host)s:25 -L 110:%(host)s:110 %(user)s@%(host)s -f nothing.sh'
nothing_script = """#!/bin/sh
while true; do sleep 53; done
"""
host = raw_input('Hostname: ')
user = raw_input('Username: ')
X = getpass.getpass('Password: ')

def start_tunnel ():
    ssh_tunnel = pexpect.spawn (tunnel_command % globals())
    try:
        ssh_tunnel.expect ('password:')
    except Exception, e:
        print str(e)
        print ssh_tunnel.before
        print ssh_tunnel.after
    time.sleep (0.1)
    ssh_tunnel.sendline (X)
    time.sleep (60) # Cygwin is slow to update process status.
    ssh_tunnel.expect (pexpect.EOF)

def main ():
    while 1:
        ps = pexpect.spawn ('ps')
        time.sleep (1)
        index = ps.expect (['/usr/bin/ssh', pexpect.EOF, pexpect.TIMEOUT])
        if index == 2:
            print 'TIMEOUT in ps command...'
            print ps.before
            print ps.after
        if index == 1:
            print time.asctime(),
            print 'restarting tunnel'
            start_tunnel ()
            time.sleep (60)
	    print 'tunnel OK'
        else:
            # print 'tunnel OK'
            time.sleep (60)

if __name__ == '__main__':
    main ()


