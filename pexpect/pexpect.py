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

Pexpect is Open Source, free, and all that stuff.
License: Python Software Foundation License
         http://www.opensource.org/licenses/PythonSoftFoundation.html

Noah Spurrier

$Revision$
$Date$
"""
import os, sys
import select
import signal
import traceback
import re
import struct
from types import *
try:
    import pty
    import tty
    import termios
    import fcntl
except ImportError, e:
    raise ImportError, str(e) + """
A critical module was not found. Probably this OS does not support it.
Currently pexpect is intended for UNIX operating systems (including OS-X)."""

# Exception classes used by this module.
class ExceptionPexpect(Exception):
    """Base class for all exceptions raised by this module."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return `self.value`
class EOF(ExceptionPexpect):
    """Raised when EOF is read from a child."""
class TIMEOUT(ExceptionPexpect):
    """Raised when a read time exceeds the timeout."""
##class MAXBUFFER(ExceptionPexpect):
##    """Raised when a scan buffer fills before matching an expected pattern."""

class spawn:
    """This is the main class interface for Pexpect. Use this class to
    start and control child applications.
    """

    def __init__(self, command):
        """This is the constructor. The command parameter is a string
        that includes the path and any arguments to the command. For
        example:
            p = pexpect.spawn ('/usr/bin/ftp')
            p = pexpect.spawn ('/bin/ls -latr /tmp')
            p = pexpect.spawn ('/usr/bin/ssh some@host.com')
        After this the child application will be created and
        will be ready for action. See expect() and send()/sendline().
        """

        self.STDIN_FILENO = sys.stdin.fileno()
        self.STDOUT_FILENO = sys.stdout.fileno()
        self.STDERR_FILENO = sys.stderr.fileno()

        ### IMPLEMENT THIS FEATURE!!!
        self.maxbuffersize = 10000
        # anything before maxsearchsize point is preserved, but not searched.
        self.maxsearchsize = 1000

        self.timeout = 30.0 # Seconds
        self.child_fd = -1
        self.pid = None
        self.log_fd = -1
    
        self.before = None
        self.after = None
        self.match = None

        self.args = split_command_line(command)
        self.command = self.args[0]
            
        self.__spawn()

    def __del__(self):
        """This makes sure that no system resources are left open.
        Python only garbage collects Python objects. Since OS file descriptors
        are not Python objects, so they must be handled manually.
        """
        if self.child_fd is not -1:
            os.close (self.child_fd)

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
        # That may not necessarily be bad, because you may spawn a child
        # that performs some operator, creates no stdout output, and then dies.
        # It is a fuzzy edge case. Any child process that you are likely to
        # want to interact with Pexpect would probably not fall into this
        # category.
        # FYI, This essentially does a fork/exec operation.

        assert self.pid == None, 'The pid member is not None.'
        assert self.command != None, 'The command member is None.'

        if which(self.command) == None:
            raise ExceptionPexpect ('The command was not found or was not executable: %s.' % self.command)

        # This is necessary for isAlive() to work. Without this there is
        # no portable way to tell if a child process is a zombie.
        # Checking waitpid with WNOHANG option does not work and
        # checking waitpid without it would block if the child is not a zombie.
        # With this children should exit completely without going into
        # a zombie state. Note that some UNIX flavors may send the signal
        # before the child's pty output buffer is empty, while others
        # may send the signal only when the buffer is empty.
        # In the later case, isAlive() will always return true until the
        # output buffer is empty. Use expect_eof() to consume all child output.
        # This is not the same as the Zombie (waiting to die) problem.
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        try:
            self.pid, self.child_fd = pty.fork()
        except OSError, e:
            raise ExceptionPexpect('Pexpect: pty.fork() failed: ' + str(e))

        if self.pid == 0: # Child
            setwinsize(24, 80)
            os.execvp(self.command, self.args)
            raise ExceptionPexpect ('Reached an unexpected state in __spawn().')

        # Parent

    def fileno (self):
        """This returns the file descriptor of the pty for the child."""
        return self.child_fd

    def set_echo (self, on):
        """This sets the terminal echo-mode on or off."""
        new = termios.tcgetattr(self.child_fd)
        if on:
            new[3] = new[3] | termios.ECHO          # lflags
        else:
            new[3] = new[3] & ~termios.ECHO          # lflags
        termios.tcsetattr(self.child_fd, termios.TCSADRAIN, new)

    def log_open (self, filename):
        """This opens a log file. All data read from the child
        application will be written to the log file.
        This is very useful to use while creating scripts.
        You can use this to figure out exactly what the child
        is sending.
        """
        self.log_fd = os.open (filename, O_APPEND | O_CREAT)
        
    def log_close (self):
        """This closes the log file opened by log().
        """
        os.close (self.log_fd)
        self.log_fd = -1
        
    def compile_pattern_list(self, pattern):
        """This compiles a pattern-string or a list of pattern-strings.
        This is used by expect() when calling expect_list().
        Thus expect() is nothing more than::
             cpl = self.compile_pattern_list(pl)
             return self.expect_list(clp, timeout)

        If you are using expect() within a loop it may be more
        efficient to compile the patterns first and call expect_list():
             cpl = self.compile_pattern_list(my_pattern)
             while some_condition:
                ...
                i = self.expect_list(clp, timeout)
                ...
        """
        if pattern is EOF:
            compiled_pattern_list = [EOF]
        elif type(pattern) is StringType:
            compiled_pattern_list = [re.compile(pattern)]
        elif type(pattern) is ListType:
            compiled_pattern_list = []
            for x in pattern:
                if x is EOF:
                    compiled_pattern_list.append(EOF)
                else:
                    compiled_pattern_list.append( re.compile(x) )
        else:
            raise TypeError, 'Pattern argument must be a string or a list of strings.'

        return compiled_pattern_list
 
    def expect(self, pattern, timeout = None):
        """This seeks through the stream looking for the given
        pattern. The 'pattern' can be a string or a list of strings.
        The strings are regular expressions (see module 're'). This
        returns the index into the pattern list or raises an exception
        on error.

        After a match is found the instance attributes
	'before', 'after' and 'match' will be set.
	You can see all the data read before the match in 'before'.
	You can see the data that was matched in 'after'.
	The re.MatchObject used in the re match will be in 'match'.
        If an error occured then 'before' will be set to all the
	data read so far and 'after' and 'match' will be None.

        Note: A list entry may be EOF instead of a string.
	This will catch EOF exceptions and return the index
	of the EOF entry instead of raising the EOF exception.
	The attributes 'after' and 'match' will be None.
	This allows you to write code like this:
		index = p.expect (['good', 'bad', pexpect.EOF])
		if index == 0:
			do_something()
		elif index == 1:
			do_something_else()
		elif index == 2:
			do_some_other_thing()
	instead of code like this:
		try:
			index = p.expect (['good', 'bad'])
			if index == 0:
				do_something()
			elif index == 1:
				do_something_else()
		except EOF:
			do_some_other_thing()
	These two forms are equivalent. It all depends on what you want.
	You can also just expect the EOF if you are waiting for all output
	of a child to finish. For example:
		p = pexpect.spawn('/bin/ls')
		p.expect (pexpect.EOF)
		print p.before
        """
        compiled_pattern_list = self.compile_pattern_list(pattern)
        return self.expect_list(compiled_pattern_list, timeout)

    def expect_exact (self, pattern_list, local_timeout = None):
        """This is similar to expect() except that it takes
        list of regular strings instead of compiled regular expressions.
        The idea is that this should be much faster. It could also be
        useful when you don't want to have to worry about escaping
        regular expression characters that you want to match.
        You may also pass just a string without a list and the single
        string will be converted to a list.
        """
        ### This is dumb. It shares most of the code with expect_list.
        ### The only different is the comparison method and that
        ### self.match is always None after calling this.

        if type(pattern_list) is StringType:
            pattern_list = [pattern_list]

        try:
            incoming = ''
            while 1: # Keep reading until exception or return.
                c = self.read(1, local_timeout)
                incoming = incoming + c

                # Sequence through the list of patterns and look for a match.
                index = -1
                for str_target in pattern_list:
                    index = index + 1
                    match_index = incoming.find (str_target)
                    if match_index >= 0:
                        self.before = incoming [ : match_index]
                        self.after = incoming [match_index : ]
                        self.match = None
                        return index
        except EOF, e:
            if EOF in pattern_list:
                self.before = incoming
                self.after = EOF
                return pattern_list.index(EOF)
            else:
                raise
        except Exception, e:
            self.before = incoming
            self.after = None
            self.match = None
            raise
            
        assert 0 == 1, 'Should not get here.'

    def expect_list(self, pattern_list, local_timeout = None):
        """This is called by expect(). This takes a list of compiled
        regular expressions. This returns the index into the pattern_list
	that matched the child's output.

        """

        if local_timeout is None: 
            local_timeout = self.timeout
        
        try:
            incoming = ''
            while 1: # Keep reading until exception or return.
                c = self.read(1, local_timeout)
                incoming = incoming + c

                # Sequence through the list of patterns and look for a match.
                index = -1
                for cre in pattern_list:
                    index = index + 1
                    if cre is EOF: 
                        continue # The EOF pattern is not a regular expression.
                    match = cre.search(incoming)
                    if match is not None:
                        self.before = incoming[ : match.start()]
                        self.after = incoming[match.start() : ]
                        self.match = match
                        return index
        except EOF, e:
            if EOF in pattern_list:
                self.before = incoming
                self.after = EOF
                return pattern_list.index(EOF)
            else:
                raise
        except Exception, e:
            self.before = incoming
            self.after = None
            self.match = None
            raise
            
        assert 0 == 1, 'Should not get here.'
        
