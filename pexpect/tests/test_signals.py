#!/usr/bin/env python
import signal, os, time, errno

def signal_handler (signum, frame):
    print 'Signal handler called with signal:', signum
    print 'signal.SIGCHLD=', signal.SIGKILL


# First thing we do is set up a handler for SIGCHLD.
signal.signal (signal.SIGCHLD, signal_handler)
#signal.signal (signal.SIGCHLD, signal.SIG_IGN)


# Create a child process for us to kill.
pid = os.fork()
if pid == 0:
    time.sleep(10000)


print 'Sending SIGKILL to child pid:', pid
os.kill (pid, signal.SIGKILL)


# SIGCHLD should interrupt sleep.
# Note that this is a race.
# It is possible that the signal handler will get called
# before we try to sleep, but this has not happened yet.
# But in that case we can only tell by order of printed output.
try:
    time.sleep(10)
except:
    print 'sleep was interrupted by signal.'


print '''The signal handler should have been called either before
or durring the sleep. If the signal handler is called after or not at all
then something went wrong.'''


# Just for fun let's see if the process is alive.
try:
    os.kill(pid, 0)
    print 'Child is alive. This is ambiguous because it may be a Zombie.'
except OSError, e:
    print 'Child appears to be dead.'
