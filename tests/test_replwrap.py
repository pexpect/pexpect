import platform
import unittest

import pexpect
from pexpect import replwrap

class REPLWrapTestCase(unittest.TestCase):
    def test_bash(self):
        bash = replwrap.bash()
        res = bash.run_command("time")
        assert 'real' in res, res

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
        child = pexpect.spawnu("bash")
        repl = replwrap.REPLWrapper(child, replwrap.u("$ "),
                            "PS1='{0}'; PS2='{1}'")

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

        child = pexpect.spawnu('python')
        # prompt_change=None should mean no prompt change
        py = replwrap.REPLWrapper(child, replwrap.u(">>> "), prompt_change=None,
                                  continuation_prompt=replwrap.u("... "))
        assert py.prompt == ">>> "

        res = py.run_command("for a in range(3): print(a)\n")
        assert res.strip().splitlines() == ['0', '1', '2']


if __name__ == '__main__':
    unittest.main()