#    def expect_eof(self, timeout = None):
#        """This reads from the child until the end of file is found.
#        A timeout exception may be thrown.
#        """
#        if timeout is None: 
#            timeout = self.timeout
#
#        incoming = ''
#        self.match = self.matched = None
#        try:
#            while 1:
#                c = self.read(1, timeout)
#                incoming = incoming + c
#        except EOF:
#            self.before = incoming
#            return 0
#        except:  # save incoming data (usefull for debugging)
#            self.before = incoming
#            raise

    def read(self, n, timeout = None):
        """This reads up to n characters from the child application.
        It includes a timeout. If the read does not complete within the
        timeout period then a TIMEOUT exception is raised.
        If the end of file is read then an EOF exception will be raised.
        If a log file was opened using log_open() then all data will
        also be written to the log file.

        Note that if this method is called with timeout=None 
        then it actually may block.
        This is a non-blocking wrapper around os.read().
        It uses select.select() to supply a timeout. 
        """
        r, w, e = select.select([self.child_fd], [], [], timeout)
        if not r:
            raise TIMEOUT('Timeout exceeded in read().')

        if self.child_fd in r:
            try:
                s = os.read(self.child_fd, n)
            except OSError, e:
                self.flag_eof = 1
                raise EOF('End Of File (EOF) in read(). Exception style platform.')
            if s == '':
                self.flag_eof = 1
                raise EOF('End Of File (EOF) in read(). Empty string style platform.')
            
            if self.log_fd != -1:
                os.write (self.log_fd, s)
                
            return s

        raise ExceptionPexpect('Reached an unexpected state in read().')

    def write(self, text):
        """This is an alias for send()."""
        self.send (text)

    def writelines (self, sequence):
        for str in sequence:
            self.write (str)

    def send(self, text):
        """This sends a string to the child process.
        """
        try:
            if text == EOF:
                self.senf_eof
                
            os.write(self.child_fd, text)
        except Exception, e:
            msg = 'Exception caught in send(): %s' % str(e)
            raise ExceptionPexpect(msg)

    def sendline(self, text):
        """This is like send(), but it adds a line separator.
        """
        self.send(text)
        self.send(os.linesep)

    def send_eof(self):
        """This sends an EOF to the child.

        More precisely: this sends a character which causes the pending
        child buffer to be sent to the waiting user program without
        waiting for end-of-line. If it is the first character of the
        line, the read() in the user program returns 0, which
        signifies end-of-file.

        This means: do make this work as expected send_eof() has to be
        called at the begining of a line. A newline-charakter is _not_
        send here to avoid problems.
        """
        ### Known Bug: this should either get the EOF character from
        ### termios or set (and restore) it. Currently the character
        ### is hard-coded here.
        ### EOF = '\004'
        ### Hmmm... how do I send an EOF?
        ###C  if ((m = write(pty, *buf, p - *buf)) < 0)
        ###C      return (errno == EWOULDBLOCK) ? n : -1;

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd) # remember current state
        new = termios.tcgetattr(fd)
        new[3] = new[3] | termios.ICANON        # lflags
        # use try/finally to ensure state gets restored
        try:
            # EOF is recognized when ICANON is set, thus ensure it is:
            termios.tcsetattr(fd, termios.TCSADRAIN, new)
            os.write(self.child_fd, termios.CEOF) ### This was based from EOF = '\004'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old) # restore state
        
    def isAlive(self):
        """This tests if the child process is running or not.
        It returns 1 if the child process appears to be running or
        0 if not. This checks the process list to see if the pid is
        there. In theory, the original child could have died and the
        pid could have been reused by some other process. This is
        unlikely, but I can find no portable way to make sure.
        Also, this is not POSIX portable way to check, but
        UNIX provides no standard way to test if a given pid is
        running or not. By convention most modern UNIX systems will
        respond to signal 0.
        """
        try:
            self.kill(0)
            return 1
        except OSError, e:
            return 0
            ###return e.errno == errno.EPERM
            ### For some reason I got this exception printed even though
            ### I am explicitly catching OSError. Noah doth halucinate?
            ###     OSError: [Errno 3] No such process

    def kill(self, sig):
        """This sends the given signal to the child application.
        In keeping with UNIX tradition it has a misleading name.
        It does not necessarily kill the child unless
        you send the right signal.
        """
        # Same as os.kill, but the pid is given for you.
        os.kill(self.pid, sig)

    def interact(self, escape_character = chr(29)):
        """This gives control of the child process to the interactive user.
        Keystrokes are sent to the child process, and the stdout and stderr
        output of the child process is printed.
        When the user types the escape_character this method will stop.
        The default for escape_character is ^] (ASCII 29).
        This simply echos the child stdout and child stderr to the real
        stdout and it echos the real stdin to the child stdin.
        """
        mode = tty.tcgetattr(self.STDIN_FILENO)
        tty.setraw(self.STDIN_FILENO)
        try:
            self.__interact_copy(escape_character)
        finally:
            tty.tcsetattr(self.STDIN_FILENO, tty.TCSAFLUSH, mode)

    def __interact_writen(self, fd, data):
        """This is used by the interact() method.
        """
        ### This is stupid. It's a deadlock waiting to happen.
        ### I can't check isAlive due to problems with OpenBSD handling.
        ### I can't think of a safe way to handle this.
        while data != '':
            n = os.write(fd, data)
            data = data[n:]
    def __interact_read(self, fd):
        """This is used by the interact() method.
        """
        return os.read(fd, 1000)
    def __interact_copy(self, escape_character = None):
        """This is used by the interact() method.
        """
        while self.isAlive():
            r, w, e = select.select([self.child_fd, self.STDIN_FILENO], [], [])
            if self.child_fd in r:
                data = self.__interact_read(self.child_fd)
                os.write(self.STDOUT_FILENO, data)
            if self.STDIN_FILENO in r:
                data = self.__interact_read(self.STDIN_FILENO)
                self.__interact_writen(self.child_fd, data)
                if escape_character in data:
                    break


