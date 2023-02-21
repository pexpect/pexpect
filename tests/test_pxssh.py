#!/usr/bin/env python
import sys
import os
import shutil
import tempfile
import unittest

if sys.platform != 'win32':
    from pexpect import pxssh
from .PexpectTestCase import PexpectTestCase

class SSHTestBase(PexpectTestCase):
    def setUp(self):
        super(SSHTestBase, self).setUp()
        self.tempdir = tempfile.mkdtemp()
        self.orig_path = os.environ.get('PATH')
        os.symlink(self.PYTHONBIN, os.path.join(self.tempdir, 'python'))
        fakessh_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fakessh'))
        os.environ['PATH'] = self.tempdir + os.pathsep + fakessh_dir + \
                    ((os.pathsep + self.orig_path) if self.orig_path else '')

    def tearDown(self):
        shutil.rmtree(self.tempdir)
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
        ssh = pxssh.pxssh(debug_command_string=True)
        tunnels = { 'local': ['2424:localhost:22'],'remote': ['2525:localhost:22'],
            'dynamic': [8888] }
        confirmation_strings = 0
        confirmation_array = ['-R 2525:localhost:22','-L 2424:localhost:22','-D 8888']
        string = ssh.login('server', 'me', password='s3cret', ssh_tunnels=tunnels)
        for confirmation in confirmation_array:
            if confirmation in string:
                confirmation_strings+=1

        if confirmation_strings!=len(confirmation_array):
            assert False, 'String generated from tunneling is incorrect.'

    def test_remote_ssh_tunnel_string(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        tunnels = { 'local': ['2424:localhost:22'],'remote': ['2525:localhost:22'],
            'dynamic': [8888] }
        confirmation_strings = 0
        confirmation_array = ['-R 2525:localhost:22','-L 2424:localhost:22','-D 8888']
        string = ssh.login('server', 'me', password='s3cret', ssh_tunnels=tunnels, spawn_local_ssh=False)
        for confirmation in confirmation_array:
            if confirmation in string:
                confirmation_strings+=1

        if confirmation_strings!=len(confirmation_array):
            assert False, 'String generated from remote tunneling is incorrect.'

    def test_ssh_config_passing_string(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        temp_file = tempfile.NamedTemporaryFile()
        config_path = temp_file.name
        string = ssh.login('server', 'me', password='s3cret', spawn_local_ssh=False, ssh_config=config_path)
        if not '-F '+config_path in string:
            assert False, 'String generated from SSH config passing is incorrect.'

    def test_username_or_ssh_config(self):
        try:
            ssh = pxssh.pxssh(debug_command_string=True)
            temp_file = tempfile.NamedTemporaryFile()
            config_path = temp_file.name
            string = ssh.login('server')
            raise AssertionError('Should have failed due to missing username and missing ssh_config.')
        except TypeError:
            pass

    def test_ssh_config_user(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        temp_file = tempfile.NamedTemporaryFile()
        config_path = temp_file.name
        temp_file.write(b'HosT server\n'
                        b'UsEr me\n'
                        b'hOSt not-server\n')
        temp_file.seek(0)
        string = ssh.login('server', ssh_config=config_path)

    def test_ssh_config_no_username_empty_config(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        temp_file = tempfile.NamedTemporaryFile()
        config_path = temp_file.name
        try:
            string = ssh.login('server', ssh_config=config_path)
            raise AssertionError('Should have failed due to no Host.')
        except TypeError:
            pass

    def test_ssh_config_wrong_Host(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        temp_file = tempfile.NamedTemporaryFile()
        config_path = temp_file.name
        temp_file.write(b'Host not-server\n'
                        b'Host also-not-server\n')
        temp_file.seek(0)
        try:
            string = ssh.login('server', ssh_config=config_path)
            raise AssertionError('Should have failed due to no matching Host.')
        except TypeError:
            pass

    def test_ssh_config_no_user(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        temp_file = tempfile.NamedTemporaryFile()
        config_path = temp_file.name
        temp_file.write(b'Host server\n'
                        b'Host not-server\n')
        temp_file.seek(0)
        try:
            string = ssh.login('server', ssh_config=config_path)
            raise AssertionError('Should have failed due to no user.')
        except TypeError:
            pass

    def test_ssh_config_empty_user(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        temp_file = tempfile.NamedTemporaryFile()
        config_path = temp_file.name
        temp_file.write(b'Host server\n'
                        b'user   \n'
                        b'Host not-server\n')
        temp_file.seek(0)
        try:
            string = ssh.login('server', ssh_config=config_path)
            raise AssertionError('Should have failed due to empty user.')
        except TypeError:
            pass

    def test_ssh_key_string(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        confirmation_strings = 0
        confirmation_array = [' -A']
        string = ssh.login('server', 'me', password='s3cret', ssh_key=True)
        for confirmation in confirmation_array:
            if confirmation in string:
                confirmation_strings+=1

        if confirmation_strings!=len(confirmation_array):
            assert False, 'String generated from forcing the SSH agent sock is incorrect.'

        confirmation_strings = 0
        temp_file = tempfile.NamedTemporaryFile()
        ssh_key = temp_file.name
        confirmation_array = [' -i '+ssh_key]
        string = ssh.login('server', 'me', password='s3cret', ssh_key=ssh_key)
        for confirmation in confirmation_array:
            if confirmation in string:
                confirmation_strings+=1
        
        if confirmation_strings!=len(confirmation_array):
            assert False, 'String generated from adding an SSH key is incorrect.'

    def test_custom_ssh_cmd_debug(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        cipher_string = '-c aes128-ctr,aes192-ctr,aes256-ctr,arcfour256,arcfour128,' \
            + 'aes128-cbc,3des-cbc,blowfish-cbc,cast128-cbc,aes192-cbc,' \
            + 'aes256-cbc,arcfour'
        confirmation_strings = 0
        confirmation_array = [cipher_string, '-2']
        string = ssh.login('server', 'me', password='s3cret', cmd='ssh ' + cipher_string + ' -2')
        for confirmation in confirmation_array:
            if confirmation in string:
                confirmation_strings+=1

        if confirmation_strings!=len(confirmation_array):
            assert False, 'String generated for custom ssh client command is incorrect.'

    def test_custom_ssh_cmd_debug(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        cipher_string = '-c aes128-ctr,aes192-ctr,aes256-ctr,arcfour256,arcfour128,' \
            + 'aes128-cbc,3des-cbc,blowfish-cbc,cast128-cbc,aes192-cbc,' \
            + 'aes256-cbc,arcfour'
        confirmation_strings = 0
        confirmation_array = [cipher_string, '-2']
        string = ssh.login('server', 'me', password='s3cret', cmd='ssh ' + cipher_string + ' -2')
        for confirmation in confirmation_array:
            if confirmation in string:
                confirmation_strings+=1

        if confirmation_strings!=len(confirmation_array):
            assert False, 'String generated for custom ssh client command is incorrect.'

    def test_failed_custom_ssh_cmd_debug(self):
        ssh = pxssh.pxssh(debug_command_string=True)
        cipher_string = '-c invalid_cipher'
        confirmation_strings = 0
        confirmation_array = [cipher_string, '-2']
        string = ssh.login('server', 'me', password='s3cret', cmd='ssh ' + cipher_string + ' -2')
        for confirmation in confirmation_array:
            if confirmation in string:
                confirmation_strings+=1

        if confirmation_strings!=len(confirmation_array):
            assert False, 'String generated for custom ssh client command is incorrect.'

    def test_custom_ssh_cmd(self):
        try:
            ssh = pxssh.pxssh()
            cipher_string = '-c aes128-ctr,aes192-ctr,aes256-ctr,arcfour256,arcfour128,' \
                + 'aes128-cbc,3des-cbc,blowfish-cbc,cast128-cbc,aes192-cbc,' \
                + 'aes256-cbc,arcfour'
            result = ssh.login('server', 'me', password='s3cret', cmd='ssh ' + cipher_string + ' -2')

            ssh.PROMPT = r'Closed connection'
            ssh.sendline('exit')
            ssh.prompt(timeout=5)
            string = str(ssh.before) + str(ssh.after)
    
            if 'Closed connection' not in string:
                assert False, 'should have logged into Mock SSH client and exited'
        except pxssh.ExceptionPxssh as e:
            assert False, 'should not have raised exception, pxssh.ExceptionPxssh'
        else:
            pass

    def test_failed_custom_ssh_cmd(self):
        try:
            ssh = pxssh.pxssh()
            cipher_string = '-c invalid_cipher'
            result = ssh.login('server', 'me', password='s3cret', cmd='ssh ' + cipher_string + ' -2')

            ssh.PROMPT = r'Closed connection'
            ssh.sendline('exit')
            ssh.prompt(timeout=5)
            string = str(ssh.before) + str(ssh.after)
    
            if 'Closed connection' not in string:
                assert False, 'should not have completed logging into Mock SSH client and exited'
        except pxssh.ExceptionPxssh as e:
            pass
        else:
            assert False, 'should have raised exception, pxssh.ExceptionPxssh'

if __name__ == '__main__':
    unittest.main()
