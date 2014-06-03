import re
import os
import sys
import unittest

import pexpect
from pexpect import replwrap

class REPLWrapTestCase(unittest.TestCase):
    def test_python(self):
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
        self.assertEqual(res.strip().splitlines()[:2], ['1 2', '3 4'])

    def test_existing_spawn(self):
        child = pexpect.spawnu("bash", echo=False, timeout=5)
        repl = replwrap.REPLWrapper(child, re.compile('[$#]'),
                                    "PS1='{0}' PS2='{1}' PROMPT_COMMAND=''")

        res = repl.run_command("echo $HOME")
        assert res.startswith('/'), res

if __name__ == '__main__':
    unittest.main()
