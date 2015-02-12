'''Pexpect is a Python module for spawning child applications and controlling
them automatically. Pexpect can be used for automating interactive applications
such as ssh, ftp, passwd, telnet, etc. It can be used to a automate setup
scripts for duplicating software package installations on different servers. It
can be used for automated software testing. Pexpect is in the spirit of Don
Libes' Expect, but Pexpect is pure Python. Other Expect-like modules for Python
require TCL and Expect or require C extensions to be compiled. Pexpect does not
use C, Expect, or TCL extensions. It should work on any platform that supports
the standard Python pty module. The Pexpect interface focuses on ease of use so
that simple tasks are easy.

There are two main interfaces to the Pexpect system; these are the function,
run() and the class, spawn. The spawn class is more powerful. The run()
function is simpler than spawn, and is good for quickly calling program. When
you call the run() function it executes a given program and then returns the
output. This is a handy replacement for os.system().

For example::

    pexpect.run('ls -la')

The spawn class is the more powerful interface to the Pexpect system. You can
use this to spawn a child program then interact with it by sending input and
expecting responses (waiting for patterns in the child's output).

For example::

    child = pexpect.spawn('scp foo user@example.com:.')
    child.expect('Password:')
    child.sendline(mypassword)

This works even for commands that ask for passwords or other input outside of
the normal stdio streams. For example, ssh reads input directly from the TTY
device which bypasses stdin.

Credits: Noah Spurrier, Richard Holden, Marco Molteni, Kimberley Burchett,
Robert Stone, Hartmut Goebel, Chad Schroeder, Erick Tryzelaar, Dave Kirby, Ids
vander Molen, George Todd, Noel Taylor, Nicolas D. Cesar, Alexander Gattin,
Jacques-Etienne Baudoux, Geoffrey Marshall, Francisco Lourenco, Glen Mabey,
Karthik Gurusamy, Fernando Perez, Corey Minyard, Jon Cohen, Guillaume
Chazarain, Andrew Ryan, Nick Craig-Wood, Andrew Stone, Jorgen Grahn, John
Spiegel, Jan Grant, and Shane Kerr. Let me know if I forgot anyone.

Pexpect is free, open source, and all that good stuff.
http://pexpect.sourceforge.net/

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

import sys
import types

from .exceptions import ExceptionPexpect, EOF, TIMEOUT
from .utils import split_command_line, which, is_executable_file
from .pty_spawn import spawn, spawnu, PY3
from .expect import Expecter, searcher_re, searcher_string

__version__ = '3.3'
__revision__ = ''
__all__ = ['ExceptionPexpect', 'EOF', 'TIMEOUT', 'spawn', 'spawnu', 'run', 'runu',
           'which', 'split_command_line', '__version__', '__revision__']

def run(command, timeout=30, withexitstatus=False, events=None,
        extra_args=None, logfile=None, cwd=None, env=None):

    '''
    This function runs the given command; waits for it to finish; then
    returns all output as a string. STDERR is included in output. If the full
    path to the command is not given then the path is searched.

    Note that lines are terminated by CR/LF (\\r\\n) combination even on
    UNIX-like systems because this is the standard for pseudottys. If you set
    'withexitstatus' to true, then run will return a tuple of (command_output,
    exitstatus). If 'withexitstatus' is false then this returns just
    command_output.

    The run() function can often be used instead of creating a spawn instance.
    For example, the following code uses spawn::

        from pexpect import *
        child = spawn('scp foo user@example.com:.')
        child.expect('(?i)password')
        child.sendline(mypassword)

    The previous code can be replace with the following::

        from pexpect import *
        run('scp foo user@example.com:.', events={'(?i)password': mypassword})

    **Examples**

    Start the apache daemon on the local machine::

        from pexpect import *
        run("/usr/local/apache/bin/apachectl start")

    Check in a file using SVN::

        from pexpect import *
        run("svn ci -m 'automatic commit' my_file.py")

    Run a command and capture exit status::

        from pexpect import *
        (command_output, exitstatus) = run('ls -l /bin', withexitstatus=1)

    The following will run SSH and execute 'ls -l' on the remote machine. The
    password 'secret' will be sent if the '(?i)password' pattern is ever seen::

        run("ssh username@machine.example.com 'ls -l'",
            events={'(?i)password':'secret\\n'})

    This will start mencoder to rip a video from DVD. This will also display
    progress ticks every 5 seconds as it runs. For example::

        from pexpect import *
        def print_ticks(d):
            print d['event_count'],
        run("mencoder dvd://1 -o video.avi -oac copy -ovc copy",
            events={TIMEOUT:print_ticks}, timeout=5)

    The 'events' argument should be either a dictionary or a tuple list that
    contains patterns and responses. Whenever one of the patterns is seen
    in the command output, run() will send the associated response string.
    So, run() in the above example can be also written as:
    
        run("mencoder dvd://1 -o video.avi -oac copy -ovc copy",
            events=[(TIMEOUT,print_ticks)], timeout=5)

    Use a tuple list for events if the command output requires a delicate
    control over what pattern should be matched, since the tuple list is passed
    to pexpect() as its pattern list, with the order of patterns preserved.

    Note that you should put newlines in your string if Enter is necessary.

    Like the example above, the responses may also contain callback functions.
    Any callback is a function that takes a dictionary as an argument.
    The dictionary contains all the locals from the run() function, so you can
    access the child spawn object or any other variable defined in run()
    (event_count, child, and extra_args are the most useful). A callback may
    return True to stop the current run process.  Otherwise run() continues
    until the next event. A callback may also return a string which will be
    sent to the child. 'extra_args' is not used by directly run(). It provides
    a way to pass data to a callback function through run() through the locals
    dictionary passed to a callback.
    '''
    return _run(command, timeout=timeout, withexitstatus=withexitstatus,
                events=events, extra_args=extra_args, logfile=logfile, cwd=cwd,
                env=env, _spawn=spawn)

def runu(command, timeout=30, withexitstatus=False, events=None,
        extra_args=None, logfile=None, cwd=None, env=None, **kwargs):
    """This offers the same interface as :func:`run`, but using unicode.

    Like :class:`spawnu`, you can pass ``encoding`` and ``errors`` parameters,
    which will be used for both input and output.
    """
    return _run(command, timeout=timeout, withexitstatus=withexitstatus,
                events=events, extra_args=extra_args, logfile=logfile, cwd=cwd,
                env=env, _spawn=spawnu, **kwargs)

def _run(command, timeout, withexitstatus, events, extra_args, logfile, cwd,
         env, _spawn, **kwargs):
    if timeout == -1:
        child = _spawn(command, maxread=2000, logfile=logfile, cwd=cwd, env=env,
                        **kwargs)
    else:
        child = _spawn(command, timeout=timeout, maxread=2000, logfile=logfile,
                cwd=cwd, env=env, **kwargs)
    if isinstance(events, list):
        patterns= [x for x,y in events]
        responses = [y for x,y in events]
    elif isinstance(events, dict):
        patterns = list(events.keys())
        responses = list(events.values())
    else:
        # This assumes EOF or TIMEOUT will eventually cause run to terminate.
        patterns = None
        responses = None
    child_result_list = []
    event_count = 0
    while True:
        try:
            index = child.expect(patterns)
            if isinstance(child.after, child.allowed_string_types):
                child_result_list.append(child.before + child.after)
            else:
                # child.after may have been a TIMEOUT or EOF,
                # which we don't want appended to the list.
                child_result_list.append(child.before)
            if isinstance(responses[index], child.allowed_string_types):
                child.send(responses[index])
            elif isinstance(responses[index], types.FunctionType) or \
                 isinstance(responses[index], types.MethodType):
                callback_result = responses[index](locals())
                sys.stdout.flush()
                if isinstance(callback_result, child.allowed_string_types):
                    child.send(callback_result)
                elif callback_result:
                    break
            else:
                raise TypeError('The callback must be a string or function.')
            event_count = event_count + 1
        except TIMEOUT:
            child_result_list.append(child.before)
            break
        except EOF:
            child_result_list.append(child.before)
            break
    child_result = child.string_type().join(child_result_list)
    if withexitstatus:
        child.close()
        return (child_result, child.exitstatus)
    else:
        return child_result

# vim: set shiftround expandtab tabstop=4 shiftwidth=4 ft=python autoindent :
