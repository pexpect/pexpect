
import unittest
import sys
import os

class PexpectTestCase(unittest.TestCase):
    def setUp(self):
        self.PYTHONBIN = sys.executable
        self.original_path = os.getcwd()
        newpath = os.path.join (os.environ['PROJECT_PEXPECT_HOME'], 'tests')
        os.chdir (newpath)
    def tearDown(self):
        os.chdir (self.original_path)

