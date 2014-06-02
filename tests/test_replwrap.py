import re
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
        # on some machines, becomes, use only first two items
        # [u'1 2', u'3 4', u'\x1b]0;00-0c-29-e7-65-bd \x07']
        self.assertEqual(res.strip().splitlines()[:2], ['1 2', '3 4'])

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
        child = pexpect.spawnu("bash --norc", echo=False, timeout=5)
        repl = replwrap.REPLWrapper(child, re.compile('[$#]'),
                            "PS1='{0}' PS2='{1}'; export PS1 PS2")

        res = repl.run_command("echo $HOME")
        assert res.startswith('/'), res

if __name__ == '__main__':
    unittest.main()
