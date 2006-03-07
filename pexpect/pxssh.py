"""This class extends pexpect.spawn to specialize setting up SSH connections.
This adds methods for login, logout, and expecting the prompt.

TODO: 
* set_unique_prompt() is using a hard-coded constant for PROMPT.
  That should be configurable.
* login() needs a state machine or at least a clear flow chart of the login process.
* login() needs some ability to fall-back to a fail-safe login method on timeout.
  If he login is taking too long then I should 'punt' and try setting the prompt anyway.
  Perhaps use some sort of prompt challange-response.
"""
from pexpect import *
import os, sys, getopt, shutil
import signal, struct, fcntl, termios
from time import sleep

# used to set shell command-line prompt to something more unique.
PROMPT = "\[PEXPECT\]\$ "
# SUBTLE HACK ALERT!
# Note that the command to set the prompt uses a slightly different string
# than the regular expression to match it. This is because when you set the
# prompt the command will echo back, but we don't want to match the echoed
# command. So if we make the set command slightly different than the regex
# we eliminate the problem. To make the set command different we add a
# backslash in front of $. The $ doesn't need to be escaped, but it doesn't
# hurt and serves to make the set command different than the regex.

class pxssh (spawn):
    """This extends the spawn class to specialize for running 'ssh' command-line client.
        This adds methods to login, logout, and expect_prompt.
    """

    def __init__ (self):
        self.PROMPT = "\[PEXPECT\]\$ "

    # I need to draw a better flow chart for this.
    ### TODO: This is getting messy and I'm pretty sure this isn't perfect.
    def login (self,server,username,password,terminal_type='ansi',original_prompts=r"][#$]|~[#$]|bash.*?[#$]| [#$] ",login_timeout=10):
        """This logs the user into the given server.
            By default the prompy is rather optimistic and should be considered more of an example.
            It's better to try to match the prompt as exactly as possible to prevent any false matches
            by a login Message Of The Day or something.
        """
        cmd = "ssh -l %s %s" % (username, server)
        spawn.__init__(self, cmd, timeout=login_timeout)
        #, "(?i)no route to host"])
        i = self.expect(["(?i)are you sure you want to continue connecting", original_prompts, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])
        if i==0: # New certificate -- always accept it. This is what you if SSH does not have the remote host's public key stored in the cache.
            self.sendline("yes")
            i = self.expect(["(?i)are you sure you want to continue connecting", original_prompts, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])
        if i==2: # password
            self.sendline(password)
            i = self.expect(["(?i)are you sure you want to continue connecting", original_prompts, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])
        if i==4:
            self.sendline(terminal_type)
            i = self.expect(["(?i)are you sure you want to continue connecting", original_prompts, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])

        if i==0:
            # This is weird. This should not happen twice in a row.
            self.close()
            return False
        elif i==1: # can occur if you have a public key pair set to authenticate. 
            ### TODO: May NOT be OK if expect false matched a prompt.
            pass
        elif i==2: # password prompt again
            # Some ssh servers will ask again for password, others print permission denied right away.
            # If you get the password prompt again then it means we didn't get the password right
            # the first time. 
            self.close()
            return False
        elif i==3: # permission denied -- password was bad.
            self.close()
            return False
        elif i==4: # terminal type again? WTF?
            self.close()
            return False
        elif i==5: # Timeout
            # This is tricky... presume that we are at the command-line prompt.
            # It may be that the prompt was so weird that we couldn't match it.
            pass
        else: # Unexpected 
            self.close()
            return False
        # We appear to have logged in -- reset command line prompt to something more unique.
        if not self.set_unique_prompt():
            self.close()
            return False
        return True

    def logout (self):
        """This sends exit. If there are stopped jobs then this sends exit twice.
        """
        self.sendline("exit")
        index = self.expect([EOF, "(?i)there are stopped jobs"])
        if index==1:
            self.sendline("exit")
            self.expect(EOF)

    def prompt (self, prompt_timeout=20):
        """This expects the prompt. This returns True if the prompt was matched.
        This returns False if there was a timeout.
        """
        i = self.expect([self.PROMPT, TIMEOUT], timeout=prompt_timeout)
        if i==1:
            return True
        return False
        
    def set_unique_prompt (self, optional_prompt=None):
        """This attempts to reset the shell prompt to something more unique.
            This makes it easier to match.
        """
        if optional_prompt is not None:
            self.prompt = optional_prompt
        self.sendline ("PS1='[PEXPECT]\$ '") # In case of sh-style
        i = self.expect ([TIMEOUT, self.PROMPT], timeout=10)
        if i == 0: # csh-style
            self.sendline ("set prompt='[PEXPECT]\$ '")
            i = self.expect ([TIMEOUT, self.PROMPT], timeout=10)
            if i == 0:
                return 0
        return 1