##    def send_human(self, text, delay_min = 0, delay_max = 1):
##        pass
##    def spawn2(self, command, args):
##        """return pid, fd_stdio, fd_stderr
##        """
##        pass
##    def expect_ex(self, string_match, local_timeout = None):
##        """This is like expect(), except that instead of regular expression patterns
##        it matches on exact strings.
##        """
##        pass
##        # Return (data_read)


def which (filename):
    """This takes a given filename and tries to find it in the
    environment path and check if it is executable.
    """

    # Special case where filename already contains a path.
    if os.path.dirname(filename) != '':
        if os.access (filename, os.X_OK):
            return filename

    if not os.environ.has_key('PATH') or os.environ['PATH'] == '':
        p = os.defpath
    else:
        p = os.environ['PATH']

    pathlist = p.split (os.pathsep)

    for path in pathlist:
        f = os.path.join(path, filename)
        if os.access(f, os.X_OK):
            return f
    return None

def setwinsize(r, c):
    """This sets the windowsize of the tty for stdout.
    This does not change the physical window size.
    It changes the size reported to TTY-aware applications like
    vi or curses. In other words, applications that respond to the
    SIGWINCH signal.
    This is used by __spawn to set the tty window size of the child.
    """
    # Check for buggy platforms. Some Pythons on some platforms
    # (notably OSF1 Alpha and RedHat 7.1) truncate the value for
    # termios.TIOCSWINSZ. It is not clear why this happens.
    # These platforms don't seem to handle the signed int very well;
    # yet other platforms like OpenBSD have a large negative value for
    # TIOCSWINSZ and they don't truncate.
    # Newer versions of Linux have totally different values for TIOCSWINSZ.
    # Note, this fix is a hack.
    TIOCSWINSZ = termios.TIOCSWINSZ
    if TIOCSWINSZ == 2148037735L: # L is not required in Python 2.2.
        TIOCSWINSZ = -2146929561 # Same number in binary, but with sign.

    # Assume ws_xpixel and ws_ypixel are zero.
    s = struct.pack("HHHH", r, c, 0, 0)
    x = fcntl.ioctl(sys.stdout.fileno(), TIOCSWINSZ, s)

