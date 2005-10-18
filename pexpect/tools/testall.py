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
'''

import unittest
import os, os.path
import sys

import pexpect
print pexpect.__version__,
print pexpect.__revision__

def add_tests_to_list (import_list, dirname, names):
    # Only check directories named 'tests'.
    if os.path.basename(dirname) != 'tests':
        return
    # Add any files that start with 'test_' and end with '.py'.
    for f in names:
        filename, ext = os.path.splitext(f)
        if ext != '.py':
            continue
        if filename.find('test_') == 0:
            import_list.append (os.path.join(dirname, filename))
 
def find_modules_and_add_paths (root_path):
    import_list = []
    module_list = []
    os.path.walk (root_path, add_tests_to_list, import_list)
    for module_file in import_list:
        path, module = os.path.split(module_file)
        module_list.append (module)
        print 'Adding:', module_file
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

