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

    def test_connection_refused(self):
        ssh = pxssh.pxssh()
        try:
            ssh.login('noserver', 'me', password='s3cret')
        except pxssh.ExceptionPxssh:
            pass
        else:
            assert False, 'should have raised exception, pxssh.ExceptionPxssh'
    
    def test_ssh_tunnel_string(self):
        ssh = pxssh.pxssh(debug_tunnel_command=True)
        tunnels = { 'local': ['2424:localhost:22'],'remote': ['2525:localhost:22'],
            'dynamic': [8888] }
        confirmation_strings = 0
        confirmation_array = ['-R 2525:localhost:22','-L 2424:localhost:22','-D 8888']
        string = ssh.login('server', 'me', password='s3cret', ssh_tunnels=tunnels)
        for confirmation in confirmation_array:
            if confirmation in string:
                confirmation_strings+=1
        
        if confirmation_strings!=3:
            assert False, 'String generated from tunneling is potientally incorrect.'


if __name__ == '__main__':
    unittest.main()