def getwinsize():
    s = struct.pack("HHHH", 0, 0, 0, 0)
    x = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
    return struct.unpack("HHHH", x)

def split_command_line(command_line):
    """This splits a command line into a list of arguments.
    It splits arguments on spaces, but handles
    embedded quotes, doublequotes, and escaped characters.
    I couldn't do this with a regular expression, so
    I wrote a little state machine to parse the command line.
    """
    arg_list = []
    arg = ''
    state_quote = 0
    state_doublequote = 0
    state_esc = 0
    for c in command_line:
        if c == '\\': # Escape the next character
            state_esc = 1
        elif c == r"'": # Handle single quote
            if state_esc:
                state_esc = 0
            elif not state_quote:
                state_quote = 1
            else:
                state_quote = 0
        elif c == r'"': # Handle double quote
            if state_esc:
                state_esc = 0
            elif not state_doublequote:
                state_doublequote = 1
            else:
                state_doublequote = 0

        # Add arg to arg_list unless in some other state.
        elif c == ' 'and not state_quote and not state_doublequote and not state_esc:
            arg_list.append(arg)
            arg = ''
        else:
            arg = arg + c
            if c != '\\'and state_esc: # escape mode lasts for one character.
                state_esc = 0

    # Handle last argument.        
    if arg != '':
        arg_list.append(arg)
    return arg_list

