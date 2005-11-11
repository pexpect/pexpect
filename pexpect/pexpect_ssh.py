"""This contains functions that perform common tasks with Pexpect, such
as setting up SSH logins, logout, or running commands that ask for a password.

"""
from pexpect import *
import os, sys, getopt, shutil
from time import sleep

PROMPT = "\[PEXPECT\]\$ "

# Set command prompt to something more unique.
# SUBTLE HACK ALERT!
# Note that the command to set the prompt uses a slightly different string
# than the regular expression to match it. This is because when you set the
# prompt the command will echo back, but we don't want to match the echoed
# command. So if we make the set command slightly different than the regex
# we eliminate the problem. To make the set command different we add a
# backslash in front of $. The $ doesn't need to be escaped, but it doesn't
# hurt and serves to make the set command different than the regex.

class ssh (spawn):
    """This extends the spawn class to specialize for running 'ssh' command-line client.
        This adds methods to login, logout, and expect_prompt.
    """
    def __init__(self):
        self.PROMPT = "\[PEXPECT\]\$ "
        pass
    def logout(self):
        """This sends exit. If there are stopped jobs then this sends exit twice.
        """
        self.sendline("exit")
        index = self.expect([EOF, "(?i)there are stopped jobs"])
        if index==1:
            self.sendline("exit")
            self.expect(EOF)
    def login(self,server,username,password,terminal_type='ansi'):
        original_prompts = r"][#$]|~[#$]|bash.*?[#$]"
        cmd = "ssh -l %s %s" % (username, server)
        self = spawn(cmd, timeout=300)
        #, "(?i)no route to host"])
        i = self.expect(["(?i)are you sure you want to continue connecting", original_prompts, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])
        if i==0: # New certificate -- always accept it.
                  # This is the prompt we get if SSH does not have 
                  # the remote host's public key stored in the cache.
            self.sendline("yes")
            i = self.expect(["(?i)are you sure you want to continue connecting", original_prompts, "(?i)password", "(?i)permission denied", "(?i)terminal type", TIMEOUT])
        if i==2: password
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
            ### May NOT be OK if expect false matched a prompt.
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
        # We appear to have logged in.
        # Now look for the command-line prompt
        # Reset it to something more unique when we find it.
        if not self.set_unique_prompt():
            self.close()
            return False
        return True

    def expect_prompt (self):
        """This expects the prompt.
        """
        i = self.expect(self.PROMPT)
        
    def set_unique_prompt (self, optional_prompt=None):
        """This attempts to reset the shell prompt to something more unique.
            This makes it easier to match in the future.
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

