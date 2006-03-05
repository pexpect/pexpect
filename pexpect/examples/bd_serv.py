#!/usr/bin/env python

# Clearly having the password on the command line is not a good idea, but
# then this entire project is probably not the most security concious thing
# I've ever built. This should be considered an experimental tool.
"""Back door shell server

This exposes a shell terminal emulator on a socket.

    --hostname : sets the remote host name to open an ssh connection to.
    --username : sets the user name to login with
    --password : (optional) sets the password to login with
    --port     : set the local port for the server to listen on
"""
import pxssh, pexpect, ANSI
import socket
import time, sys, os, getopt, getpass

def exit_with_usage(exit_code=1):
    print globals()['__doc__']
    os._exit(exit_code)

def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    '''This forks the current process into a daemon.
    Almost none of this is necessary (or advisable) if your daemon 
    is being started by inetd. In that case, stdin, stdout and stderr are 
    all set up for you to refer to the network connection, and the fork()s 
    and session manipulation should not be done (to avoid confusing inetd). 
    Only the chdir() and umask() steps remain as useful. 

    References:
        UNIX Programming FAQ
        1.7 How do I get my program to act like a daemon?
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16

        Advanced Programming in the Unix Environment
        W. Richard Stevens, 1992, Addison-Wesley, ISBN 0-201-56317-7.

    The stdin, stdout, and stderr arguments are file names that
    will be opened and be used to replace the standard file descriptors
    in sys.stdin, sys.stdout, and sys.stderr.
    These arguments are optional and default to /dev/null.
    Note that stderr is opened unbuffered, so
    if it shares a file with stdout then interleaved output
    may not appear in the order that you expect.
    '''

    # Do first fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit first parent.
    except OSError, e: 
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/") 
    os.umask(0) 
    os.setsid() 

    # Do second fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit second parent.
    except OSError, e: 
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Now I am a daemon!
    
    # Redirect standard file descriptors.
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # I now return as the daemon
    return 0

def add_cursor_blink (response, row, col):
    i = (row-1) * 80 + col
    return response[:i]+'<img src="http://www.noah.org/cursor.gif">'+response[i:]

def main ():
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?', ['help','h','?', 'hostname', 'username', 'password', 'port'])
    except Exception, e:
        print str(e)
        exit_with_usage()

    command_line_options = dict(optlist)
    options = dict(optlist)
    # There are a million ways to cry for help. These are but a few of them.
    if [elem for elem in command_line_options if elem in ['-h','--h','-?','--?','--help']]:
        exit_with_usage(0)

    if '--hostname' in options:
        hostname = options['--hostname']
    else:
        hostname = raw_input('hostname: ')
    if '--username' in options:
        username = options['--username']
    else:
        username = raw_input('username: ')
    if '--password' in options:
        password = options['--password']
    else:
        password = getpass.getpass('password: ')
    if '--port' in options:
        port = int(options['--port'])
    else:
        port = int(raw_input('port: '))
    
    #daemonize ()
    #daemonize('/dev/null','/tmp/daemon.log','/tmp/daemon.log')
    sys.stdout.write ('server started with pid %d\n' % os.getpid() )

    virtual_screen = ANSI.ANSI (24,80) 
    child = pxssh.pxssh()
    child.login (hostname, username, password)
    print 'created shell. command line prompts is', child.PROMPT
    #child.sendline ('stty -echo')
    #time.sleep (0.2)
    #child.sendline ('export PS1="HAON "')
    #time.sleep (0.2)
    #child.expect (pexpect.TIMEOUT)
    print child.before
    virtual_screen.process_list (child.before)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    localhost = '127.0.0.1' # symbolic name meaning the local host
    s.bind((localhost, port))
    print 'Listen'
    s.listen(1)
    print 'Accept'
    try:
        while True:
            conn, addr = s.accept()
            print 'Connected by', addr
            data = conn.recv(1024)
            request = data.split('\x01')#('\n')
            cmd = request[0]
            arg = request[1]

            if cmd == 'COMMAND':
                child.sendline (arg)
                child.prompt()
                virtual_screen.process_list (child.before.replace('\r',''))
                if arg == 'exit':
                    s.close()
                    break
            elif cmd == 'REFRESH':
                pass
            elif data == 'SKIP':
            # Wait until the TIMEOUT then throw away all data from the child.
                child.expect (pexpect.TIMEOUT)
                sh_response = child.before.replace ('\r', '')
                virtual_screen.process_list (sh_response)
            response = []
            response.append ('%03d' % virtual_screen.cols)
            response.append ('%03d' % virtual_screen.rows)
            response.append (virtual_screen.dump())
            print 'cols:', virtual_screen.cols
            print 'rows:', virtual_screen.rows
            print 'screen size:', len(response[2])
            #response = add_cursor_blink (response, row, col)
            sent = conn.send('\n'.join(response))
            if sent < len (response):
                print "Sent is too short. Some data was cut off."
            conn.close()
    finally:
        print "cleaning up socket"
        s.close()
 
if __name__ == "__main__":
#    daemonize('/dev/null','/tmp/daemon.log','/tmp/daemon.log')
    main()

