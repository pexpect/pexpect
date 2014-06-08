import tempfile
import os

import pexpect
from . import PexpectTestCase


class TestCaseWhich(PexpectTestCase.PexpectTestCase):
    " Tests for pexpect.which(). "

    def test_which_finds_ls(self):
        " which() can find ls(1). "
        exercise = pexpect.which("ls")
        assert exercise is not None
        assert exercise.startswith('/')

    def test_os_defpath_which(self):
        " which() finds an executable in $PATH and returns its abspath. "
        fname = 'cc'
        bin_dir = tempfile.mkdtemp()
        bin_path = os.path.join(bin_dir, fname)
        save_path = os.environ['PATH']
        save_defpath = os.defpath

        try:
            # setup
            os.environ['PATH'] = ''
            os.defpath = bin_dir
            with open(bin_path, 'w') as fp:
                pass

            # given non-executable,
            os.chmod(bin_path, 0o400)

            # exercise absolute and relative,
            assert pexpect.which(bin_path) is None
            assert pexpect.which(fname) is None

            # given executable,
            os.chmod(bin_path, 0o700)

            # exercise absolute and relative,
            assert pexpect.which(bin_path) == bin_path
            assert pexpect.which(fname) == bin_path

        finally:
            # restore,
            os.environ['PATH'] = save_path
            os.defpath = save_defpath

            # destroy scratch files and folders,
            if os.path.exists(bin_path):
                os.unlink(bin_path)
            if os.path.exists(bin_dir):
                os.rmdir(bin_dir)

    def test_path_search_which(self):
        " which() finds an executable in $PATH and returns its abspath. "
        fname = 'gcc'
        bin_dir = tempfile.mkdtemp()
        bin_path = os.path.join(bin_dir, fname)
        save_path = os.environ['PATH']
        try:
            # setup
            os.environ['PATH'] = bin_dir
            with open(bin_path, 'w') as fp:
                pass

            # given non-executable,
            os.chmod(bin_path, 0o400)

            # exercise absolute and relative,
            assert pexpect.which(bin_path) is None
            assert pexpect.which(fname) is None

            # given executable,
            os.chmod(bin_path, 0o700)

            # exercise absolute and relative,
            assert pexpect.which(bin_path) == bin_path
            assert pexpect.which(fname) == bin_path

        finally:
            # restore,
            os.environ['PATH'] = save_path

            # destroy scratch files and folders,
            if os.path.exists(bin_path):
                os.unlink(bin_path)
            if os.path.exists(bin_dir):
                os.rmdir(bin_dir)

    def test_which_follows_symlink(self):
        " which() follows symlinks and returns its path. "
        fname = 'original'
        symname = 'extra-crispy'
        bin_dir = tempfile.mkdtemp()
        bin_path = os.path.join(bin_dir, fname)
        sym_path = os.path.join(bin_dir, symname)
        save_path = os.environ['PATH']
        try:
            # setup
            os.environ['PATH'] = bin_dir
            with open(bin_path, 'w') as fp:
                pass
            os.chmod(bin_path, 0o400)
            os.symlink(bin_path, sym_path)

            # should not be found because symlink points to non-executable
            assert pexpect.which(symname) is None

            # but now it should -- because it is executable
            os.chmod(bin_path, 0o700)
            assert pexpect.which(symname) == sym_path

        finally:
            # restore,
            os.environ['PATH'] = save_path

            # destroy scratch files, symlinks, and folders,
            if os.path.exists(sym_path):
                os.unlink(sym_path)
            if os.path.exists(bin_path):
                os.unlink(bin_path)
            if os.path.exists(bin_dir):
                os.rmdir(bin_dir)

    def test_which_should_not_match_folders(self):
        " Which does not match folders, even though they are executable. "
        # make up a path and insert a folder that is 'executable', a naive
        # implementation might match (previously pexpect versions 3.2 and
        # sh versions 1.0.8, reported by @lcm337.)
        fname = 'g++'
        bin_dir = tempfile.mkdtemp()
        bin_dir2 = os.path.join(bin_dir, fname)
        save_path = os.environ['PATH']
        try:
            os.environ['PATH'] = bin_dir
            os.mkdir(bin_dir2, 0o755)
            # should not be found because it is not executable *file*,
            # but rather, has the executable bit set, as a good folder
            # should -- it should not be returned because it fails isdir()
            exercise = pexpect.which(fname)
            assert exercise is None

        finally:
            # restore,
            os.environ['PATH'] = save_path
            # destroy scratch folders,
            for _dir in (bin_dir2, bin_dir,):
                if os.path.exists(_dir):
                    os.rmdir(_dir)

    def test_which_should_match_other_group_user(self):
        " which() returns executables by other, group, and user ownership. "
        # create an executable and test that it is found using which() for
        # each of the 'other', 'group', and 'user' permission bits.
        fname = 'g77'
        bin_dir = tempfile.mkdtemp()
        bin_path = os.path.join(bin_dir, fname)
        save_path = os.environ['PATH']
        try:
            # setup
            os.environ['PATH'] = bin_dir
            with open(bin_path, 'w') as fp:
                fp.write('#!/bin/sh\necho hello, world\n')
            for should_match, mode in ((False, 0o000),
                                       (True,  0o005),
                                       (True,  0o050),
                                       (True,  0o500),
                                       (False, 0o004),
                                       (False, 0o040),
                                       (False, 0o400)):
                os.chmod(bin_path, mode)

                if not should_match:
                    # should not be found because it is not executable
                    assert pexpect.which(fname) is None
                else:
                    # should match full path
                    assert pexpect.which(fname) == bin_path

        finally:
            # restore,
            os.environ['PATH'] = save_path
            # destroy scratch files and folders,
            if os.path.exists(bin_path):
                os.unlink(bin_path)
            if os.path.exists(bin_dir):
                os.rmdir(bin_dir)
