"""This class extends pexpect.spawn to specialize setting up SSH connections.
This adds methods for login, logout, and expecting the shell prompt.
$Id$
"""
from pexpect import *
import pexpect

__all__ = ['ExceptionPxssh', 'pxssh']

# Exception classes used by this module.
class ExceptionPxssh(ExceptionPexpect):
    """Raised for pxssh exceptions.
    """

class pxssh (spawn):
    """This class extends pexpect.spawn to specialize setting up SSH connections.
    This adds methods for login, logout, and expecting the shell prompt.
    It does various tricky things to handle many situations in the SSH login process.
    For example, if the session is your first login, then pxssh automatically
    accepts the remote certificate; or if you have public key authentication setup
    then pxssh won't wait for the password prompt.

    pxssh uses the shell prompt to synchronize output from the remote host. In
    order to make this more robust it sets the shell prompt to something more
    unique than just $ or #. This should work on most Borne/Bash or Csh style
    shells.

    Example usage that runs a few commands on a remote server and prints the result:
        import pxssh
        import getpass
        try:                                                            
            s = pxssh.pxssh()
            hostname = raw_input('hostname: ')
            username = raw_input('username: ')
            password = getpass.getpass('password: ')
            s.login (hostname, username, password)
            s.sendline ('uptime')  # run a command
            s.prompt()             # match the prompt
            print s.before         # print everything before the prompt.
            s.sendline ('ls -l')
            s.prompt()
            print s.before
            s.sendline ('df')
            s.prompt()
            print s.before
            s.logout()
        except pxssh.ExceptionPxssh, e:
            print "pxssh failed on login."
            print str(e)

    """