####################
#
#        NOTES
#
####################

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
# Advanced documentation:
#       Explain how patterns can be associated with actions.
#       Can I Do this without changing interface.

# Test bad fork
# Test ENOENT. In other words, no more TTY devices.

#GLOBAL_SIGCHLD_RECEIVED = 0
#def childdied (signum, frame):
#    print 'Signal handler called with signal', signum
#    frame.f_globals['pexpect'].GLOBAL_SIGCHLD_RECEIVED = 1
#    print str(frame.f_globals['pexpect'].GLOBAL_SIGCHLD_RECEIVED)
#    GLOBAL_SIGCHLD_RECEIVED = 1

### Add a greedy read -- like a readall() to keep reading until a
# timeout is returned. Will e.expect('') work? or e.expect(None)?

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
##            raise TIMEOUT('Read exceeded time: %d'%timeout)
##
##        if self.fd in r:
##            try:
##                s = os.read(self.fd, n)
##            except OSError, e:
##                self.flag_eof = 1
##                raise EOF('Read reached End Of File (EOF). Exception platform.')
##            if s == '':
##                self.flag_eof = 1
##                raise EOF('Read reached End Of File (EOF). Empty string platform.')
##            return s
##
##        self.flag_error = 1
##        raise ExceptionPexpect('PushbackReader.read() reached an unexpected state.'+
##        ' There is a logic error in the Pexpect source code.')
##
##    def pushback(self, data):
##        self.buffer = piece+self.buffer


