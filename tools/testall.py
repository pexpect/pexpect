#!/usr/bin/env python
'''This script runs all tests in a directory.
It does not need to know about the tests ahead of time.
It recursively descends from the current directory and
automatically builds up a list of tests to run.
Only directories named 'tests' are processed.
The path to each 'tests' directory is added to the PYTHONPATH.
Only python scripts that start with 'test_' are added to
the list of scripts in the test suite.
Noah Spurrier

PEXPECT LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012, Noah Spurrier <noah@noah.org>
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''
from __future__ import print_function

import unittest
import os, os.path
import sys
import platform

import pexpect

print("Testing pexpect %s using python %s:" % (
    pexpect.__version__, platform.python_version()))

# Don't bother checking performance on Travis, we know it's slow.
TEST_PERFORMANCE = 'TRAVIS' not in os.environ

def add_tests_to_list (import_list, dirname, names):
    # Only check directories named 'tests'.
    if os.path.basename(dirname) != 'tests':
        return
    # Add any files that start with 'test_' and end with '.py'.
    for f in names:
        filename, ext = os.path.splitext(f)
        if ext != '.py':
            continue
        if (not TEST_PERFORMANCE) and (filename == 'test_performance'):
            continue
        if filename.find('test_') == 0:
            import_list.append (os.path.join(dirname, filename))

def find_modules_and_add_paths (root_path):
    import_list = []
    module_list = []
    for (dirpath, dirnames, filenames) in os.walk(root_path):
        add_tests_to_list(import_list, dirpath, filenames)

    for module_file in import_list:
        path, module = os.path.split(module_file)
        module_list.append (module)
        print('Adding:', os.path.relpath(module_file))
        if not path in sys.path:
            sys.path.append (path)
        if not os.path.dirname(path) in sys.path:
            sys.path.append (os.path.dirname(path))

    module_list.sort()
    return module_list

def suite():
    modules_to_test = find_modules_and_add_paths (os.getcwd())
    alltests = unittest.TestSuite()
    for module in map(__import__, modules_to_test):
        alltests.addTest(unittest.findTestCases(module))
    return alltests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
#    s = all()
#    runner = unittest.TextTestRunner()
#    runner.run (s)

