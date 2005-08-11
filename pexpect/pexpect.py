"""
Pexpect is a Python module for spawning child applications;
controlling them; and responding to expected patterns in their output.
Pexpect can be used for automating interactive applications such as
ssh, ftp, passwd, telnet, etc. It can be used to a automate setup scripts
for duplicating software package installations on different servers.
It can be used for automated software testing. Pexpect is in the spirit of
Don Libes' Expect, but Pexpect is pure Python. Other Expect-like
modules for Python require TCL and Expect or require C extensions to
be compiled. Pexpect does not use C, Expect, or TCL extensions. It
should work on any platform that supports the standard Python pty
module. The Pexpect interface focuses on ease of use so that simple
tasks are easy.

Pexpect is Open Source, Free, and all Good that stuff.
License: Python Software Foundation License
         http://www.opensource.org/licenses/PythonSoftFoundation.html

Noah Spurrier
Richard Holden
Marco Molteni
Kimberley Burchett 
Robert Stone
Mike Snitzer
Marti Raudsepp
Matt <matt (*) corvil.com>
Hartmut Goebel
Chad Schroeder
Erick Tryzelaar
(Let me know if I forgot anyone.)

$Revision$
$Date$
"""


try:
    import os, sys, time
    import select
    import string
    import re
    import struct
    import resource
    from types import *
    import pty
    import tty
    import termios
    import fcntl
    import errno
    import traceback
except ImportError, e:
    raise ImportError (str(e) + """
A critical module was not found. Probably this operating system does not support it.
Pexpect is intended for UNIX-like operating systems.""")

__version__ = '0.99999'
__revision__ = '$Revision$'
__all__ = ['ExceptionPexpect', 'EOF', 'TIMEOUT', 'TIMEOUT_PATTERN', 'spawn', 'run',
    '__version__', '__revision__']

# Exception classes used by this module.
class ExceptionPexpect(Exception):
    """Base class for all exceptions raised by this module."""
    def __init__(self, value, pattern_list = None):
        self.value = value
        self.pattern_list = pattern_list
    def __str__(self):
        if self.pattern_list is None:
            return str(self.value)
        string = str(self.value) + '\nPattern(s) to match:\n'
        for p in self.pattern_list:
            if type(p) is type(re.compile('')):
                string = string + p.pattern + '\n'
            else:
                string = string + str(p) + '\n'
        return string[:-1]
    def get_trace(self):
        """This returns an abbreviated stack trace with lines that only concern the caller.
        In other words, the stack trace inside the Pexpect module is not included.
        """
        tblist = traceback.extract_tb(sys.exc_info()[2])
        tblist = filter(self.__filter_not_pexpect, tblist)
        tblist = traceback.format_list(tblist)
        return ''.join(tblist)
    def __filter_not_pexpect(self, trace_list_item):
        if trace_list_item[0].find('pexpect.py') == -1:
            return True
        else:
            return False
class EOF(ExceptionPexpect):
    """Raised when EOF is read from a child."""
class TIMEOUT(ExceptionPexpect):
    """Raised when a read time exceeds the timeout."""
##class TIMEOUT_PATTERN(TIMEOUT):
##    """Raised when the pattern match time exceeds the timeout.
##    This is different than a read TIMEOUT because the child process may
##    give output, thus never give a TIMEOUT, but the output
##    may never match a pattern.
##    """
##class MAXBUFFER(ExceptionPexpect):
##    """Raised when a scan buffer fills before matching an expected pattern."""

def run (command, args=[], timeout=30):
    """This funnction runs the given command; waits for it to finish;
        then returns all output as a string. STDERR is included in output.
        This is a function interface to the spawn class.
        Note that lines are terminated by CR/LF (\\r\\n) combination
        even on UNIX-like systems because this is the standard for pseudo ttys.
    """
    child = spawn(command, args, timeout)
    child.expect (EOF)
    return child.before

