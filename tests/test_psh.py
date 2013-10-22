#!/usr/bin/env python
import unittest

from pexpect import pxssh, psh
from test_pxssh import SSHTestBase

class PshTestBase(SSHTestBase):
    def test_psh(self):
        ssh = pxssh.pxssh()
        ssh.login('server', 'user', 's3cret')
        sh = psh.psh(ssh)
        res = set(sh.ls())
        self.assertEqual(res, set([b'file1.py', b'file2.html']))

if __name__ == '__main__':
    unittest.main()