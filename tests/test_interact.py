#!/usr/bin/env python
'''
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
import pexpect
import unittest
import commands
import sys, os, time, tty
import PexpectTestCase
import thread
import threading

def start_interact (p):
    p.interact()

class InteractTestCase (PexpectTestCase.PexpectTestCase):

    def test_interact_thread (self):
        # I can't believe this actually works...
        # Note that I had to add a delay in the swapcase_echo.py script.
        # I'm not sure why this helped.
        p = pexpect.spawn('%s swapcase_echo.py' % self.PYTHONBIN)
        mode = tty.tcgetattr(p.STDIN_FILENO)
        t = threading.Thread (target=start_interact, args=(p,))
        t.start()
        #thread.start_new_thread (start_interact, (p,))
        time.sleep(1)
        p.sendline ('Hello')
        #time.sleep(1)
        try:
            p.expect ('hELLO', timeout=4)
        except Exception, e:
            p.close(force = False)
            tty.tcsetattr(p.STDIN_FILENO, tty.TCSAFLUSH, mode)
            print str(p)
            raise e
        p.close(force = True)
        tty.tcsetattr(p.STDIN_FILENO, tty.TCSAFLUSH, mode)
#    def test_interact_thread (self):
#        # I can't believe this actually works...
#        p = pexpect.spawn('%s swapcase_echo.py' % self.PYTHONBIN)
#        mode = tty.tcgetattr(p.STDIN_FILENO)
#        thread.start_new_thread (start_interact, (p,))
#        time.sleep(1)
#        p.sendline ('Hello')
#        time.sleep(2)
#        p.close(force = False)
#        tty.tcsetattr(p.STDIN_FILENO, tty.TCSAFLUSH, mode)

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

