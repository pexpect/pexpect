#!/usr/bin/env python
"""hivesh -- Hive Shell

This lets you ssh to a group of servers and control them as if they were one.
Each command you enter is sent to each host in parallel. The response of each
host is collected and printed. In normal synchronous mode Hive will wait for
each host to return the shell command line prompt. The shell prompt is used
to synch output.

Example:
    $ ./hivesh.py --samepw host1.example.com host2.example.net
    username: myusername
    password: 
    connecting to host1.example.com - OK
    connecting to host2.example.net- OK
    targetting hosts: 63.199.26.226 63.199.26.229
    CMD (? for help) > uptime
    =======================================================================
    host1.example.com
    -----------------------------------------------------------------------
    uptime
    23:49:55 up 74 days,  5:14,  2 users,  load average: 0.15, 0.05, 0.01
    =======================================================================
    host2.example.net
    -----------------------------------------------------------------------
    uptime
    23:53:02 up 1 day, 13:36,  2 users,  load average: 0.50, 0.40, 0.46
    =======================================================================

Usage:
    hivesh.py host1 host2 host3 ... hostN
You will be asked for your username and password.
It is assumed that these will be the same for all hosts
or that you have key pairs registered for each host.

    --samepw : This flag tells Hive that you want to be prompted just once
                for your username and password and to use these credentials
                for each host.

$Id $
Noah Spurrier
"""
# TODO add feature to support username:password@host combination
# TODO add feature to log each host output in separate file

import sys, os, re, getopt, traceback, types, time, getpass
import pexpect, pxssh

def exit_with_usage(exit_code=1):
    print globals()['__doc__']
    os._exit(exit_code)

CMD_HELP="""Hive commands are preceded by a colon : (just think of vi).

:target name1 name2 name3 ...
    set list of hosts to target commands

:target all
    reset list of hosts to target all hosts in the hive. 

:sync
    set mode to wait for shell prompts after commands are run. This is the
    default. When Hive first logs into a host it sets a special shell prompt
    pattern that it can later look for to synchronize output of the hosts. If
    you 'su' to another user then it can upset the synchronization. If you need
    to run something like 'su' then use the following pattern:

    CMD (? for help) > :async
    CMD (? for help) > sudo su - root
    CMD (? for help) > :prompt
    CMD (? for help) > :sync

:async
    set mode to not expect command line prompts (see :sync). Afterwards
    commands are send to target hosts, but their responses are not read back
    until :sync is run. This is useful to run before commands that will not
    return with the special shell prompt pattern that Hive uses to synchronize.

:resync
    This is similar to :sync, but it does not change the mode.
    It looks for the prompt and thus consumes all input from all targetted
    hosts.

:prompt
    force each host to reset command line prompt to the special pattern
    used to synchronize all the hosts. This is useful if you 'su' to
    a different user where Hive would not know the prompt to match.

:send my text
    This will send the 'my text' wihtout a line feed to the targetted hosts.
    This output of the hosts is not automatically synchronized.

:exit
    This will exit the hive shell.
"""

