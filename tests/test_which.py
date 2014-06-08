import tempfile
import os

import pexpect
from . import PexpectTestCase


class TestCaseMisc(PexpectTestCase.PexpectTestCase):

    def test_basic_which(self):
        # should find at least 'ls' program, and it should begin with '/'
        exercise = pexpect.which("ls")
        assert exercise is not None and exercise.startswith('/')

    def test_which(self):
        p = os.defpath
        ep = os.environ['PATH']
        os.defpath = ":/tmp"
        os.environ['PATH'] = ":/tmp"
        wp = pexpect.which("ticker.py")
        assert wp == 'ticker.py'
        os.defpath = "/tmp"
        os.environ['PATH'] = "/tmp"
        wp = pexpect.which("ticker.py")
        assert wp is None
        os.defpath = p
        os.environ['PATH'] = ep

    def test_absolute_which(self):
        # make up a path and insert first a non-executable,
        # then, make it executable, and assert we may which() find it.
        fname = 'gcc'
        bin_dir = tempfile.mkdtemp()
        bin_path = os.path.join(bin_dir, fname)
        save_path = os.environ['PATH']
        try:
            # setup
            os.environ['PATH'] = bin_dir
            with open(bin_path, 'w') as fp:
                fp.write('#!/bin/sh\necho hello, world\n')
            os.chmod(bin_path, 0o400)

            # it should not be found because it is not executable
            assert pexpect.which(fname) is None, fname

            # but now it should -- because it is executable
            os.chmod(bin_path, 0o700)
            assert pexpect.which(fname) == bin_path, (fname, bin_path)

        finally:
            # restore,
            os.environ['PATH'] = save_path
            # destroy scratch files and folders,
            if os.path.exists(bin_path):
                os.unlink(bin_path)
            if os.path.exists(bin_dir):
                os.rmdir(bin_dir)

    def test_which_should_not_match_folders(self):
        # make up a path and insert a folder, which is 'executable', which
        # a naive implementation might match (previously pexpect versions
        # 3.2 and sh versions 1.0.8, reported by @lcm337.)
        fname = 'g++'
        bin_dir = tempfile.mkdtemp()
        bin_dir2 = os.path.join(bin_dir, fname)
        save_path = os.environ['PATH']
        try:
            os.environ['PATH'] = bin_dir
            os.mkdir(bin_dir2, 0o755)
            # it should not be found because it is not executable *file*,
            # but rather, has the executable bit set, as a good folder
            # should -- it shouldn't be returned because it fails isdir()
            exercise = pexpect.which(fname)
            assert exercise is None, exercise

        finally:
            # restore,
            os.environ['PATH'] = save_path
            # destroy scratch folders,
            for _dir in (bin_dir2, bin_dir,):
                if os.path.exists(_dir):
                    os.rmdir(_dir)