class spawn:
    """This is the main class interface for Pexpect. Use this class to
    start and control child applications.
    """

    def __init__(self, command, args=[], timeout=30):
        """This is the constructor. The command parameter may be a string
        that includes a command and any arguments to the command. For example:
            p = pexpect.spawn ('/usr/bin/ftp')
            p = pexpect.spawn ('/usr/bin/ssh user@example.com')
            p = pexpect.spawn ('ls -latr /tmp')
        You may also construct it with a list of arguments like so:
            p = pexpect.spawn ('/usr/bin/ftp', [])
            p = pexpect.spawn ('/usr/bin/ssh', ['user@example.com'])
            p = pexpect.spawn ('ls', ['-latr', '/tmp'])
        After this the child application will be created and
        will be ready to talk to. For normal use, see expect() and 
        send() and sendline().

        If the command parameter is an integer AND a valid file descriptor
        then spawn will talk to the file descriptor instead. This can be
        used to act expect features to any file descriptor. For example:
            fd = os.open ('somefile.txt', os.O_RDONLY)
            s = pexpect.spawn (fd)
        The original creator of the file descriptor is responsible
        for closing it. Spawn will not try to close it and spawn will
        raise an exception if you try to call spawn.close().
        """

        self.STDIN_FILENO = pty.STDIN_FILENO
        self.STDOUT_FILENO = pty.STDOUT_FILENO
        self.STDERR_FILENO = pty.STDERR_FILENO

        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.timeout = timeout
        self.child_fd = -1 # initially closed
        self.__child_fd_owner = None
        self.exitstatus = None
        self.pid = None
        self.log_file = None    
        self.before = None
        self.after = None
        self.match = None
        self.softspace = 0 # File-like object.
        self.name = '' # File-like object.
        self.flag_eof = 0
        self.delimiter = EOF

        # NEW -- to support buffering -- the ability to read more than one 
        # byte from a TTY at a time. See setmaxread() method.
        self.buffer = ''
        self.maxread = 1 # Maximum to read at a time
        ### IMPLEMENT THIS FEATURE!!!
        # anything before maxsearchsize point is preserved, but not searched.
        #self.maxsearchsize = 1000
        
        # If command is an int type then it must represent an open file descriptor.
        if type (command) == type(0):
            try: # Command is an int, so now check if it is a file descriptor.
                os.fstat(command)
            except OSError:
                raise ExceptionPexpect ('Command is an int type, yet is not a valid file descriptor.')
            self.pid = -1 
            self.child_fd = command
            self.__child_fd_owner = 0 # Sets who is reponsible for the child_fd
            self.args = None
            self.command = None
            self.name = '<file descriptor>'
            return

        if type (args) != type([]):
            raise TypeError ('The second argument, args, must be a list.')

        if args == []:
            self.args = _split_command_line(command)
            self.command = self.args[0]
        else:
            self.args = args
            self.args.insert (0, command)
            self.command = command
        self.name = '<' + reduce(lambda x, y: x+' '+y, self.args) + '>'

        self.__spawn()

    def __del__(self):
        """This makes sure that no system resources are left open.
        Python only garbage collects Python objects. OS file descriptors
        are not Python objects, so they must be handled explicitly.
        If the child file descriptor was opened outside of this class
        (passed to the constructor) then this does not close it.
        """
        if self.__child_fd_owner:
            self.close()

    def __spawn(self):
        """This starts the given command in a child process. This does
        all the fork/exec type of stuff for a pty. This is called by
        __init__. The args parameter is a list, command is a string.
        """
        # The pid and child_fd of this object get set by this method.
        # Note that it is difficult for this method to fail.
        # You cannot detect if the child process cannot start.
        # So the only way you can tell if the child process started
        # or not is to try to read from the file descriptor. If you get
        # EOF immediately then it means that the child is already dead.
        # That may not necessarily be bad, because you may haved spawned a child
        # that performs some task; creates no stdout output; and then dies.
        # It is a fuzzy edge case. Any child process that you are likely to
        # want to interact with Pexpect would probably not fall into this
        # category.
        # FYI, This essentially does a fork/exec operation.

        assert self.pid == None, 'The pid member is not None.'
        assert self.command != None, 'The command member is None.'

        if _which(self.command) == None:
            raise ExceptionPexpect ('The command was not found or was not executable: %s.' % self.command)

        try:
            self.pid, self.child_fd = pty.fork()
        except OSError, e:
            raise ExceptionPexpect('Pexpect: pty.fork() failed: ' + str(e))

        if self.pid == 0: # Child
            try: # Some platforms do not like setwinsize (Cygwin).
                self.child_fd = sys.stdout.fileno()
                self.setwinsize(24, 80)
            except:
                pass
            # Do not allow child to inherit open file descriptors from parent.
            max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
            for i in range (3, max_fd):
                try:
                    os.close (i)
                except OSError:
                    pass

            os.execvp(self.command, self.args)

        # Parent
        self.__child_fd_owner = 1

    def fileno (self):   # File-like object.
        """This returns the file descriptor of the pty for the child."""
        return self.child_fd

    def close (self, wait=1):   # File-like object.
        """ This closes the connection with the child application.
        It makes no attempt to actually kill the child or wait for its status.
        If the file descriptor was set by passing a file descriptor
        to the constructor then this method raises an exception.
        Note that calling close() more than once is valid.
        This emulates standard Python behavior with files.
        If wait is set to True then close will wait
        for the exit status of the process. Doing a wait is a blocking call,
        but this usually takes almost no time at all. Generally,
        you don't have to worry about this. If you are
        creating lots of children then you usually want to call wait.
        Only set wait to false if you know the child will
        continue to run after closing the controlling TTY.
        Otherwise you will end up with defunct (zombie) processes.
        """
        if self.child_fd != -1:
            if not self.__child_fd_owner:
                raise ExceptionPexpect ('This file descriptor cannot be closed because it was not created by spawn. The original creator is responsible for closing it.')
            self.flush()
            os.close (self.child_fd)
            if wait:
                try:
                    pid, status = os.waitpid (self.pid, 0)
                    if os.WIFEXITED (status):
                        self.exitstatus = os.WEXITSTATUS(status)
                except OSError, e: ### suggested by Robert Stone
                    if e[0] == errno.ECHILD:
                        pass
                    else:
                        raise e
            self.child_fd = -1
            self.__child_fd_owner = None

    def flush (self):   # File-like object.
        """This does nothing. It is here to support the interface for a File-like object.
        """
        pass

    def isatty (self):   # File-like object.
        """This returns 1 if the file descriptor is open and
        connected to a tty(-like) device, else 0.
        """
        return os.isatty(self.child_fd)

    def setecho (self, on):
        """This sets the terminal echo mode on or off."""
        new = termios.tcgetattr(self.child_fd)
        if on:
            new[3] = new[3] | termios.ECHO # lflags
        else:
            new[3] = new[3] & ~termios.ECHO # lflags
        termios.tcsetattr(self.child_fd, termios.TCSADRAIN, new)

    def setlog (self, fileobject):
        """This sets logging output to go to the given fileobject.
        Set fileobject to None to stop logging. 
        Example:
            child = pexpect.spawn('some_command')
            fout = file('mylog.txt','w')
            child.setlog (fout)
            ...
        """
        self.log_file = fileobject

    def setmaxread (self, maxread):
        """This sets the maximum number of bytes to read from a TTY at one time.
        This is used to change the read buffer size. When a pexpect.spawn
        object is created the default maxread is 1 (unbuffered).
        Set this value higher to turn on buffer. This should help performance
        in cases where large amounts of output are read back from the child.
        """
        self.maxread = maxread

    def read_nonblocking (self, size = 1, timeout = None):
        """
        This reads at most size characters from the child application.
        It includes a timeout. If the read does not complete within the
        timeout period then a TIMEOUT exception is raised.
        If the end of file is read then an EOF exception will be raised.
        If a log file was set using setlog() then all data will
        also be written to the log file.

        Notice that if this method is called with timeout=None 
        then it actually may block.

        This is a non-blocking wrapper around os.read().
        It uses select.select() to implement a timeout. 
        """
        
        if self.child_fd == -1:
            raise ValueError ('I/O operation on closed file in read_nonblocking().')

        # Note that some systems like Solaris don't seem to ever give
        # an EOF when the child dies. In fact, you can still try to read
        # from the child_fd -- it will block forever or until TIMEOUT.
        # For this case, I test isalive() before doing any reading.
        # If isalive() is false, then I pretend that this is the same as EOF.
        if not self.isalive():
            r, w, e = select.select([self.child_fd], [], [], 0)
            if not r:
                self.flag_eof = 1
                raise EOF ('End Of File (EOF) in read_nonblocking(). Braindead platform.')

        r, w, e = select.select([self.child_fd], [], [], timeout)
        if not r:
            raise TIMEOUT ('Timeout exceeded in read_nonblocking().')
