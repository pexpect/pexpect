import os
import runpy
import sys
import types
import unittest
from unittest import mock


class SetupTestCase(unittest.TestCase):
    def test_setup_does_not_require_distutils(self):
        """Ensure setup.py imports setup from setuptools without distutils."""
        setup_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'setup.py',
        )
        fake_setuptools = types.ModuleType('setuptools')
        fake_setup = mock.Mock()
        fake_setuptools.setup = fake_setup

        patched_modules = {
            'distutils': None,
            'distutils.core': None,
            'setuptools': fake_setuptools,
        }
        with mock.patch.dict(sys.modules, patched_modules), \
             mock.patch.object(sys, 'argv', ['setup.py', '--version']):
            runpy.run_path(setup_path)

        self.assertEqual(fake_setup.call_count, 1)
        self.assertEqual(fake_setup.call_args[1]['name'], 'pexpect')


if __name__ == '__main__':
    unittest.main()
