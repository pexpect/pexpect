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
import os
import tempfile
import PexpectTestCase

class TestCaseLog(PexpectTestCase.PexpectTestCase):

    def test_log (self):
        log_message = 'This is a test.'
        filename = tempfile.mktemp()
        mylog = open (filename, 'w')
        p = pexpect.spawn('echo', [log_message])
        p.logfile = mylog
        p.expect (pexpect.EOF)
        p.logfile = None
        mylog.close()
        lf = open(filename).read()
        lf = lf[:-2]
        os.unlink (filename)
        assert lf == log_message

    def test_log_logfile_read (self):
        log_message = 'This is a test.'
        filename = tempfile.mktemp()
        mylog = open (filename, 'w')
        p = pexpect.spawn('cat')
        p.logfile_read = mylog
        p.sendline(log_message)
        p.sendeof()
        p.expect (pexpect.EOF)
        p.logfile = None
        mylog.close()
        lf = open(filename).read()
        lf = lf[:-2]
        os.unlink (filename)
        lf = lf.replace(chr(4),'')
        assert lf == 'This is a test.\r\nThis is a test.', "The read log file has bad data. Note logfile_read should only record what we read from child and nothing else.\n" + repr(lf)

    def test_log_logfile_send (self):
        log_message = 'This is a test.'
        filename = tempfile.mktemp()
        mylog = open (filename, 'w')
        p = pexpect.spawn('cat')
        p.logfile_send = mylog
        p.sendline(log_message)
        p.sendeof()
        p.expect (pexpect.EOF)
        p.logfile = None
        mylog.close()
        lf = open(filename).read()
        lf = lf[:-2]
        os.unlink (filename)
        assert lf == log_message, "The send log file has bad data. Note logfile_send should only record what we sent to child and nothing else."

    def test_log_send_and_received (self):

        '''The logfile should have the test message three time -- once for the
        data we sent. Once for the data that cat echos back as characters are
        typed. And once for the data that cat prints after we send a linefeed
        (sent by sendline). '''

        log_message = 'This is a test.'
        filename = tempfile.mktemp()
        mylog = open (filename, 'w')
        p = pexpect.spawn('cat')
        p.logfile = mylog
        p.sendline(log_message)
        p.sendeof()
        p.expect (pexpect.EOF)
        p.logfile = None
        mylog.close()
        lf = open(filename).read()
        os.unlink (filename)
        lf = lf.replace(chr(4),'')
        assert lf == 'This is a test.\nThis is a test.\r\nThis is a test.\r\n', repr(lf)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseLog,'test')