def main ():
    global CMD_HELP

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?', ['help','h','?','samepw','username=','password='])
    except Exception, e:
        print str(e)
        exit_with_usage()
    options = dict(optlist)
    # There are a million ways to cry for help. These are but a few of them.
    if [elem for elem in options if elem in ['-h','--h','-?','--?','--help']]:
        exit_with_usage(0)

    if '--samepw' in options:
        samepw = True
    else:
        samepw = False
    if samepw:
        if '--username' in options:
            username = options['--username']
        else:
            username = raw_input('username: ')
        if '--password' in options:
            password = options['--password']
        else:
            password = getpass.getpass('password: ')

    hive = {}
    hive_names = []
    for host_connect_string in args:
        hcd = parse_host_connect_string (host_connect_string)
        hostname = hcd['hostname']
        username = hcd['username']
        password = hcd['password']
        port     = hcd['port']
        print 'connecting to', hostname
        if not samepw:
            if username == '':
                username = raw_input('username: ')
            if password == '':
                password = getpass.getpass('password: ')
        if port == '':
            port = None
        try:
            hive[hostname] = pxssh.pxssh()
            hive[hostname].login(hostname, username, password, port)
            hive_names.append(hostname)
            print '- OK'
        except Exception, e:
            print '- ERROR',
            print str(e)
            print 'Skipping', hostname
            if hostname in hive:
                del hive[hostname]

    synchronous_mode = True
    target_hostnames = hive_names[:]
    print 'targetting hosts:', ' '.join(target_hostnames)
    while True:
        cmd = raw_input('CMD (? for help) > ')
        cmd = cmd.strip()
        if cmd=='?':
            print CMD_HELP
            continue
        elif cmd==':resync':
            resync (hive, target_hostnames, timeout=0.5)
            for hostname in target_hostnames:
                print '/============================================================================='
                print '| ' + hostname
                print '\\-----------------------------------------------------------------------------'
                print hive[hostname].before
            print '=============================================================================='
            continue
        elif cmd==':sync':
            synchronous_mode = True
            resync (hive, target_hostnames, timeout=0.5)
            continue
        elif cmd==':async':
            synchronous_mode = False
            continue
        elif cmd==':prompt':
            for hostname in target_hostnames:
                hive[hostname].set_unique_prompt()
            continue
        elif cmd[:5] == ':send':
            cmd, txt = cmd.split(None,1)
            for hostname in target_hostnames:
                hive[hostname].send(txt)
            continue
        elif cmd[:7] == ':expect':
            cmd, pattern = cmd.split(None,1)
            print 'looking for', pattern
            for hostname in target_hostnames:
                hive[hostname].expect(pattern)
                print hive[hostname].before
            continue
        elif cmd[:7] == ':target':
            # TODO need to check target_list against hive_names
            target_hostnames = cmd.split()[1:]
            if len(target_hostnames) == 0 or target_hostnames[0] == 'all':
                target_hostnames = hive_names[:]
            print 'targetting hosts:', ' '.join(target_hostnames)
            continue
        elif cmd == ':exit':
            break
        #
        # Run the command on all targets in parallel
        #
        for hostname in target_hostnames:
            hive[hostname].sendline (cmd)

        #
        # print the response for each targeted host.
        #
        if synchronous_mode:
            for hostname in target_hostnames:
                hive[hostname].prompt(timeout=2)
                print '/============================================================================='
                print '| ' + hostname
                print '\\-----------------------------------------------------------------------------'
                print hive[hostname].before
            print '=============================================================================='
    
def resync (hive, hive_names, timeout=2, max_attempts=5):
    """This waits for the shell prompt for each host in an effort to try to get
    them all to the same state. The timeout is set low so that hosts that are
    already at the prompt will not slow things down too much. If a prompt match
    is made for a hosts then keep asking until it stops matching. This is a
    best effort to consume all input if it printed more than one prompt. It's
    kind of kludgy. Note that this will always introduce a delay equal to the
    timeout for each machine. So for 10 machines with a 2 second delay you will
    get AT LEAST a 20 second delay if not more.
    """
    # TODO This is ideal for threading.
    for hostname in hive_names:
        for attempts in xrange(0, max_attempts):
            if not hive[hostname].prompt(timeout=timeout):
                break

def parse_host_connect_string (hcs):
    """This parses a host connection string in the form username:password@hostname:port.
    All fields are options expcet hostname. A dictionary is returned with all four keys.
    Keys that were not included are set to empty strings ''. Note that if your password has
    the '@' character then you must backslash escape it.
    """
    if '@' in hcs:
        p = re.compile (r'(?P<username>[^@:]*)(:?)(?P<password>.*)(?!\\)@(?P<hostname>[^:]*):?(?P<port>[0-9]*)')
    else:
        p = re.compile (r'(?P<username>)(?P<password>)(?P<hostname>[^:]*):?(?P<port>[0-9]*)')
    m = p.search (hcs)
    d = m.groupdict()
    d['password'] = d['password'].replace('\\@','@')
    return d

if __name__ == "__main__":
    try:
        start_time = time.time()
        print time.asctime()
        main()
        print time.asctime()
        print "TOTAL TIME IN MINUTES:",
        print (time.time() - start_time) / 60.0
    except Exception, e:
        tb_dump = traceback.format_exc()
        print "=========================================================================="
        print "ERROR -- Unexpected exception in script."
        print str(e)
        print str(tb_dump)
        print "=========================================================================="
        exit_with_usage(3)

