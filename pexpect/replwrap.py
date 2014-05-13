"""Generic wrapper for read-eval-print-loops, a.k.a. interactive shells
"""
import pexpect

PEXPECT_PROMPT = u'[PEXPECT_PROMPT>'

class REPLWrapper(object):
    """Wrapper for a REPL.
    
    :param cmd_or_spawn: This can either be an instance of :class:`pexpect.spawn`
      in which a REPL has already been started, or a str command to start a new
      REPL process.
    :param str orig_prompt: The prompt to expect at first.
    :param str prompt_change: A command to change the prompt to something more
      unique. If this is ``None``, the prompt will not be changed.
    :param str new_prompt: The more unique prompt to expect after the change.
    """
    def __init__(self, cmd_or_spawn, orig_prompt, prompt_change,
                 new_prompt=PEXPECT_PROMPT):
        if isinstance(cmd_or_spawn, str):
            self.child = pexpect.spawnu(cmd_or_spawn)
        else:
            self.child = cmd_or_spawn
        self.child.setecho(False)  # Don't repeat our input.
        
        if prompt_change is None:
            self.prompt = orig_prompt
        else:
            self.set_prompt(orig_prompt, prompt_change, new_prompt)
            self.prompt = new_prompt

        self.expect_prompt()

    def set_prompt(self, orig_prompt, prompt_change, new_prompt=PEXPECT_PROMPT):
        self.child.expect_exact(orig_prompt)
        self.child.sendline(prompt_change)

    def expect_prompt(self, timeout=-1):
        self.child.expect_exact(self.prompt, timeout=timeout)
    
    def run_command(self, command, timeout=-1):
        """Send a command to the REPL, wait for and return output.
        
        :param str command: The command to send. Trailing newlines are not needed.
        :param int timeout: How long to wait for the next prompt. -1 means the
          default from the :class:`pexpect.spawn` object (default 30 seconds).
          None means to wait indefinitely.
        """
        # TODO: Multiline commands and continuation prompts
        self.child.sendline(command)
        self.expect_prompt(timeout=timeout)
        return self.child.before

def python(command="python"):
    """Start a Python shell and return a :class:`REPLWrapper` object."""
    return REPLWrapper(command, u">>> ", u"import sys; sys.ps1=%r" % PEXPECT_PROMPT)

def bash(command="bash", orig_prompt=u"$"):
    """Start a bash shell and return a :class:`REPLWrapper` object."""
    return REPLWrapper(command, orig_prompt, u"PS1=%r" % PEXPECT_PROMPT)