#            if not self.isalive():
#                raise EOF ('End of File (EOF) in read_nonblocking(). Really dumb platform.')
#            else:
#                raise TIMEOUT ('Timeout exceeded in read_nonblocking().')

        if self.child_fd in r:
            try:
                s = os.read(self.child_fd, size)
            except OSError, e:
                self.flag_eof = 1
                raise EOF ('End Of File (EOF) in read_nonblocking(). Exception style platform.')
            if s == '':
                self.flag_eof = 1
                raise EOF ('End Of File (EOF) in read_nonblocking(). Empty string style platform.')
            
            if self.log_file != None:
                self.log_file.write (s)
                self.log_file.flush()
                
            return s

        raise ExceptionPexpect ('Reached an unexpected state in read_nonblocking().')

    def read (self, size = -1):   # File-like object.
        """This reads at most size bytes from the file 
        (less if the read hits EOF before obtaining size bytes). 
        If the size argument is negative or omitted, 
        read all data until EOF is reached. 
        The bytes are returned as a string object. 
        An empty string is returned when EOF is encountered immediately.
        """
        if size == 0:
            return ''
        if size < 0:
            self.expect (self.delimiter) # delimiter default is EOF
            return self.before

        # I could have done this more directly by not using expect(), but
        # I deliberately decided to couple read() to expect() so that
        # I would catch any bugs early and ensure consistant behavior.
        # It's a little less efficient, but there is less for me to
        # worry about if I have to later modify read() or expect().
        cre = re.compile('.{%d}' % size, re.DOTALL) 
        index = self.expect ([cre, self.delimiter]) # delimiter default is EOF
        if index == 0:
            return self.after ### self.before should be ''. Should I assert this?
        return self.before
        
    def readline (self, size = -1):    # File-like object.
        """This reads and returns one entire line. A trailing newline is kept in
        the string, but may be absent when a file ends with an incomplete line. 
        Note: This readline() looks for a \\r\\n pair even on UNIX because this is 
        what the pseudo tty device returns. So contrary to what you may be used to
        you will receive a newline as \\r\\n.
        An empty string is returned when EOF is hit immediately.
        Currently, the size agument is mostly ignored, so this behavior is not
        standard for a file-like object. If size is 0 then an empty string is
        returned.
        """
        if size == 0:
            return ''
        index = self.expect (['\r\n', self.delimiter]) # delimiter default is EOF
        if index == 0:
            return self.before + '\r\n'
        else:
            return self.before

    def __iter__ (self):
        """This is to support interators over a file-like object.
        """
        return self
    def next (self):
        """This is to support iterators over a file-like object.
        """
        result = self.readline()
        if result == "":
            raise StopIteration
        return result

    def readlines (self, sizehint = -1):    # File-like object.
        """This reads until EOF using readline() and returns a list containing 
        the lines thus read. The optional sizehint argument is ignored.
        """        
        lines = []
        while 1:
            line = self.readline()
            if not line:
                break
            lines.append(line)
        return lines

    def write(self, str):   # File-like object.
        """This is similar to send() except that there is no return value.
        """
        self.send (str)

    def writelines (self, sequence):   # File-like object.
        """This calls write() for each element in the sequence.
        The sequence can be any iterable object producing strings, 
        typically a list of strings. This does not add line separators
        There is no return value.
        """
        for str in sequence:
            self.write (str)

    def send(self, str):
        """This sends a string to the child process.
        This returns the number of bytes written.
        """
        return os.write(self.child_fd, str)

    def sendline(self, str=''):
        """This is like send(), but it adds a line feed (os.linesep).
        This returns the number of bytes written.
        """
        n = self.send(str)
        n = n + self.send (os.linesep)
        return n

    def sendeof(self):
        """This sends an EOF to the child.
        This sends a character which causes the pending parent output
        buffer to be sent to the waiting child program without
        waiting for end-of-line. If it is the first character of the
        line, the read() in the user program returns 0, which
        signifies end-of-file. This means to work as expected 
        a sendeof() has to be called at the begining of a line. 
        This method does not send a newline. It is the responsibility
        of the caller to ensure the eof is sent at the beginning of a line.
        """
        ### Hmmm... how do I send an EOF?
        ###C  if ((m = write(pty, *buf, p - *buf)) < 0)
        ###C      return (errno == EWOULDBLOCK) ? n : -1;
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd) # remember current state
        new = termios.tcgetattr(fd)
        new[3] = new[3] | termios.ICANON # lflags
        # use try/finally to ensure state gets restored
        try:
            # EOF is recognized when ICANON is set, so make sure it is set.
            termios.tcsetattr(fd, termios.TCSADRAIN, new)
            os.write (self.child_fd, '%c' % termios.CEOF)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old) # restore state

    def eof (self):
        """This returns 1 if the EOF exception was raised at some point.
        """
        return self.flag_eof

    def isalive(self):
        """This tests if the child process is running or not.
        This returns 1 if the child process appears to be running or 0 if not.
        This also sets the exitstatus attribute.
        It can take literally SECONDS for Solaris to return the right status.
        This is the most wiggly part of Pexpect, but I think I've almost got
        it nailed down.
        """
        # I can't use signals. Signals on UNIX suck and they
        # mess up Python pipes (setting SIGCHLD to SIGIGNORE).

        # If this class was created from an existing file descriptor then
        # I just check to see if the file descriptor is still valid.
        if self.pid == -1 and not self.__child_fd_owner: 
            try:
                os.fstat(self.child_fd)
                return 1
            except:
                return 0

        try:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
        except OSError:
            return 0

        # I have to do this twice for Solaris.
        # I can't even believe that I figured this out...
        # If waitpid() returns 0 it means that no child process wishes to
        # report, and the value of status is undefined.
