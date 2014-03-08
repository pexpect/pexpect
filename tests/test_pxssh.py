#!/usr/bin/env python
import os

import unittest

from pexpect import pxssh

class SSHTestBase(unittest.TestCase):
    def setUp(self):
        self.orig_path = os.environ.get('PATH')
        fakessh_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fakessh'))
        os.environ['PATH'] = fakessh_dir + \
                    ((os.pathsep + self.orig_path) if self.orig_path else '')

    def tearDown(self):
        if self.orig_path:
            os.environ['PATH'] = self.orig_path
        else:
            del os.environ['PATH']

class PxsshTestCase(SSHTestBase):
    def test_fake_ssh(self):
        ssh = pxssh.pxssh()
        #ssh.logfile_read = sys.stdout  # DEBUG
        ssh.login('server', 'me', password='s3cret')
        ssh.sendline('ping')
        ssh.expect('pong', timeout=10)
        assert ssh.prompt(timeout=10)
        ssh.logout()

    def test_wrong_pw(self):
        ssh = pxssh.pxssh()
        try:
            ssh.login('server', 'me', password='wr0ng')
        except pxssh.ExceptionPxssh:
            pass
        else:
            assert False, 'Password should have been refused'

    def test_failed_set_unique_prompt(self):
        ssh = pxssh.pxssh()
        ssh.set_unique_prompt = lambda: False
        try:
            ssh.login('server', 'me', password='s3cret',
                      auto_prompt_reset=True)
        except pxssh.ExceptionPxssh:
            pass
        else:
            assert False, 'should have raised exception, pxssh.ExceptionPxssh'


if __name__ == '__main__':
    unittest.main()
