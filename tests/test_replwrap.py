import platform
import unittest
import re
import os

import pexpect
from pexpect import replwrap


class REPLWrapTestCase(unittest.TestCase):
    def setUp(self):
        super(REPLWrapTestCase, self).setUp()
        self.save_ps1 = os.getenv('PS1', r'\$')
        self.save_ps2 = os.getenv('PS2', '>')
        os.putenv('PS1', r'\$')
        os.putenv('PS2', '>')

    def tearDown(self):
        super(REPLWrapTestCase, self).tearDown()
        os.putenv('PS1', self.save_ps1)
        os.putenv('PS2', self.save_ps2)

    def test_bash(self):
        bash = replwrap.bash()
        res = bash.run_command("time")
        assert 'real' in res, res

        # PAGER should be set to cat, otherwise man hangs
        res = bash.run_command('man sleep', timeout=2)
        assert 'SLEEP' in res, res

    def test_multiline(self):
        bash = replwrap.bash()
        res = bash.run_command("echo '1 2\n3 4'")
        self.assertEqual(res.strip().splitlines(), ['1 2', '3 4'])

        # Should raise ValueError if input is incomplete
        try:
            bash.run_command("echo '5 6")
        except ValueError:
            pass
        else:
            assert False, "Didn't raise ValueError for incomplete input"

        # Check that the REPL was reset (SIGINT) after the incomplete input
        res = bash.run_command("echo '1 2\n3 4'")
        self.assertEqual(res.strip().splitlines(), ['1 2', '3 4'])

    def test_existing_spawn(self):
        child = pexpect.spawnu("bash", timeout=5, echo=False)
        repl = replwrap.REPLWrapper(child, re.compile('[$#]'),
                                    "PS1='{0}' PS2='{1}' "
                                    "PROMPT_COMMAND=''")

        res = repl.run_command("echo $HOME")
        assert res.startswith('/'), res

    def test_python(self):
        if platform.python_implementation() == 'PyPy':
            raise unittest.SkipTest("This test fails on PyPy because of REPL differences")

        p = replwrap.python()
        res = p.run_command('4+7')
        assert res.strip() == '11'

        res = p.run_command('for a in range(3): print(a)\n')
        assert res.strip().splitlines() == ['0', '1', '2']

    def test_no_change_prompt(self):
        if platform.python_implementation() == 'PyPy':
            raise unittest.SkipTest("This test fails on PyPy because of REPL differences")

        child = pexpect.spawnu('python', echo=False, timeout=5)
        # prompt_change=None should mean no prompt change
        py = replwrap.REPLWrapper(child, replwrap.u(">>> "), prompt_change=None,
                                  continuation_prompt=replwrap.u("... "))
        assert py.prompt == ">>> "

        res = py.run_command("for a in range(3): print(a)\n")
        assert res.strip().splitlines() == ['0', '1', '2']


if __name__ == '__main__':
    unittest.main()