#        if pid == 0 and status == 0:
        if pid == 0:
            try:
                pid, status = os.waitpid(self.pid, os.WNOHANG)
                #print 'Solaris sucks'
            except OSError: # This is crufty. When does this happen?
                return 0
            # If pid and status is still 0 after two calls to waitpid() then
            # the process really is alive. This seems to work on all platforms.
#            if pid == 0 and status == 0:
            if pid == 0:
                return 1

        # I do not OR this together because I want hooks for debugging.
        if os.WIFEXITED (status):
            self.exitstatus = os.WEXITSTATUS(status)
            return 0
        elif os.WIFSTOPPED (status):
            return 0
        elif os.WIFSIGNALED (status):
            return 0
        else:
            return 0 # Can I ever get here?

    def kill(self, sig):
        """This sends the given signal to the child application.
        In keeping with UNIX tradition it has a misleading name.
        It does not necessarily kill the child unless
        you send the right signal.
        """
        # Same as os.kill, but the pid is given for you.
        if self.isalive():
            os.kill(self.pid, sig)

    def compile_pattern_list(self, patterns):
        """This compiles a pattern-string or a list of pattern-strings.
        Patterns must be a StringType, EOF, TIMEOUT, SRE_Pattern, or 
        a list of those.

        This is used by expect() when calling expect_list().
        Thus expect() is nothing more than::
             cpl = self.compile_pattern_list(pl)
             return self.expect_list(clp, timeout)

        If you are using expect() within a loop it may be more
        efficient to compile the patterns first and then call expect_list().
        This avoid calls in a loop to compile_pattern_list():
             cpl = self.compile_pattern_list(my_pattern)
             while some_condition:
                ...
                i = self.expect_list(clp, timeout)
                ...
        """
        if type(patterns) is not ListType:
            patterns = [patterns]

        compiled_pattern_list = []
        for p in patterns:
            if type(p) is StringType:
                compiled_pattern_list.append(re.compile(p, re.DOTALL))
            elif p is EOF:
                compiled_pattern_list.append(EOF)
            elif p is TIMEOUT:
                compiled_pattern_list.append(TIMEOUT)
            elif type(p) is type(re.compile('')):
                compiled_pattern_list.append(p)
            else:
                raise TypeError ('Argument must be one of StringType, EOF, TIMEOUT, SRE_Pattern, or a list of those type. %s' % str(type(p)))

        return compiled_pattern_list
 
    def expect(self, pattern, timeout = -1):
        """This seeks through the stream until a pattern is matched.
        The pattern is overloaded and may take several types including a list.
        The pattern can be a StringType, EOF, a compiled re, or
        a list of those types. Strings will be compiled to re types.
        This returns the index into the pattern list. If the pattern was
        not a list this returns index 0 on a successful match.
        This may raise exceptions for EOF or TIMEOUT.
        To avoid the EOF or TIMEOUT exceptions add EOF or TIMEOUT to
        the pattern list.

        After a match is found the instance attributes
        'before', 'after' and 'match' will be set.
        You can see all the data read before the match in 'before'.
        You can see the data that was matched in 'after'.
        The re.MatchObject used in the re match will be in 'match'.
        If an error occured then 'before' will be set to all the
        data read so far and 'after' and 'match' will be None.

        If timeout is -1 then timeout will be set to the self.timeout value.

        Note: A list entry may be EOF or TIMEOUT instead of a string.
        This will catch these exceptions and return the index
        of the list entry instead of raising the exception.
        The attribute 'after' will be set to the exception type.
        The attribute 'match' will be None.
        This allows you to write code like this:
                index = p.expect (['good', 'bad', pexpect.EOF, pexpect.TIMEOUT])
                if index == 0:
                    do_something()
                elif index == 1:
                    do_something_else()
                elif index == 2:
                    do_some_other_thing()
                elif index == 3:
                    do_something_completely_different()
        instead of code like this:
                try:
                    index = p.expect (['good', 'bad'])
                    if index == 0:
                        do_something()
                    elif index == 1:
                        do_something_else()
                except EOF:
                    do_some_other_thing()
                except TIMEOUT:
                    do_something_completely_different()
        These two forms are equivalent. It all depends on what you want.
        You can also just expect the EOF if you are waiting for all output
        of a child to finish. For example:
                p = pexpect.spawn('/bin/ls')
                p.expect (pexpect.EOF)
                print p.before

        If you are trying to optimize for speed then see
        expect_list() and expect_exact().
        """
        compiled_pattern_list = self.compile_pattern_list(pattern)
        return self.expect_list(compiled_pattern_list, timeout)

    def expect_exact (self, pattern_list, timeout = -1):
        """This method is no longer supported or allowed.
        It was too hard to maintain and keep it up to date with expect_list.
        Few people used this method. Most people favored reliability over speed.
        The implementation is left in comments in case anyone needs to hack this
        feature back into their copy.
        If someone wants to diff this with expect_list and make them work
        nearly the same then I will consider adding this make in.
        """
        raise ExceptionPexpect ('This method is no longer supported or allowed.')
