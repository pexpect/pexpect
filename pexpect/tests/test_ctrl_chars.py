#!/usr/bin/env python
import pexpect
import unittest
import PexpectTestCase
import time
import os

class TestCtrlChars(PexpectTestCase.PexpectTestCase):
        
    def test_control_chars (self):

        """This tests that we can send all 256 8-bit ASCII characters
        to a child process."""

        child = pexpect.spawn('python getch.py')
        # Most Linux machines don't like this to be below 0.03.
        child.delaybeforesend = 0.03
        for i in range(256):
            child.send(chr(i))
            child.expect ('%d\r\n' % i)
            #print child.after

    def test_sendcontrol(self):

        """This tests that we can send all special control codes by name.
        """

        child = pexpect.spawn('python getch.py')
        # Most Linux machines don't like this to be below 0.03.
        child.delaybeforesend = 0.03
        for i in 'abcdefghijklmnopqrstuvwxyz':
            child.sendcontrol(i)
            child.expect ('[0-9]+\r\n')
            #print child.after

        child.sendcontrol('@')
        child.expect ('0\r\n')
        #print child.after
        child.sendcontrol('[')
        child.expect ('27\r\n')
        #print child.after
        child.sendcontrol('\\')
        child.expect ('28\r\n')
        #print child.after
        child.sendcontrol(']')
        child.expect ('29\r\n')
        #print child.after
        child.sendcontrol('^')
        child.expect ('30\r\n')
        #print child.after
        child.sendcontrol('_')
        child.expect ('31\r\n')
        #print child.after
        child.sendcontrol('?')
        child.expect ('127\r\n')
        #print child.after

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCtrlChars,'test')

