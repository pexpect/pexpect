'''This class extends pexpect.spawn to specialize setting up SSH connections.
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

'''

from pexpect import ExceptionPexpect, TIMEOUT, EOF, spawn
from pprint import pprint
import copy


__all__ = ['ExceptionPxssh', 'pxssh']


class ExceptionPxssh(ExceptionPexpect):
    pass


class pxssh(spawn):

    """
        Class to handle basic commincation and setup of the ssh session.
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

    def _build_ssh_command(self):
        """
            Method to build the ssh command string.
        :return:
        """
        options = ''.join([" -o '%s=%s'" % (o, v) for (o, v) in self.options.items()])

        for key, val in pxssh._SSH_OPTIONS.iteritems():
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
        """
            Second Phase Checks.
        :param result: type: int
        :return:
        """
        second_phase_success = {
            1: "prompt",
            5: "timeout"
        }
        second_phase_errors = {
            0: 'Got "are you sure" prompt twice.',
            2: 'password refused',
            3: 'permission denied',
            4: 'Weird error. Got "terminal type" prompt twice.',
            6: 'connection closed'
        }

        try:
            if result in second_phase_success:
                return True

            if result in second_phase_errors:
                self.close()
                raise ExceptionPxssh(second_phase_errors[result[0]])
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
        self.PROMPT = None
        self.login_timeout = 10
        self.options = {}
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
            self.set_unique_prompt()

    def logout(self):
        """
            Sends exit to the remote shell.

            If there are stopped jobs then this automatically sends exit twice.
        :return:
        """
        self.sendline("exit")
        index = self.expect([EOF, "(?i)there are stopped jobs"])
        if index==1:
            self.sendline("exit")
            self.expect(EOF)
        self.close()

    def read_prompt(self):
        """
            Read the character buffer coming in on the ssh channel, till a timeout occurs, this should be the end of the
            prompt.
            # Todo: Need to check that this will get the correct prompt even on a slow device. prehaps a sliding window ?
        :return:
        """
        buffer = ''
        char_buffer = ''

        while True:
            try:
                char_buffer = ssh.read_nonblocking(size=1, timeout=0.5)
                buffer += char_buffer
                char_buffer = ""
            except TIMEOUT as err:
                break
        return buffer

    def set_unique_prompt(self):
        """
            Method to auto set the prompt.
        :return:
        """
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
            Match the original prompt
        :param timeout:
        :return:
        """
        if timeout == -1:
            timeout = self.timeout

        i = self.expect([self.PROMPT, TIMEOUT], timeout=timeout)
        if i==1:
            return False
        return True


if __name__ == '__main__':
    ssh = pxssh()

    ssh.login("ssh unnethack@eu.un.nethack.nu", "john", "05May1981")

    ssh.sendline("curl -kvvL http://www.bbc.co.uk")
    ssh.prompt()
    print ssh.before

    raw_input("")