#        """This is similar to expect() except that it takes
#        list of plain strings instead of regular expressions.
#        This should be much faster than expect(). It could also be
#        useful when you don't want to have to worry about escaping
#        regular expression characters that you want to match.
#        You may also pass just a string without a list and the string
#        will be automatically converted to a list with a single string element.
#        If timeout is -1 then timeout will be set to the self.timeout value.
#        See also expect_list() for speed optimization.
#        """
#        ### This is dumb. It shares most of the code with expect_list.
#        ### The only different is the comparison method and that
#        ### self.match is always None after calling this.
#        if timeout == -1:
#            timeout = self.timeout
#
#        if type(pattern_list) is StringType:
#            pattern_list = [pattern_list]
#
#        try:
#            #ED# incoming = ''
#            incoming = self.buffer
#            while 1: # Keep reading until exception or return.
#                #ED# c = self.read_nonblocking (1, timeout) 
#                #ED# incoming = incoming + c
#
#                # Sequence through the list of patterns and look for a match.
#                index = -1
#                for str_target in pattern_list:
#                    index = index + 1
#                    if str_target is EOF or str_target is TIMEOUT: 
#                        continue # The Exception patterns are handled differently.
#                    match_index = incoming.find (str_target)
#                    if match_index >= 0:
#                        self.before = incoming [ : match_index]
#                        self.after = incoming [match_index : ]
#                        self.buffer = incoming [match_index + len(str_target):]
#                        self.match = None
#                        return index
#                c = self.read_nonblocking (self.maxread, timeout) 
#                incoming = incoming + c
#                
#        except EOF:
#            self.before = incoming
#            self.after = EOF
#            if EOF in pattern_list:
#                #self.buffer = ''
#                return pattern_list.index(EOF)
#            else:
#                raise
#        except TIMEOUT, TimeOutInst:
#            self.before = incoming
#            self.after = TIMEOUT
#            if TIMEOUT in pattern_list:
#                #self.buffer = ''
#                return pattern_list.index(TIMEOUT)
#            else:
#                raise TIMEOUT (TimeOutInst.__str__(),pattern_list)
#        except Exception:
#            self.before = incoming
#            self.after = None
#            self.match = None
#            self.buffer = ''
#            raise
            
    def expect_list(self, pattern_list, timeout = -1):
        """
        This takes a list of compiled regular expressions and returns 
        the index into the pattern_list that matched the child's output.
        This is called by expect(). It is similar to the expect() method
        except that expect_list() is not overloaded and it does not have to
        compile the pattern list on every call. This will help if you are
        trying to optimize for speed. You must not pass
        anything except a list of compiled regular expressions.
        If timeout is -1 then timeout will be set to the self.timeout value.
        """

        if timeout == -1:
            timeout = self.timeout
            end_time = None
        if timeout != None:
            end_time = time.time() + timeout
 
        try:
            incoming = self.buffer
            while 1: # Keep reading until exception or return.
                # Sequence through the list of patterns looking for a match.
                index = -1
                for cre in pattern_list:
                    index = index + 1
                    if cre is EOF or cre is TIMEOUT: 
                        continue # The patterns for PexpectExceptions are handled differently.
                    match = cre.search(incoming)
                    if match is not None:
                        self.before = incoming[ : match.start()]
                        self.after = incoming[match.start() : ]
                        self.match = match
                        self.buffer = incoming[match.end() : ]
                        return index
                # No match, so read more data
                if timeout != None:
                    timeout = end_time - time.time()
                    if timeout <= 0:
                        raise TIMEOUT ('Timeout exceeded in expect_list().')
                c = self.read_nonblocking (self.maxread, timeout)
                incoming = incoming + c
        except EOF, e:
            self.before = incoming
            self.after = EOF
            if EOF in pattern_list:
                return pattern_list.index(EOF)
            else:
                raise EOF (str(e), pattern_list)
        except TIMEOUT, e:
            self.before = incoming
            self.after = TIMEOUT
            if TIMEOUT in pattern_list:
                return pattern_list.index(TIMEOUT)
            else:
                raise TIMEOUT (str(e), pattern_list)
        except Exception:
            self.before = incoming
            self.after = None
            self.match = None
            self.buffer = ''
            raise

    def getwinsize(self):
        """
        This returns the window size of the child tty.
        The return value is a tuple of (rows, cols).
        """

        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(self.fileno(), termios.TIOCGWINSZ, s)
        return struct.unpack('HHHH', x)[0:2]

    def setwinsize(self, r, c):
        """
        This sets the windowsize of the child tty.
        This will cause a SIGWINCH signal to be sent to the child.
        This does not change the physical window size.
        It changes the size reported to TTY-aware applications like
        vi or curses -- applications that respond to the SIGWINCH signal.
        """
        # Check for buggy platforms. Some Python versions on some platforms
        # (notably OSF1 Alpha and RedHat 7.1) truncate the value for
        # termios.TIOCSWINSZ. It is not clear why this happens.
        # These platforms don't seem to handle the signed int very well;
        # yet other platforms like OpenBSD have a large negative value for
        # TIOCSWINSZ and they don't have a truncate problem.
        # Newer versions of Linux have totally different values for TIOCSWINSZ.
        # Note that this fix is a hack.
        TIOCSWINSZ = termios.TIOCSWINSZ
        if TIOCSWINSZ == 2148037735L: # L is not required in Python >= 2.2.
            TIOCSWINSZ = -2146929561 # Same bits, but with sign.

        # Note, assume ws_xpixel and ws_ypixel are zero.
        s = struct.pack('HHHH', r, c, 0, 0)
        fcntl.ioctl(self.fileno(), TIOCSWINSZ, s)

    def interact(self, escape_character = chr(29)):
        """This gives control of the child process to the interactive user
        (the human at the keyboard).
        Keystrokes are sent to the child process, and the stdout and stderr
        output of the child process is printed.
        When the user types the escape_character this method will stop.
        The default for escape_character is ^] (ASCII 29).
        This simply echos the child stdout and child stderr to the real
        stdout and it echos the real stdin to the child stdin.
        """
        # Flush the buffer.
        self.stdout.write (self.buffer)
        self.buffer = ''
        self.stdout.flush()
        mode = tty.tcgetattr(self.STDIN_FILENO)
        tty.setraw(self.STDIN_FILENO)
        try:
            self.__interact_copy(escape_character)
        finally:
            tty.tcsetattr(self.STDIN_FILENO, tty.TCSAFLUSH, mode)

    def __interact_writen(self, fd, data):
        """This is used by the interact() method.
        """
        while data != '' and self.isalive():
            n = os.write(fd, data)
            data = data[n:]
    def __interact_read(self, fd):
        """This is used by the interact() method.
        """
        return os.read(fd, 1000)
    def __interact_copy(self, escape_character = None):
        """This is used by the interact() method.
        """
        while self.isalive():
            r, w, e = select.select([self.child_fd, self.STDIN_FILENO], [], [])
            if self.child_fd in r:
                data = self.__interact_read(self.child_fd)
                os.write(self.STDOUT_FILENO, data)
            if self.STDIN_FILENO in r:
                data = self.__interact_read(self.STDIN_FILENO)
                self.__interact_writen(self.child_fd, data)
                if escape_character in data:
                    break

