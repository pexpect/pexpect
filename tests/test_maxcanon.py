""" Module for canonical-mode tests. """
# std imports
import sys
import os

# local
import pexpect
from . import PexpectTestCase

# 3rd-party
import pytest


class TestCaseCanon(PexpectTestCase.PexpectTestCase):
    """
    Test expected Canonical mode behavior (limited input line length).

    All systems use the value of MAX_CANON which can be found using
    fpathconf(3) value PC_MAX_CANON -- with the exception of Linux
    and FreeBSD.

    Linux, though defining a value of 255, actually honors the value
    of 4096 from linux kernel include file tty.h definition
    N_TTY_BUF_SIZE.

    Linux also does not honor IMAXBEL. termios(3) states, "Linux does not
    implement this bit, and acts as if it is always set." Although these
    tests ensure it is enabled, this is a non-op for Linux.

    FreeBSD supports neither, and instead uses a fraction (1/5) of the tty
    speed which is always 9600.  Therefor, the maximum limited input line
    length is 9600 / 5 = 1920.

    These tests only ensure the correctness of the behavior described by
    the sendline() docstring. pexpect is not particularly involved in
    these scenarios, though if we wish to expose some kind of interface
    to tty.setraw, for example, these tests may be re-purposed as such.

    Lastly, portions of these tests are skipped on Travis-CI. It produces
    unexpected behavior not reproduced on Debian/GNU Linux.
    """

    def setUp(self):
        super(TestCaseCanon, self).setUp()

        self.echo = False
        if sys.platform.lower().startswith('linux'):
            # linux is 4096, N_TTY_BUF_SIZE.
            self.max_input = 4096
            self.echo = True
        elif sys.platform.lower().startswith('sunos'):
            # SunOS allows PC_MAX_CANON + 1; see
            # https://bitbucket.org/illumos/illumos-gate/src/d07a59219ab7fd2a7f39eb47c46cf083c88e932f/usr/src/uts/common/io/ldterm.c?at=default#cl-1888
            self.max_input = os.fpathconf(0, 'PC_MAX_CANON') + 1
        elif sys.platform.lower().startswith('freebsd'):
            # http://lists.freebsd.org/pipermail/freebsd-stable/2009-October/052318.html
            self.max_input = 9600 / 5
        else:
            # All others (probably) limit exactly at PC_MAX_CANON
            self.max_input = os.fpathconf(0, 'PC_MAX_CANON')

    @pytest.mark.skipif(
        sys.platform.lower().startswith('freebsd'),
        reason='os.write to BLOCK indefinitely on FreeBSD in this case'
    )
    def test_under_max_canon(self):
        " BEL is not sent by terminal driver at maximum bytes - 1. "
        # given,
        child = pexpect.spawn('bash', echo=self.echo, timeout=5)
        child.sendline('echo READY')
        child.sendline('stty icanon imaxbel')
        child.sendline('echo BEGIN; cat')

        # some systems BEL on (maximum - 1), not able to receive CR,
        # even though all characters up until then were received, they
        # simply cannot be transmitted, as CR is part of the transmission.
        send_bytes = self.max_input - 1

        # exercise,
        child.sendline('_' * send_bytes)

        # fast forward beyond 'cat' command, as ^G can be found as part of
        # set-xterm-title sequence of $PROMPT_COMMAND or $PS1.
        child.expect_exact('BEGIN')

        # verify, all input is found in echo output,
        child.expect_exact('_' * send_bytes)

        # BEL is not found,
        with self.assertRaises(pexpect.TIMEOUT):
            child.expect_exact('\a', timeout=1)

        # cleanup,
        child.sendeof()           # exit cat(1)
        child.sendline('exit 0')  # exit bash(1)
        child.expect(pexpect.EOF)
        assert not child.isalive()
        assert child.exitstatus == 0

    @pytest.mark.skipif(
        sys.platform.lower().startswith('freebsd'),
        reason='os.write to BLOCK indefinitely on FreeBSD in this case'
    )
    def test_beyond_max_icanon(self):
        " a single BEL is sent when maximum bytes is reached. "
        # given,
        child = pexpect.spawn('bash', echo=self.echo, timeout=5)
        child.sendline('stty icanon imaxbel erase ^H')
        child.sendline('cat')
        send_bytes = self.max_input

        # exercise,
        child.sendline('_' * send_bytes)
        child.expect_exact('\a')

        # exercise, we must now backspace to send CR.
        child.sendcontrol('h')
        child.sendline()

        if os.environ.get('TRAVIS', None) == 'true':
            # Travis-CI has intermittent behavior here, possibly
            # because the master process is itself, a PTY?
            return

        # verify the length of (maximum - 1) received by cat(1),
        # which has written it back out,
        child.expect_exact('_' * (send_bytes - 1))
        # and not a byte more.
        with self.assertRaises(pexpect.TIMEOUT):
            child.expect_exact('_', timeout=1)

        # cleanup,
        child.sendeof()           # exit cat(1)
        child.sendline('exit 0')  # exit bash(1)
        child.expect_exact(pexpect.EOF)
        assert not child.isalive()
        assert child.exitstatus == 0

    @pytest.mark.skipif(
        sys.platform.lower().startswith('freebsd'),
        reason='os.write to BLOCK indefinitely on FreeBSD in this case'
    )
    def test_max_no_icanon(self):
        " may exceed maximum input bytes if canonical mode is disabled. "
        # given,
        child = pexpect.spawn('bash', echo=self.echo, timeout=5)
        child.sendline('stty -icanon imaxbel')
        child.sendline('echo BEGIN; cat')
        send_bytes = self.max_input + 11

        # exercise,
        child.sendline('_' * send_bytes)

        # fast forward beyond 'cat' command, as ^G can be found as part of
        # set-xterm-title sequence of $PROMPT_COMMAND or $PS1.
        child.expect_exact('BEGIN')

        if os.environ.get('TRAVIS', None) == 'true':
            # Travis-CI has intermittent behavior here, possibly
            # because the master process is itself, a PTY?
            return

        # BEL is *not* found,
        with self.assertRaises(pexpect.TIMEOUT):
            child.expect_exact('\a', timeout=1)

        # verify, all input is found in output,
        child.expect_exact('_' * send_bytes)

        # cleanup,
        child.sendcontrol('c')    # exit cat(1) (eof wont work in -icanon)
        child.sendcontrol('c')
        child.sendline('exit 0')  # exit bash(1)
        child.expect(pexpect.EOF)
        assert not child.isalive()
        assert child.exitstatus == 0
