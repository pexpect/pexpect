#!/usr/bin/env python

import unittest 
import sys 
sys.path.append('tests') 

modules_to_test = ( 
'test_expect',
'test_is_alive',
'test_ansi',
'test_command_list_split',
'test_destructor',
'test_constructor',
'test_log',
'test_missing_command',
'test_run_out_of_pty',
'test_screen'
) 


def suite(): 
    alltests = unittest.TestSuite() 
    for module in map(__import__, modules_to_test): 
        alltests.addTest(unittest.findTestCases(module)) 
    return alltests 

if __name__ == '__main__': 
    unittest.main(defaultTest='suite') 