# Python's super is super annoying.
# http://mail.python.org/pipermail/python-list/2006-February/325485.html
    def __init__ (self, timeout=30, maxread=2000, searchwindowsize=None, logfile=None, env=None):
        spawn.__init__(self, None, timeout=timeout, maxread=maxread, searchwindowsize=searchwindowsize, logfile=logfile, env=env)

        self.name = '<pxssh>'
        #super(spawn, self).__init__()
        # SUBTLE HACK ALERT!
        # Note that the command to set the prompt uses a slightly different string
        # than the regular expression to match it. This is because when you set the
        # prompt the command will echo back, but we don't want to match the echoed
        # command. So if we make the set command slightly different than the regex
        # we eliminate the problem. To make the set command different we add a
        # backslash in front of $. The $ doesn't need to be escaped, but it doesn't
        # hurt and serves to make the set prompt command different than the regex.
        self.UNIQUE_PROMPT = "\[PEXPECT\][\$\#] " # used to match the command-line prompt.
        self.GENERIC_PROMPT = r"][#$]|~[#$]|bash.*?[#$]|[#$] " # used to match the command-line prompt.
        self.PROMPT = self.UNIQUE_PROMPT # used to match the command-line prompt.
        # used to set shell command-line prompt to UNIQUE_PROMPT.
        self.PROMPT_SET_SH = "PS1='[PEXPECT]\$ '"
        self.PROMPT_SET_CSH = "set prompt='[PEXPECT]\$ '"
        self.auto_prompt_reset = True 

    ### TODO: This is getting messy and I'm pretty sure this isn't perfect.
    ### TODO: I need to draw a flow chart for this.
    def login (self,server,username,password='',terminal_type='ansi',original_prompt=None,login_timeout=10,port=None,auto_prompt_reset=True):
        """This logs the user into the given server. By default the original prompt
        is rather optimistic and should be considered more of an example. It's
        better to try to match the prompt as exactly as possible to prevent any
        false matches by server strings such as a "Message Of The Day" or
        something. The closer you can make the original_prompt match your real
        prompt then the better. A timeout will not necessarily cause the login
        to fail. In the case of a timeout we assume that the prompt was so
        weird that we could not match it. We still try to reset the prompt to
        something more unique. If that still fails then this raises an
        ExceptionPxssh exception.
        Set auto_prompt_reset to False to inhibit setting the prompt to
        the UNIQUE_PROMPT. By default pxssh will reset the command-line prompt
        which the prompt() method uses to match. You can turn this off, but
        this will break the prompt() method unless you also set the
        PROMPT attribute to the prompt you want to match.
        """
        if original_prompt is None:
            original_prompt = self.GENERIC_PROMPT
        if port is None:
            cmd = "ssh -l %s %s" % (username, server)
        else:
            cmd = "ssh -p %s -l %s %s" % (str(port),username,server)
        spawn._spawn(self, cmd)
        i = self.expect(["(?i)are you sure you want to continue connecting", original_prompt, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT, "(?i)connection closed by remote host"], timeout=login_timeout)
        if i==0: # New certificate -- always accept it. This is what you if SSH does not have the remote host's public key stored in the cache.
            self.sendline("yes")
            i = self.expect(["(?i)are you sure you want to continue connecting", original_prompt, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])
        if i==2: # password
            self.sendline(password)
            i = self.expect(["(?i)are you sure you want to continue connecting", original_prompt, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])
        if i==4:
            self.sendline(terminal_type)
            i = self.expect(["(?i)are you sure you want to continue connecting", original_prompt, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])

        if i==0:
            # This is weird. This should not happen twice in a row.
            self.close()
            #return False
            raise ExceptionPxssh ('Weird error. Got "are you sure" prompt twice.')
        elif i==1: # can occur if you have a public key pair set to authenticate. 
            ### TODO: May NOT be OK if expect() got tricked and matched a false prompt.
            pass
        elif i==2: # password prompt again
            # For incorrect passwords, some ssh servers will
            # ask for the password again, others return 'denied' right away.
            # If we get the password prompt again then this means
            # we didn't get the password right the first time. 
            self.close()
            #return False
            raise ExceptionPxssh ('password refused')
        elif i==3: # permission denied -- password was bad.
            self.close()
            #return False
            raise ExceptionPxssh ('permission denied')
        elif i==4: # terminal type again? WTF?
            self.close()
            #return False
            raise ExceptionPxssh ('Weird error. Got "terminal type" prompt twice.')
        elif i==5: # Timeout
            # This is tricky... I presume that we are at the command-line prompt.
            # It may be that the shell prompt was so weird that we couldn't match it.
            # Or it may be that we couldn't log in for some other reason.
            # I can't be sure, but it's safe to guess that we did loging because
            # if I presume wrong and we are not logged in then this should
            # be caught later when I try to set the shell prompt.
            pass
        elif i==6: # Connection closed by remote host
            self.close()
            #return False
            raise ExceptionPxssh ('connection closed')
        else: # Unexpected 
            self.close()
            #return False
            raise ExceptionPxssh ('unexpected login response')
        # We appear to be in.
        # set shell prompt to something unique.
        if auto_prompt_reset:
            if not self.set_unique_prompt():
                self.close()
                raise ExceptionPxssh ('could not set shell prompt\n'+self.before)
        return True

    def logout (self):
        """This sends exit to the remote shell.
        If there are stopped jobs then this sends exit twice.
        """
        self.sendline("exit")
        index = self.expect([EOF, "(?i)there are stopped jobs"])
        if index==1:
            self.sendline("exit")
            self.expect(EOF)
        self.close()

    def prompt (self, timeout=20):
        """This matches the shell prompt.
        This is little more than a short-cut to the expect() method.
        This returns True if the shell prompt was matched.
        This returns False if there was a timeout.
        Note that if you called login() with auto_prompt_reset
        set to False then you should have manually set the PROMPT
        attribute to a regex pattern for matching the prompt.
        """
        i = self.expect([self.PROMPT, TIMEOUT], timeout=timeout)
        if i==1:
            return False
        return True
        
    def set_unique_prompt (self):
        """This sets the remote shell prompt to something more unique than
        # or $. This makes it easier for the prompt() method to match the shell
        prompt unambiguously. This method is called automatically by the
        login() method, but you may want to call it manually if you somehow
        reset the shell prompt. For example, if you 'su' to a different user
        then you will need to manually reset the prompt. This sends shell
        commands to the remote host to set the prompt, so this assumes the
        remote host is ready to receive commands.

        You can also set your own prompt and set the PROMPT attribute
        to a regular expression that matches it.
        """
        self.sendline (self.PROMPT_SET_SH) # sh-style
        i = self.expect ([TIMEOUT, self.PROMPT], timeout=10)
        if i == 0: # csh-style
            self.sendline (self.PROMPT_SET_CSH)
            i = self.expect ([TIMEOUT, self.PROMPT], timeout=10)
            if i == 0:
                return False
        return True

