#!/usr/bin/env python
"""hivesh -- Hive Shell

This lets you ssh to a group of servers and control them as if they were one.

Usage:
    hivesh.py server1 server2 server3
Features:
    *
    *
    *

$Id $
Noah Spurrier
"""
import sys, os, re, math, stat, getopt, traceback, types, time, getpass
import pexpect, pxssh

def exit_with_usage(exit_code=1):
    print globals()['__doc__']
    os._exit(exit_code)

def main ():
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?', ['help','h','?','username','password'])
    except Exception, e:
        print str(e)
        exit_with_usage()
    options = dict(optlist)
    # There are a million ways to cry for help. These are but a few of them.
    if [elem for elem in options if elem in ['-h','--h','-?','--?','--help']]:
        exit_with_usage(0)

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

:target name1 name2 name3 ... - set list of hosts to target commands

:target all - reset list of hosts to target all hosts in the hive. 

:sync - set mode to wait for shell prompts after commands are run. This is the
default. When Hive first logs into a host it sets a special shell prompt
pattern that it can later look for to synchronize output of the hosts. If you
'su' to another user then it can upset the synchronization. If you need to run
something like 'su' then use the following pattern:

    CMD (? for help) > :async
    CMD (? for help) > sudo su - root
    CMD (? for help) > :prompt
    CMD (? for help) > :sync

:async - set mode to not expect command line prompts (see :sync). Afterwards
commands are send to target hosts, but their responses are not read back until
:sync is run. This is useful to run before commands that will not return with
the special shell prompt pattern that Hive uses to synchronize.

:prompt - force each host to reset command line prompt to the special pattern
used to synchronize all the hosts. This is useful if you 'su' to a different
user.

:sendline my_text - This will send the 'my_text' followed by a CR to the
targetted hosts. This output of the hosts is not automatically synchronized.
This is useful if you want send a response to username and password prompts.
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
        elif cmd[:9] == ':sendline':
            cmd, line = cmd.split(None,1)
            for name in target_names:
                hive[name].sendline(line)
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