##############################################################################
# End of Spawn
##############################################################################

def _which (filename):
    """This takes a given filename; tries to find it in the
    environment path; then checks if it is executable.
    """

    # Special case where filename already contains a path.
    if os.path.dirname(filename) != '':
        if os.access (filename, os.X_OK):
            return filename

    if not os.environ.has_key('PATH') or os.environ['PATH'] == '':
        p = os.defpath
    else:
        p = os.environ['PATH']

    # Oddly enough this was the one line that made Pexpect
    # incompatible with Python 1.5.2.
    #pathlist = p.split (os.pathsep) 
    pathlist = string.split (p, os.pathsep)

    for path in pathlist:
        f = os.path.join(path, filename)
        if os.access(f, os.X_OK):
            return f
    return None

def _split_command_line(command_line):
    """This splits a command line into a list of arguments.
    It splits arguments on spaces, but handles
    embedded quotes, doublequotes, and escaped characters.
    It's impossible to do this with a regular expression, so
    I wrote a little state machine to parse the command line.
    """
    arg_list = []
    arg = ''

    # Constants to name the states we can be in.
    state_basic = 0
    state_esc = 1
    state_singlequote = 2
    state_doublequote = 3
    state_whitespace = 4 # The state of consuming whitespace between commands.
    state = state_basic

    for c in command_line:
        if state == state_basic or state == state_whitespace:
            if c == '\\': # Escape the next character
                state = state_esc
            elif c == r"'": # Handle single quote
                state = state_singlequote
            elif c == r'"': # Handle double quote
                state = state_doublequote
            elif c.isspace():
                # Add arg to arg_list if we aren't in the middle of whitespace.
                if state == state_whitespace:
                    None # Do nothing.
                else:
                    arg_list.append(arg)
                    arg = ''
                    state = state_whitespace
            else:
                arg = arg + c
                state = state_basic
        elif state == state_esc:
            arg = arg + c
            state = state_basic
        elif state == state_singlequote:
            if c == r"'":
                state = state_basic
            else:
                arg = arg + c
        elif state == state_doublequote:
            if c == r'"':
                state = state_basic
            else:
                arg = arg + c

    if arg != '':
        arg_list.append(arg)
    return arg_list


