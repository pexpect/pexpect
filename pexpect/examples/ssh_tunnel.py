#!/usr/bin/env python
"""This starts an SSH tunnel to a given host.
If the SSH process ever dies then this script will detect that and restart it.
I use this under Cygwin to keep open encrypted tunnels to
port 110 (POP3) and port 25 (SMTP). I set my mail client to talk to
localhost and I keep this script running in the background.

Note that this is a rather stupid script at the moment because it
just looks to see if any ssh process is running. It should really
make sure that our specific ssh process is running.

ssh is missing a very useful feature. It has no way to report the
process id of the background daemon that it creates with the -f command.
Most annoying!

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

def get_process_info ():
    # This seems to work on both Linux and BSD, but should otherwise be considered highly UNportable.
    # Basic process info is one of those glaring features missing from POSIX.
    ps = pexpect.run ('ps ax -O ppid')
    pass
def start_tunnel ():
    try:
        ssh_tunnel = pexpect.spawn (tunnel_command % globals())
        ssh_tunnel.expect ('password:')
        time.sleep (0.1)
        ssh_tunnel.sendline (X)
        time.sleep (60) # Cygwin is slow to update process status.
        ssh_tunnel.expect (pexpect.EOF)

    except Exception, e:
        print str(e)

def main ():
    while 1:
        ps = pexpect.spawn ('ps')
        time.sleep (1)
        index = ps.expect (['/usr/bin/ssh', pexpect.EOF, pexpect.TIMEOUT])
        if index == 2:
            print 'TIMEOUT in ps command...'
            print str(ps)
            time.sleep (13)
        if index == 1:
            print time.asctime(),
            print 'restarting tunnel'
            start_tunnel ()
            time.sleep (11)
	        print 'tunnel OK'
        else:
            # print 'tunnel OK'
            time.sleep (7)

if __name__ == '__main__':
    main ()

