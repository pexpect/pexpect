import sys
import unittest

import pexpect
from pexpect import replwrap

class REPLWrapTestCase(unittest.TestCase):
    def test_python(self):
        py = replwrap.python(sys.executable)
        res = py.run_command("5+6")
        self.assertEqual(res.strip(), "11")
    
    def test_existing_spawn(self):
        child = pexpect.spawnu("python")
        repl = replwrap.REPLWrapper(child, u">>> ",
                            "import sys; sys.ps1=%r" % replwrap.PEXPECT_PROMPT)
        
        res = repl.run_command("print(7*6)")
        self.assertEqual(res.strip(), "42")

if __name__ == '__main__':
    unittest.main()