####################
#
#        NOTES
#
####################

##    def send_human(self, text, delay_min = 0, delay_max = 1):
##        pass
##    def spawn2(self, command, args):
##        """return pid, fd_stdio, fd_stderr
##        """
##        pass


# Reason for double fork:
# http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC15
# Reason for ptys:
# http://www.erlenstar.demon.co.uk/unix/faq_4.html#SEC52

# Nonblocking on Win32?
# Reasearch this as a way to maybe make pipe work for Win32.
# http://groups.google.com/groups?q=setraw+tty&hl=en&selm=uvgpvisvk.fsf%40roundpoint.com&rnum=7
# 
#    if istty:
#        if os.name=='posix':
#            import tty
#            tty.setraw(sys.stdin.fileno())
#        elif os.name=='nt':
#            import win32file, win32con
#            hstdin = win32file._get_osfhandle(sys.stdin.fileno())
#            modes = (win32file.GetConsoleMode(hstdin)
#                     & ~(win32con.ENABLE_LINE_INPUT
#                         |win32con.ENABLE_ECHO_INPUT))
#            win32file.SetConsoleMode(hstdin, modes)

# Basic documentation:
#       Explain use of lists of patterns and return index.
#       Explain exceptions for non-handled special cases like EOF

# Test bad fork
# Test ENOENT. In other words, no more TTY devices.

