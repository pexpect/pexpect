# -*- coding: utf-8 -*-

import importlib
import sys
from unittest import mock

from . import PexpectTestCase
import pexpect


class TestCaseDelay(PexpectTestCase.PexpectTestCase):
    """
    Tests for various delay attributes.
    """
    def test_delaybeforesend(self):
        """
        Test various values for delaybeforesend.
        """
        p = pexpect.spawn("cat")

        p.delaybeforesend = 1
        p.sendline("line 1")
        p.expect("line 1")

        p.delaybeforesend = 0.0
        p.sendline("line 2")
        p.expect("line 2")

        p.delaybeforesend = None
        p.sendline("line 3")
        p.expect("line 3")

    def test_delayafterread(self):
        """
        Test various values for delayafterread.
        """
        p = pexpect.spawn("cat")

        p.delayafterread = 1
        p.sendline("line 1")
        p.expect("line 1")

        p.delayafterread = 0.0
        p.sendline("line 2")
        p.expect("line 2")

        p.delayafterread = None
        p.sendline("line 3")
        p.expect("line 3")

    def test_close_propagates_delays(self):
        """
        Test that spawn.close() propagates delayafterclose and delayafterterminate to ptyproc.
        """
        fake_ptyproc = mock.Mock()
        fake_ptyproc.delayafterclose = 0.1
        fake_ptyproc.delayafterterminate = 0.1
        fake_ptyproc.isalive.return_value = False
        fake_ptyproc.status = 0
        fake_ptyproc.exitstatus = 0
        fake_ptyproc.signalstatus = None

        if hasattr(pexpect, "spawn"):
            child = pexpect.spawn(None)
        else:
            fake_ptyprocess = mock.MagicMock()
            fake_ptyprocess.PtyProcessError = Exception
            stubs = {
                "termios": mock.MagicMock(),
                "tty": mock.MagicMock(),
                "pty": mock.MagicMock(),
                "ptyprocess": fake_ptyprocess,
                "ptyprocess.ptyprocess": fake_ptyprocess,
            }
            with mock.patch.dict(sys.modules, stubs):
                try:
                    pty_spawn = importlib.import_module("pexpect.pty_spawn")
                    child = pty_spawn.spawn(None)
                finally:
                    sys.modules.pop("pexpect.pty_spawn", None)

        child.ptyproc = fake_ptyproc
        child.delayafterclose = 2.5
        child.delayafterterminate = 3.5
        child.close()

        self.assertEqual(fake_ptyproc.delayafterclose, 2.5)
        self.assertEqual(fake_ptyproc.delayafterterminate, 3.5)
        fake_ptyproc.close.assert_called_once_with(force=True)
