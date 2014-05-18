import sys
import unittest

import pexpect
from pexpect import replwrap

class REPLWrapTestCase(unittest.TestCase):
    def test_python(self):
        py = replwrap.python(sys.executable)
        res = py.run_command("5+6")
        self.assertEqual(res.strip(), "11")

    def test_multiline(self):
        py = replwrap.python(sys.executable)
        res = py.run_command("for a in range(3):\n  print(a)\n")
        self.assertEqual(res.strip().splitlines(), ['0', '1', '2'])

        # Should raise ValueError if input is incomplete
        try:
            py.run_command("for a in range(3):")
        except ValueError:
            pass
        else:
            assert False, "Didn't raise ValueError for incorrect input"

        # Check that the REPL was reset (SIGINT) after the incomplete input
        res = py.run_command("for a in range(3):\n  print(a)\n")
        self.assertEqual(res.strip().splitlines(), ['0', '1', '2'])

    def test_existing_spawn(self):
        child = pexpect.spawnu("python")
        repl = replwrap.REPLWrapper(child, replwrap.u(">>> "),
                            "import sys; sys.ps1=%r" % replwrap.PEXPECT_PROMPT)

        res = repl.run_command("print(7*6)")
        self.assertEqual(res.strip(), "42")

if __name__ == '__main__':
    unittest.main()