#GLOBAL_SIGCHLD_RECEIVED = 0
#def childdied (signum, frame):
#    print 'Signal handler called with signal', signum
#    frame.f_globals['pexpect'].GLOBAL_SIGCHLD_RECEIVED = 1
#    print str(frame.f_globals['pexpect'].GLOBAL_SIGCHLD_RECEIVED)
#    GLOBAL_SIGCHLD_RECEIVED = 1

### Weird bug. If you read too fast after doing a sendline()
# Sometimes you will read the data back that you just sent even if
# the child did not echo the data. This is particularly a problem if
# you send a password.

# This was previously used to implement a look-ahead in reads.
# if the lookahead failed then Pexpect would "push-back" the data
# that was read. The idea was to allow read() to read blocks of data.
# What I do now is just read one character at a time and then try a
# match. This is not as efficient, but it works well enough for the
# output of most applications and it makes program logic much simpler.
##class PushbackReader:
##    """This class is a wrapper around os.read. It adds the features of buffering
##        to allow push-back of data and to provide a timeout on a read.
##    """
##    def __init__(self, file_descriptor):
##        self.fd = file_descriptor
##        self.buffer = ''
##
##    def read(self, n, timeout = None):
##        """This does a read restricted by a timeout and 
##        it includes any cached data from previous calls. 
##            This is a non-blocking wrapper around os.read.
##        it uses select.select to supply a timeout. 
##        Note that if this is called with timeout=None (the default)
##        then this actually MAY block.
##        """
##        # The read() call is a problem.
##        # Some platforms return an empty string '' at EOF.
##        # Whereas other platforms raise an Input/output exception.
##
##        avail = len(self.buffer)
##        if n > avail:
##            result = self.buffer
##            n = n-avail
##        else:
##            result = self.buffer[: n]
##            self.buffer = self.buffer[n:]
##
##        r, w, e = select.select([self.fd], [], [], timeout)
##        if not r:
##            self.flag_timeout = 1
##            raise TIMEOUT ('Read exceeded time: %d'%timeout)
##
##        if self.fd in r:
##            try:
##                s = os.read(self.fd, n)
##            except OSError, e:
##                self.flag_eof = 1
##                raise EOF ('Read reached End Of File (EOF). Exception platform.')
##            if s == '':
##                self.flag_eof = 1
##                raise EOF ('Read reached End Of File (EOF). Empty string platform.')
##            return s
##
##        self.flag_error = 1
##        raise ExceptionPexpect ('PushbackReader.read() reached an unexpected state.'+
##        ' There is a logic error in the Pexpect source code.')
##
##    def pushback(self, data):
##        self.buffer = piece+self.buffer


#def _setwinsize(r, c):
#    """This sets the windowsize of the tty for stdout.
#    This does not change the physical window size.
#    It changes the size reported to TTY-aware applications like
#    vi or curses -- applications that respond to the SIGWINCH signal.
#    This is used by __spawn to set the tty window size of the child.
#    """
#    # Check for buggy platforms. Some Pythons on some platforms
#    # (notably OSF1 Alpha and RedHat 7.1) truncate the value for
#    # termios.TIOCSWINSZ. It is not clear why this happens.
#    # These platforms don't seem to handle the signed int very well;
#    # yet other platforms like OpenBSD have a large negative value for
#    # TIOCSWINSZ and they don't truncate.
#    # Newer versions of Linux have totally different values for TIOCSWINSZ.
#    #
#    # Note that this fix is a hack.
#    TIOCSWINSZ = termios.TIOCSWINSZ
#    if TIOCSWINSZ == 2148037735L: # L is not required in Python 2.2.
#        TIOCSWINSZ = -2146929561 # Same number in binary, but with sign.
#
#    # Assume ws_xpixel and ws_ypixel are zero.
#    s = struct.pack("HHHH", r, c, 0, 0)
#    fcntl.ioctl(sys.stdout.fileno(), TIOCSWINSZ, s)
#
#def _getwinsize():
#    s = struct.pack("HHHH", 0, 0, 0, 0)
#    x = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
#    return struct.unpack("HHHH", x)

