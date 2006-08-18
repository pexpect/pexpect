#!/usr/bin/env python
"""hivesh -- Hive Shell

This lets you ssh to a group of servers and control them as if they were one.
Each command you enter is sent to each host in parallel. The response of each
host is collected and printed. In normal synchronous mode Hive will wait for
each host to return the shell command line prompt. The shell prompt is used
to synch output.

Example:
    $ ./hivesh.py host1.example.com host2.example.net
    username: noah
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

    --askall : This tells Hive that you want to be prompted for your
                username and password separately for all machines.
                This is useful if you have differnet usernames and
                passwords on each host. This can even be used to connect
                to different user accounts on a single host. For example:
                    hive.py --askall host1 host1 host1

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

def main ():
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?', ['help','h','?','askall','username','password'])
    except Exception, e:
        print str(e)
        exit_with_usage()
    options = dict(optlist)
    # There are a million ways to cry for help. These are but a few of them.
    if [elem for elem in options if elem in ['-h','--h','-?','--?','--help']]:
        exit_with_usage(0)

    if '--askall' in options:
        ask_all_mode = True
    else:
        ask_all_mode = False
    if not ask_all_mode:
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
    for name in args:
        print 'connecting to', name,
        if ask_all_mode:
            username = raw_input('username: ')
            password = getpass.getpass('password: ')
        try:
            hive[name] = pxssh.pxssh()
            hive[name].login(name, username, password)
            hive_names.append(name)
            print '- OK'
        except Exception, e:
            print '- ERROR',
            print str(e)
            print 'Skipping', name
            if name in hive:
                del hive[name]

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

:prompt
    force each host to reset command line prompt to the special pattern
    used to synchronize all the hosts. This is useful if you 'su' to
    a different user where Hive would not know the prompt to match.

:send my text
    This will send the 'my text' wihtout a line feed to the targetted hosts.
    This output of the hosts is not automatically synchronized.
"""

    synchronous_mode = True
    target_names = hive_names[:]
    print 'targetting hosts:', ' '.join(target_names)
    while True:
        cmd = raw_input('CMD (? for help) > ')
        cmd = cmd.strip()
        if cmd=='?':
            print CMD_HELP
            continue
        elif cmd==':sync':
            synchronous_mode = True
            resync (hive, target_names)
            continue
        elif cmd==':async':
            synchronous_mode = False
            continue
        elif cmd==':prompt':
            for name in target_names:
                hive[name].set_unique_prompt()
            continue
        elif cmd[:5] == ':send':
            cmd, txt = cmd.split(None,1)
            for name in target_names:
                hive[name].send(txt)
            continue
        elif cmd[:7] == ':expect':
            cmd, pattern = cmd.split(None,1)
            print 'looking for', pattern
            for name in target_names:
                hive[name].expect(pattern)
                print hive[name].before
            continue
        elif cmd[:7] == ':target':
            # TODO need to check target_list against hive_names
            target_names = cmd.split()[1:]
            if len(target_names) == 0 or target_names[0] == 'all':
                target_names = hive_names[:]
            print 'targetting hosts:', ' '.join(target_names)
            continue

        # Run the command on all targets in parallel
        for name in target_names:
            hive[name].sendline (cmd)
            # This is a simple hack to detect if switching users, so we can set the prompt.
            #if cmd[:3] == 'su ' or ' su ' in cmd:
            #    print "hacking prompt"
            #    time.sleep(0.5)
            #    hive[name].set_unique_prompt()

        if cmd == 'exit':
            break

        # if syncronous then wait for the prompts.
        if synchronous_mode:
            for name in target_names:
                hive[name].prompt()
                print '=============================================================================='
                print name
                print '------------------------------------------------------------------------------'
                print hive[name].before
            print '=============================================================================='
    
def resync (hive, hive_names, timeout=2, max_attempts=5):
    """This expects the prompt for each server in an effort to
    try to get them all to the same state. The timeout is set low
    so that servers that are already at the prompt will not slow
    things down too much. If a server does match a prompt then
    keep asking until it stops. This is a best effort to consume
    all input. It's kind of kludgy.
    """
    for name in hive_names:
        for attempts in xrange(0, max_attempts):
            if not hive[name].prompt(timeout=timeout):
                break

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

