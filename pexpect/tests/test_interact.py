#!/usr/bin/env python
import pexpect
import unittest
import commands
import sys, os, time, tty
import PexpectTestCase
import thread

def start_interact (p):
    p.interact()

class InteractTestCase (PexpectTestCase.PexpectTestCase):

    def test_interact_thread (self):
        # I can't believe this actually works...
        p = pexpect.spawn('%s swapcase_echo.py' % self.PYTHONBIN)
        mode = tty.tcgetattr(p.STDIN_FILENO)
        thread.start_new_thread (start_interact, (p,))
        time.sleep(1)
        p.sendline ('Hello')
        time.sleep(2)
        p.close(force = False)
        tty.tcsetattr(p.STDIN_FILENO, tty.TCSAFLUSH, mode)
        
    def test_interact (self):
        p = pexpect.spawn('%s interact.py' % self.PYTHONBIN)
        p.sendline ('Hello')
        p.sendline ('there')
        p.sendline ('Mr. Python')
        p.expect ('Hello')
        p.expect ('there')
        p.expect ('Mr. Python')
        p.sendeof () 
        p.expect (pexpect.EOF)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(InteractTestCase,'test')

