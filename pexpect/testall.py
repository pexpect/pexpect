#!/usr/bin/env python
'''This module allows you to run all tests in the project where:
    test directories are named 'tests'
    test module names begin with 'test_'

Testing from Unittest GUI:
    type testall.py into the unittestgui.py GUI

Testing from Command Line:
    To run tests from command line just run this script.
    Alternatively you can run it this way:
        python /usr/local/lib/python2.1/unittest.py testall

'''

import unittest
import os, os.path
import sys

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

