import os
import sys
import time
import select
import re
import pty
import tty
import termios
import errno
import signal
from contextlib import contextmanager

import ptyprocess
from ptyprocess.ptyprocess import use_native_pty_fork

from .exceptions import ExceptionPexpect, EOF, TIMEOUT
from .spawnbase import SpawnBase, SpawnBaseUnicode
from .utils import which, split_command_line

@contextmanager
def _wrap_ptyprocess_err():
    """Turn ptyprocess errors into our own ExceptionPexpect errors"""
    try:
        yield
    except ptyprocess.PtyProcessError as e:
        raise ExceptionPexpect(*e.args)

PY3 = (sys.version_info[0] >= 3)

class spawn(SpawnBase):
    '''This is the main class interface for Pexpect. Use this class to start
    and control child applications. '''
    ptyprocess_class = ptyprocess.PtyProcess

    # This is purely informational now - changing it has no effect
    use_native_pty_fork = use_native_pty_fork

    def __init__(self, command, args=[], timeout=30, maxread=2000,
                 searchwindowsize=None, logfile=None, cwd=None, env=None,
                 ignore_sighup=True, echo=True, preexec_fn=None):
        '''This is the constructor. The command parameter may be a string that
        includes a command and any arguments to the command. For example::

            child = pexpect.spawn('/usr/bin/ftp')
            child = pexpect.spawn('/usr/bin/ssh user@example.com')
            child = pexpect.spawn('ls -latr /tmp')

        You may also construct it with a list of arguments like so::

            child = pexpect.spawn('/usr/bin/ftp', [])
            child = pexpect.spawn('/usr/bin/ssh', ['user@example.com'])
            child = pexpect.spawn('ls', ['-latr', '/tmp'])

        After this the child application will be created and will be ready to
        talk to. For normal use, see expect() and send() and sendline().

        Remember that Pexpect does NOT interpret shell meta characters such as
        redirect, pipe, or wild cards (``>``, ``|``, or ``*``). This is a
        common mistake.  If you want to run a command and pipe it through
        another command then you must also start a shell. For example::

            child = pexpect.spawn('/bin/bash -c "ls -l | grep LOG > logs.txt"')
            child.expect(pexpect.EOF)

        The second form of spawn (where you pass a list of arguments) is useful
        in situations where you wish to spawn a command and pass it its own
        argument list. This can make syntax more clear. For example, the
        following is equivalent to the previous example::

            shell_cmd = 'ls -l | grep LOG > logs.txt'
            child = pexpect.spawn('/bin/bash', ['-c', shell_cmd])
            child.expect(pexpect.EOF)

        The maxread attribute sets the read buffer size. This is maximum number
        of bytes that Pexpect will try to read from a TTY at one time. Setting
        the maxread size to 1 will turn off buffering. Setting the maxread
        value higher may help performance in cases where large amounts of
        output are read back from the child. This feature is useful in
        conjunction with searchwindowsize.

        The searchwindowsize attribute sets the how far back in the incoming
        seach buffer Pexpect will search for pattern matches. Every time
        Pexpect reads some data from the child it will append the data to the
        incoming buffer. The default is to search from the beginning of the
        incoming buffer each time new data is read from the child. But this is
        very inefficient if you are running a command that generates a large
        amount of data where you want to match. The searchwindowsize does not
        affect the size of the incoming data buffer. You will still have
        access to the full buffer after expect() returns.

        The logfile member turns on or off logging. All input and output will
        be copied to the given file object. Set logfile to None to stop
        logging. This is the default. Set logfile to sys.stdout to echo
        everything to standard output. The logfile is flushed after each write.

        Example log input and output to a file::

            child = pexpect.spawn('some_command')
            fout = open('mylog.txt','wb')
            child.logfile = fout

        Example log to stdout::

            # In Python 2:
            child = pexpect.spawn('some_command')
            child.logfile = sys.stdout

            # In Python 3, spawnu should be used to give str to stdout:
            child = pexpect.spawnu('some_command')
            child.logfile = sys.stdout

        The logfile_read and logfile_send members can be used to separately log
        the input from the child and output sent to the child. Sometimes you
        don't want to see everything you write to the child. You only want to
        log what the child sends back. For example::

            child = pexpect.spawn('some_command')
            child.logfile_read = sys.stdout

        Remember to use spawnu instead of spawn for the above code if you are
        using Python 3.

        To separately log output sent to the child use logfile_send::

            child.logfile_send = fout

        If ``ignore_sighup`` is True, the child process will ignore SIGHUP
        signals. For now, the default is True, to preserve the behaviour of
        earlier versions of Pexpect, but you should pass this explicitly if you
        want to rely on it.

        The delaybeforesend helps overcome a weird behavior that many users
        were experiencing. The typical problem was that a user would expect() a
        "Password:" prompt and then immediately call sendline() to send the
        password. The user would then see that their password was echoed back
        to them. Passwords don't normally echo. The problem is caused by the
        fact that most applications print out the "Password" prompt and then
        turn off stdin echo, but if you send your password before the
        application turned off echo, then you get your password echoed.
        Normally this wouldn't be a problem when interacting with a human at a
        real keyboard. If you introduce a slight delay just before writing then
        this seems to clear up the problem. This was such a common problem for
        many users that I decided that the default pexpect behavior should be
        to sleep just before writing to the child application. 1/20th of a
        second (50 ms) seems to be enough to clear up the problem. You can set
        delaybeforesend to 0 to return to the old behavior. Most Linux machines
        don't like this to be below 0.03. I don't know why.

        Note that spawn is clever about finding commands on your path.
        It uses the same logic that "which" uses to find executables.

        If you wish to get the exit status of the child you must call the
        close() method. The exit or signal status of the child will be stored
        in self.exitstatus or self.signalstatus. If the child exited normally
        then exitstatus will store the exit return code and signalstatus will
        be None. If the child was terminated abnormally with a signal then
        signalstatus will store the signal value and exitstatus will be None.
        If you need more detail you can also read the self.status member which
        stores the status returned by os.waitpid. You can interpret this using
        os.WIFEXITED/os.WEXITSTATUS or os.WIFSIGNALED/os.TERMSIG.

        The echo attribute may be set to False to disable echoing of input.
        As a pseudo-terminal, all input echoed by the "keyboard" (send()
        or sendline()) will be repeated to output.  For many cases, it is
        not desirable to have echo enabled, and it may be later disabled
        using setecho(False) followed by waitnoecho().  However, for some
        platforms such as Solaris, this is not possible, and should be
        disabled immediately on spawn.
        
        If preexec_fn is given, it will be called in the child process before
        launching the given command. This is useful to e.g. reset inherited
        signal handlers.
        '''
        super(spawn, self).__init__(timeout=timeout, maxread=maxread, searchwindowsize=searchwindowsize,
                                    logfile=logfile)
        self.STDIN_FILENO = pty.STDIN_FILENO
        self.STDOUT_FILENO = pty.STDOUT_FILENO
        self.STDERR_FILENO = pty.STDERR_FILENO
        self.cwd = cwd
        self.env = env
        self.echo = echo
        self.ignore_sighup = ignore_sighup
        self.__irix_hack = sys.platform.lower().startswith('irix')
        if command is None:
            self.command = None
            self.args = None
            self.name = '<pexpect factory incomplete>'
        else:
            self._spawn(command, args, preexec_fn)

    def __str__(self):
        '''This returns a human-readable string that represents the state of
        the object. '''

        s = []
        s.append(repr(self))
        s.append('command: ' + str(self.command))
        s.append('args: %r' % (self.args,))
        s.append('searcher: %r' % (self.searcher,))
        s.append('buffer (last 100 chars): %r' % (
                self.buffer[-100:] if self.buffer else self.buffer,))
        s.append('before (last 100 chars): %r' % (
                self.before[-100:] if self.before else self.before,))
        s.append('after: %r' % (self.after,))
        s.append('match: %r' % (self.match,))
        s.append('match_index: ' + str(self.match_index))
        s.append('exitstatus: ' + str(self.exitstatus))
        s.append('flag_eof: ' + str(self.flag_eof))
        s.append('pid: ' + str(self.pid))
        s.append('child_fd: ' + str(self.child_fd))
        s.append('closed: ' + str(self.closed))
        s.append('timeout: ' + str(self.timeout))
        s.append('delimiter: ' + str(self.delimiter))
        s.append('logfile: ' + str(self.logfile))
        s.append('logfile_read: ' + str(self.logfile_read))
        s.append('logfile_send: ' + str(self.logfile_send))
        s.append('maxread: ' + str(self.maxread))
        s.append('ignorecase: ' + str(self.ignorecase))
        s.append('searchwindowsize: ' + str(self.searchwindowsize))
        s.append('delaybeforesend: ' + str(self.delaybeforesend))
        s.append('delayafterclose: ' + str(self.delayafterclose))
        s.append('delayafterterminate: ' + str(self.delayafterterminate))
        return '\n'.join(s)

    def _spawn(self, command, args=[], preexec_fn=None):
        '''This starts the given command in a child process. This does all the
        fork/exec type of stuff for a pty. This is called by __init__. If args
        is empty then command will be parsed (split on spaces) and args will be
        set to parsed arguments. '''

        # The pid and child_fd of this object get set by this method.
        # Note that it is difficult for this method to fail.
        # You cannot detect if the child process cannot start.
        # So the only way you can tell if the child process started
        # or not is to try to read from the file descriptor. If you get
        # EOF immediately then it means that the child is already dead.
        # That may not necessarily be bad because you may have spawned a child
        # that performs some task; creates no stdout output; and then dies.

        # If command is an int type then it may represent a file descriptor.
        if isinstance(command, type(0)):
            raise ExceptionPexpect('Command is an int type. ' +
                    'If this is a file descriptor then maybe you want to ' +
                    'use fdpexpect.fdspawn which takes an existing ' +
                    'file descriptor instead of a command string.')

        if not isinstance(args, type([])):
            raise TypeError('The argument, args, must be a list.')

        if args == []:
            self.args = split_command_line(command)
            self.command = self.args[0]
        else:
            # Make a shallow copy of the args list.
            self.args = args[:]
            self.args.insert(0, command)
            self.command = command

        command_with_path = which(self.command)
        if command_with_path is None:
            raise ExceptionPexpect('The command was not found or was not ' +
                    'executable: %s.' % self.command)
        self.command = command_with_path
        self.args[0] = self.command

        self.name = '<' + ' '.join(self.args) + '>'

        assert self.pid is None, 'The pid member must be None.'
        assert self.command is not None, 'The command member must not be None.'

        kwargs = {'echo': self.echo, 'preexec_fn': preexec_fn}
        if self.ignore_sighup:
            def preexec_wrapper():
                "Set SIGHUP to be ignored, then call the real preexec_fn"
                signal.signal(signal.SIGHUP, signal.SIG_IGN)
                if preexec_fn is not None:
                    preexec_fn()
            kwargs['preexec_fn'] = preexec_wrapper

        self.ptyproc = self.ptyprocess_class.spawn(self.args, env=self.env,
                                                   cwd=self.cwd, **kwargs)

        self.pid = self.ptyproc.pid
        self.child_fd = self.ptyproc.fd


        self.terminated = False
        self.closed = False

    def close(self, force=True):
        '''This closes the connection with the child application. Note that
        calling close() more than once is valid. This emulates standard Python
        behavior with files. Set force to True if you want to make sure that
        the child is terminated (SIGKILL is sent if the child ignores SIGHUP
        and SIGINT). '''

        self.flush()
        self.ptyproc.close()
        self.isalive()  # Update exit status from ptyproc
        self.child_fd = -1

    def isatty(self):
        '''This returns True if the file descriptor is open and connected to a
        tty(-like) device, else False.

        On SVR4-style platforms implementing streams, such as SunOS and HP-UX,
        the child pty may not appear as a terminal device.  This means
        methods such as setecho(), setwinsize(), getwinsize() may raise an
        IOError. '''

        return os.isatty(self.child_fd)

    def waitnoecho(self, timeout=-1):
        '''This waits until the terminal ECHO flag is set False. This returns
        True if the echo mode is off. This returns False if the ECHO flag was
        not set False before the timeout. This can be used to detect when the
        child is waiting for a password. Usually a child application will turn
        off echo mode when it is waiting for the user to enter a password. For
        example, instead of expecting the "password:" prompt you can wait for
        the child to set ECHO off::

            p = pexpect.spawn('ssh user@example.com')
            p.waitnoecho()
            p.sendline(mypassword)

        If timeout==-1 then this method will use the value in self.timeout.
        If timeout==None then this method to block until ECHO flag is False.
        '''

        if timeout == -1:
            timeout = self.timeout
        if timeout is not None:
            end_time = time.time() + timeout
        while True:
            if not self.getecho():
                return True
            if timeout < 0 and timeout is not None:
                return False
            if timeout is not None:
                timeout = end_time - time.time()
            time.sleep(0.1)

    def getecho(self):
        '''This returns the terminal echo mode. This returns True if echo is
        on or False if echo is off. Child applications that are expecting you
        to enter a password often set ECHO False. See waitnoecho().

        Not supported on platforms where ``isatty()`` returns False.  '''
        return self.ptyproc.getecho()

    def setecho(self, state):
        '''This sets the terminal echo mode on or off. Note that anything the
        child sent before the echo will be lost, so you should be sure that
        your input buffer is empty before you call setecho(). For example, the
        following will work as expected::

            p = pexpect.spawn('cat') # Echo is on by default.
            p.sendline('1234') # We expect see this twice from the child...
            p.expect(['1234']) # ... once from the tty echo...
            p.expect(['1234']) # ... and again from cat itself.
            p.setecho(False) # Turn off tty echo
            p.sendline('abcd') # We will set this only once (echoed by cat).
            p.sendline('wxyz') # We will set this only once (echoed by cat)
            p.expect(['abcd'])
            p.expect(['wxyz'])

        The following WILL NOT WORK because the lines sent before the setecho
        will be lost::

            p = pexpect.spawn('cat')
            p.sendline('1234')
            p.setecho(False) # Turn off tty echo
            p.sendline('abcd') # We will set this only once (echoed by cat).
            p.sendline('wxyz') # We will set this only once (echoed by cat)
            p.expect(['1234'])
            p.expect(['1234'])
            p.expect(['abcd'])
            p.expect(['wxyz'])


        Not supported on platforms where ``isatty()`` returns False.
        '''
        return self.ptyproc.setecho(state)

        self.echo = state

    def read_nonblocking(self, size=1, timeout=-1):
        '''This reads at most size characters from the child application. It
        includes a timeout. If the read does not complete within the timeout
        period then a TIMEOUT exception is raised. If the end of file is read
        then an EOF exception will be raised. If a log file was set using
        setlog() then all data will also be written to the log file.

        If timeout is None then the read may block indefinitely.
        If timeout is -1 then the self.timeout value is used. If timeout is 0
        then the child is polled and if there is no data immediately ready
        then this will raise a TIMEOUT exception.

        The timeout refers only to the amount of time to read at least one
        character. This is not effected by the 'size' parameter, so if you call
        read_nonblocking(size=100, timeout=30) and only one character is
        available right away then one character will be returned immediately.
        It will not wait for 30 seconds for another 99 characters to come in.

        This is a wrapper around os.read(). It uses select.select() to
        implement the timeout. '''

        if self.closed:
            raise ValueError('I/O operation on closed file.')

        if timeout == -1:
            timeout = self.timeout

        # Note that some systems such as Solaris do not give an EOF when
        # the child dies. In fact, you can still try to read
        # from the child_fd -- it will block forever or until TIMEOUT.
        # For this case, I test isalive() before doing any reading.
        # If isalive() is false, then I pretend that this is the same as EOF.
        if not self.isalive():
            # timeout of 0 means "poll"
            r, w, e = self.__select([self.child_fd], [], [], 0)
            if not r:
                self.flag_eof = True
                raise EOF('End Of File (EOF). Braindead platform.')
        elif self.__irix_hack:
            # Irix takes a long time before it realizes a child was terminated.
            # FIXME So does this mean Irix systems are forced to always have
            # FIXME a 2 second delay when calling read_nonblocking? That sucks.
            r, w, e = self.__select([self.child_fd], [], [], 2)
            if not r and not self.isalive():
                self.flag_eof = True
                raise EOF('End Of File (EOF). Slow platform.')

        r, w, e = self.__select([self.child_fd], [], [], timeout)

        if not r:
            if not self.isalive():
                # Some platforms, such as Irix, will claim that their
                # processes are alive; timeout on the select; and
                # then finally admit that they are not alive.
                self.flag_eof = True
                raise EOF('End of File (EOF). Very slow platform.')
            else:
                raise TIMEOUT('Timeout exceeded.')

        if self.child_fd in r:
            return super(spawn, self).read_nonblocking(size)

        raise ExceptionPexpect('Reached an unexpected state.')  # pragma: no cover

    def write(self, s):
        '''This is similar to send() except that there is no return value.
        '''

        self.send(s)

    def writelines(self, sequence):
        '''This calls write() for each element in the sequence. The sequence
        can be any iterable object producing strings, typically a list of
        strings. This does not add line separators. There is no return value.
        '''

        for s in sequence:
            self.write(s)

    def send(self, s):
        '''Sends string ``s`` to the child process, returning the number of
        bytes written. If a logfile is specified, a copy is written to that
        log.

        The default terminal input mode is canonical processing unless set
        otherwise by the child process. This allows backspace and other line
        processing to be performed prior to transmitting to the receiving
        program. As this is buffered, there is a limited size of such buffer.

        On Linux systems, this is 4096 (defined by N_TTY_BUF_SIZE). All
        other systems honor the POSIX.1 definition PC_MAX_CANON -- 1024
        on OSX, 256 on OpenSolaris, 255 on FreeBSD.

        This value may be discovered using fpathconf(3)::

        >>> from os import fpathconf
        >>> print(fpathconf(0, 'PC_MAX_CANON'))
        256

        On such a system, only 256 bytes may be received per line. Any
        subsequent bytes received will be discarded. BEL (``'\a'``) is then
        sent to output if IMAXBEL (termios.h) is set by the tty driver.
        This is usually enabled by default.  Linux does not honor this as
        an option -- it behaves as though it is always set on.

        Canonical input processing may be disabled altogether by executing
        a shell, then stty(1), before executing the final program::

        >>> bash = pexpect.spawn('/bin/bash', echo=False)
        >>> bash.sendline('stty -icanon')
        >>> bash.sendline('base64')
        >>> bash.sendline('x' * 5000)
        '''

        time.sleep(self.delaybeforesend)

        s = self._coerce_send_string(s)
        self._log(s, 'send')

        return self._send(s)

    def _send(self, s):
        return os.write(self.child_fd, s)

    def sendline(self, s=''):
        '''Wraps send(), sending string ``s`` to child process, with
        ``os.linesep`` automatically appended. Returns number of bytes
        written.  Only a limited number of bytes may be sent for each
        line in the default terminal mode, see docstring of :meth:`send`.
        '''

        n = self.send(s)
        n = n + self.send(self.linesep)
        return n

    def _log_control(self, byte):
        """Write control characters to the appropriate log files"""
        self._log(byte, 'send')

    def sendcontrol(self, char):
        '''Helper method that wraps send() with mnemonic access for sending control
        character to the child (such as Ctrl-C or Ctrl-D).  For example, to send
        Ctrl-G (ASCII 7, bell, '\a')::

            child.sendcontrol('g')

        See also, sendintr() and sendeof().
        '''
        n, byte = self.ptyproc.sendcontrol(char)
        self._log_control(byte)
        return n

    def sendeof(self):
        '''This sends an EOF to the child. This sends a character which causes
        the pending parent output buffer to be sent to the waiting child
        program without waiting for end-of-line. If it is the first character
        of the line, the read() in the user program returns 0, which signifies
        end-of-file. This means to work as expected a sendeof() has to be
        called at the beginning of a line. This method does not send a newline.
        It is the responsibility of the caller to ensure the eof is sent at the
        beginning of a line. '''

        n, byte = self.ptyproc.sendeof()
        self._log_control(byte)

    def sendintr(self):
        '''This sends a SIGINT to the child. It does not require
        the SIGINT to be the first character on a line. '''

        n, byte = self.ptyproc.sendintr()
        self._log_control(byte)

    @property
    def flag_eof(self):
        return self.ptyproc.flag_eof

    @flag_eof.setter
    def flag_eof(self, value):
        self.ptyproc.flag_eof = value

    def eof(self):
        '''This returns True if the EOF exception was ever raised.
        '''
        return self.flag_eof

    def terminate(self, force=False):
        '''This forces a child process to terminate. It starts nicely with
        SIGHUP and SIGINT. If "force" is True then moves onto SIGKILL. This
        returns True if the child was terminated. This returns False if the
        child could not be terminated. '''

        if not self.isalive():
            return True
        try:
            self.kill(signal.SIGHUP)
            time.sleep(self.delayafterterminate)
            if not self.isalive():
                return True
            self.kill(signal.SIGCONT)
            time.sleep(self.delayafterterminate)
            if not self.isalive():
                return True
            self.kill(signal.SIGINT)
            time.sleep(self.delayafterterminate)
            if not self.isalive():
                return True
            if force:
                self.kill(signal.SIGKILL)
                time.sleep(self.delayafterterminate)
                if not self.isalive():
                    return True
                else:
                    return False
            return False
        except OSError:
            # I think there are kernel timing issues that sometimes cause
            # this to happen. I think isalive() reports True, but the
            # process is dead to the kernel.
            # Make one last attempt to see if the kernel is up to date.
            time.sleep(self.delayafterterminate)
            if not self.isalive():
                return True
            else:
                return False

    def wait(self):
        '''This waits until the child exits. This is a blocking call. This will
        not read any data from the child, so this will block forever if the
        child has unread output and has terminated. In other words, the child
        may have printed output then called exit(), but, the child is
        technically still alive until its output is read by the parent. '''

        ptyproc = self.ptyproc
        with _wrap_ptyprocess_err():
            exitstatus = ptyproc.wait()
        self.status = ptyproc.status
        self.exitstatus = ptyproc.exitstatus
        self.signalstatus = ptyproc.signalstatus
        self.terminated = True

        return exitstatus

    def isalive(self):
        '''This tests if the child process is running or not. This is
        non-blocking. If the child was terminated then this will read the
        exitstatus or signalstatus of the child. This returns True if the child
        process appears to be running or False if not. It can take literally
        SECONDS for Solaris to return the right status. '''

        ptyproc = self.ptyproc
        with _wrap_ptyprocess_err():
            alive = ptyproc.isalive()

        if not alive:
            self.status = ptyproc.status
            self.exitstatus = ptyproc.exitstatus
            self.signalstatus = ptyproc.signalstatus
            self.terminated = True

        return alive

    def kill(self, sig):

        '''This sends the given signal to the child application. In keeping
        with UNIX tradition it has a misleading name. It does not necessarily
        kill the child unless you send the right signal. '''

        # Same as os.kill, but the pid is given for you.
        if self.isalive():
            os.kill(self.pid, sig)

    def getwinsize(self):
        '''This returns the terminal window size of the child tty. The return
        value is a tuple of (rows, cols). '''
        return self.ptyproc.getwinsize()

    def setwinsize(self, rows, cols):
        '''This sets the terminal window size of the child tty. This will cause
        a SIGWINCH signal to be sent to the child. This does not change the
        physical window size. It changes the size reported to TTY-aware
        applications like vi or curses -- applications that respond to the
        SIGWINCH signal. '''
        return self.ptyproc.setwinsize(rows, cols)


    def interact(self, escape_character=chr(29),
            input_filter=None, output_filter=None):

        '''This gives control of the child process to the interactive user (the
        human at the keyboard). Keystrokes are sent to the child process, and
        the stdout and stderr output of the child process is printed. This
        simply echos the child stdout and child stderr to the real stdout and
        it echos the real stdin to the child stdin. When the user types the
        escape_character this method will stop. The default for
        escape_character is ^]. This should not be confused with ASCII 27 --
        the ESC character. ASCII 29 was chosen for historical merit because
        this is the character used by 'telnet' as the escape character. The
        escape_character will not be sent to the child process.

        You may pass in optional input and output filter functions. These
        functions should take a string and return a string. The output_filter
        will be passed all the output from the child process. The input_filter
        will be passed all the keyboard input from the user. The input_filter
        is run BEFORE the check for the escape_character.

        Note that if you change the window size of the parent the SIGWINCH
        signal will not be passed through to the child. If you want the child
        window size to change when the parent's window size changes then do
        something like the following example::

            import pexpect, struct, fcntl, termios, signal, sys
            def sigwinch_passthrough (sig, data):
                s = struct.pack("HHHH", 0, 0, 0, 0)
                a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(),
                    termios.TIOCGWINSZ , s))
                global p
                p.setwinsize(a[0],a[1])
            # Note this 'p' global and used in sigwinch_passthrough.
            p = pexpect.spawn('/bin/bash')
            signal.signal(signal.SIGWINCH, sigwinch_passthrough)
            p.interact()
        '''

        # Flush the buffer.
        self.write_to_stdout(self.buffer)
        self.stdout.flush()
        self.buffer = self.string_type()
        mode = tty.tcgetattr(self.STDIN_FILENO)
        tty.setraw(self.STDIN_FILENO)
        if PY3:
            escape_character = escape_character.encode('latin-1')
        try:
            self.__interact_copy(escape_character, input_filter, output_filter)
        finally:
            tty.tcsetattr(self.STDIN_FILENO, tty.TCSAFLUSH, mode)

    def __interact_writen(self, fd, data):
        '''This is used by the interact() method.
        '''

        while data != b'' and self.isalive():
            n = os.write(fd, data)
            data = data[n:]

    def __interact_read(self, fd):
        '''This is used by the interact() method.
        '''

        return os.read(fd, 1000)

    def __interact_copy(self, escape_character=None,
            input_filter=None, output_filter=None):

        '''This is used by the interact() method.
        '''

        while self.isalive():
            r, w, e = self.__select([self.child_fd, self.STDIN_FILENO], [], [])
            if self.child_fd in r:
                try:
                    data = self.__interact_read(self.child_fd)
                except OSError as err:
                    if err.args[0] == errno.EIO:
                        # Linux-style EOF
                        break
                    raise
                if data == b'':
                    # BSD-style EOF
                    break
                if output_filter:
                    data = output_filter(data)
                if self.logfile is not None:
                    self.logfile.write(data)
                    self.logfile.flush()
                os.write(self.STDOUT_FILENO, data)
            if self.STDIN_FILENO in r:
                data = self.__interact_read(self.STDIN_FILENO)
                if input_filter:
                    data = input_filter(data)
                i = data.rfind(escape_character)
                if i != -1:
                    data = data[:i]
                    self.__interact_writen(self.child_fd, data)
                    break
                self.__interact_writen(self.child_fd, data)

    def __select(self, iwtd, owtd, ewtd, timeout=None):

        '''This is a wrapper around select.select() that ignores signals. If
        select.select raises a select.error exception and errno is an EINTR
        error then it is ignored. Mainly this is used to ignore sigwinch
        (terminal resize). '''

        # if select() is interrupted by a signal (errno==EINTR) then
        # we loop back and enter the select() again.
        if timeout is not None:
            end_time = time.time() + timeout
        while True:
            try:
                return select.select(iwtd, owtd, ewtd, timeout)
            except select.error:
                err = sys.exc_info()[1]
                if err.args[0] == errno.EINTR:
                    # if we loop back we have to subtract the
                    # amount of time we already waited.
                    if timeout is not None:
                        timeout = end_time - time.time()
                        if timeout < 0:
                            return([], [], [])
                else:
                    # something else caused the select.error, so
                    # this actually is an exception.
                    raise


class spawnu(SpawnBaseUnicode, spawn):
    """Works like spawn, but accepts and returns unicode strings.

    Extra parameters:

    :param encoding: The encoding to use for communications (default: 'utf-8')
    :param errors: How to handle encoding/decoding errors; one of 'strict'
                   (the default), 'ignore', or 'replace', as described
                   for :meth:`~bytes.decode` and :meth:`~str.encode`.
    """
    ptyprocess_class = ptyprocess.PtyProcessUnicode

    def _send(self, s):
        return os.write(self.child_fd, s.encode(self.encoding, self.errors))

    def _log_control(self, byte):
        s = byte.decode(self.encoding, 'replace')
        self._log(s, 'send')
