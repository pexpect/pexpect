"""
This class extends pexpect.spawn to specialize setting up SSH connections.
This adds methods for login, logout, and expecting the shell prompt.

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
"""


from pexpect import ExceptionPexpect, TIMEOUT, EOF, spawn


__all__ = ['ExceptionPxssh', 'pxssh']


class ExceptionPxssh(ExceptionPexpect):
    pass


class pxssh(spawn):

    """
        This class extends pexpect.spawn to specialize setting up SSH
        connections. This adds methods for login, logout, and expecting the shell
        prompt. It does various tricky things to handle many situations in the SSH
        login process. For example, if the session is your first login, then pxssh
        automatically accepts the remote certificate; or if you have public key
        authentication setup then pxssh won't wait for the password prompt.
        pxssh uses the shell prompt to synchronize output from the remote host. In
        order to make this more robust it sets the shell prompt to something more
        unique than just $ or #. This should work on most Borne/Bash or Csh style
        shells.
        Example that runs a few commands on a remote server and prints the result::
            from pexpect import pxssh
            import getpass
            try:
                s = pxssh.pxssh()
                hostname = raw_input('hostname: ')
                username = raw_input('username: ')
                password = getpass.getpass('password: ')
                s.login(hostname, username, password)
                s.sendline('uptime')   # run a command
                s.prompt()             # match the prompt
                print(s.before)        # print everything before the prompt.
                s.sendline('ls -l')
                s.prompt()
                print(s.before)
                s.sendline('df')
                s.prompt()
                print(s.before)
                s.logout()
            except pxssh.ExceptionPxssh as e:
                print("pxssh failed on login.")
                print(e)
        Example showing how to specify SSH options::
            from pexpect import pxssh
            s = pxssh.pxssh(options={
                                "StrictHostKeyChecking": "no",
                                "UserKnownHostsFile": "/dev/null"})
            ...
        Note that if you have ssh-agent running while doing development with pxssh
        then this can lead to a lot of confusion. Many X display managers (xdm,
        gdm, kdm, etc.) will automatically start a GUI agent. You may see a GUI
        dialog box popup asking for a password during development. You should turn
        off any key agents during testing. The 'force_password' attribute will turn
        off public key authentication. This will only work if the remote SSH server
        is configured to allow password logins. Example of using 'force_password'
        attribute::
                s = pxssh.pxssh()
                s.force_password = True
                hostname = raw_input('hostname: ')
                username = raw_input('username: ')
                password = getpass.getpass('password: ')
                s.login (hostname, username, password)
    """

    _PROMPT_ESCAPES =["$", "(", ")", "[", "]"]
    _REGEX_STRINGS = {
        "accept_key": "(?i)are you sure you want to continue connecting",
        "password_check": "(?i)(?:password)|(?:passphrase for key)",
        "denied": "(?i)permission denied",
        "terminal_type": "(?i)terminal type",
        "closed": "(?i)connection closed by remote host",
        "stopped": "(?i)there are stopped jobs"
    }
    _SSH_COMMAND = 'ssh {0} -l {1} {2}'
    _SSH_OPTIONS = {
        "quiet": " -q",
        "check_local_ip": " -o'NoHostAuthenticationForLocalhost=yes'",
        "port": " -p {0}",
        "ssh_key": " -i {0}"
    }
    PROMPT_SET_SH = "PS1='[PEXPECT]\$ '"
    PROMPT_SET_CSH = "set prompt='[PEXPECT]\$ '"
    UNIQUE_PROMPT = "\[PEXPECT\][\$\#] "

    def _build_ssh_command(self):
        """
            Method to build the ssh command string.
        :return:
        """
        options = ''.join([" -o '%s=%s'" % (o, v) for (o, v) in self.options.items()])

        for key, val in pxssh._SSH_OPTIONS.items():
            try:
                options += val.format(getattr(self, key))
            except AttributeError:
                options += val

        self.ssh_command = pxssh._SSH_COMMAND.format(options, self.username, self.server)

    def _first_phase_expect(self):
        """
            Method to return the expect from the first phase.
        :return: int:
        """
        return self.expect(
            [
                pxssh._REGEX_STRINGS["accept_key"], self.original_prompt, pxssh._REGEX_STRINGS["password_check"],
                pxssh._REGEX_STRINGS["denied"], pxssh._REGEX_STRINGS["terminal_type"], TIMEOUT
            ]
        )

    def _first_phase(self, result):
        """
            First phase Checks
        :param result:
        :return:
        """
        first_phase_success = {
            0: "yes",
            2: self.password,
            4: self.terminal_type
        }
        first_phase_errors = {
            7: 'Could not establish connection to host'
        }

        if result in first_phase_success:
            self.sendline(first_phase_success[result])
            return self._first_phase_expect()

        if result in first_phase_errors:
            self.close()
            raise ExceptionPxssh(first_phase_errors[result])

        else:
            return result

    def _initial_phase_expect(self):
        """
            Method to check the response.
        :return: int:
        """
        return self.expect(
            [
                pxssh._REGEX_STRINGS["accept_key"], self.original_prompt,
                pxssh._REGEX_STRINGS["password_check"], pxssh._REGEX_STRINGS["denied"],
                pxssh._REGEX_STRINGS["terminal_type"], TIMEOUT, pxssh._REGEX_STRINGS["closed"], EOF
            ], timeout=self.login_timeout
        )

    def _second_phase(self, result):

        second_phase_success = {
            1: "prompt",
            5: "timeout"
        }
        second_phase_errors = {
            0: 'Got "are you sure" prompt twice.',
            2: 'password refused',
            3: 'permission denied',
            4: 'Got "terminal type" prompt twice.',
            6: 'connection closed'
        }

        try:
            if result in second_phase_success:
                return True

            if result in second_phase_errors:
                self.close()
                raise ExceptionPxssh(second_phase_errors[result])
            else:
                self.close()
                raise ExceptionPxssh("Unknown ssh error.")

        except KeyError as err:
            self.close()
            raise ExceptionPxssh("Unknown ssh error: {0}".format(str(err)))

    def __init__(self, timeout=30, maxread=2000, searchwindowsize=None, logfile=None, cwd=None,
                 env=None, ignore_sighup=True, echo=True, options={}, encoding=None, codec_errors='strict'):

        super(pxssh, self).__init__(None, timeout=timeout, maxread=maxread, searchwindowsize=searchwindowsize,
                                    logfile=logfile, cwd=cwd, env=env, ignore_sighup=ignore_sighup, echo=echo,
                                    encoding=encoding, codec_errors=codec_errors)

        # Internal Variables
        self.auto_prompt_reset = True
        self.command = None
        self.force_password = False
        self.PROMPT = self.UNIQUE_PROMPT
        self.login_timeout = 10
        self.options = options
        self.original_prompt = r"[#$]"
        self.password = None
        self.server = None
        self.ssh_opts = ("-o'RSAAuthentication=no'" + " -o 'PubkeyAuthentication=no'")
        self.terminal_type = "ansi"
        self.username = None

    def login(self,  server, username, password='', terminal_type='ansi', original_prompt=r"[#$]", login_timeout=10,
              port=22, auto_prompt_reset=True, ssh_key=None, quiet=True, sync_multiplier=1, check_local_ip=True):

        for name in list(locals().keys()):
            if name != "self":
                setattr(self, name, locals()[name])

        self._build_ssh_command()

        self._spawn(self.ssh_command)
        initial_phase = self._initial_phase_expect()
        first_phase = self._first_phase(initial_phase)
        self._second_phase(first_phase)

        if self.auto_prompt_reset:
            if not self.set_unique_prompt():
                self.close()
                raise ExceptionPxssh('could not set shell prompt '
                                     '(received: %r, expected: %r).' % (
                                         self.before, self.PROMPT,))

    def logout(self):

        self.sendline("exit")
        index = self.expect([EOF, "(?i)there are stopped jobs"])

        if index==1:
            self.sendline("exit")
            self.expect(EOF)

        self.close()

    def read_prompt(self):

        buffer = ''
        char_buffer = ''

        while True:
            try:
                char_buffer = self.read_nonblocking(size=1, timeout=0.5)
                buffer += char_buffer
                char_buffer = ""

            except TIMEOUT:
                break

        return buffer

    def set_unique_prompt(self):

        self.sendline("unset PROMPT_COMMAND")
        self.sendline(self.PROMPT_SET_SH)  # sh-style
        i = self.expect([TIMEOUT, self.PROMPT], timeout=10)
        if i == 0:  # csh-style
            self.sendline(self.PROMPT_SET_CSH)
            i = self.expect([TIMEOUT, self.PROMPT], timeout=10)
            if i == 0:
                return False
        return True

    def sync_original_prompt(self):

        self.sendline('')
        x = self.read_prompt()

        self.sendline('')
        y = self.read_prompt()

        if x == y:
            self.PROMPT = x.replace("\r\n", "")
            for escape in pxssh._PROMPT_ESCAPES:
                self.PROMPT = self.PROMPT.replace(escape, "\{0}".format(escape))

    def prompt(self, timeout=-1):

        """
            Match the next shell prompt.
            This is little more than a short-cut to the :meth:`~pexpect.spawn.expect`
            method. Note that if you called :meth:`login` with
            ``auto_prompt_reset=False``, then before calling :meth:`prompt` you must
            set the :attr:`PROMPT` attribute to a regex that it will use for
            matching the prompt.
            Calling :meth:`prompt` will erase the contents of the :attr:`before`
            attribute even if no prompt is ever matched. If timeout is not given or
            it is set to -1 then self.timeout is used.
            :return: True if the shell prompt was matched, False if the timeout was
                 reached.
        """

        if timeout == -1:
            timeout = self.timeout

        i = self.expect([self.PROMPT, TIMEOUT], timeout=timeout)
        if i==1:
            return False
        return True
