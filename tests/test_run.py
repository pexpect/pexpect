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
import subprocess
import PexpectTestCase

# TODO Many of these test cases blindly assume that sequential
# TODO listing of the /bin directory will yield the same results.
# TODO This may not always be true, but seems adequate for testing for now.
# TODO I should fix this at some point.

def timeout_callback (d):
#    print d["event_count"],
    if d["event_count"]>5:
        return 1
    return 0

class ExpectTestCase(PexpectTestCase.PexpectTestCase):
    def test_run_exit (self):
        (data, exitstatus) = pexpect.run ('python exit1.py', withexitstatus=1)
        assert exitstatus == 1, "Exit status of 'python exit1.py' should be 1."

    def test_run (self):
        the_old_way = subprocess.Popen(args=['ls', '-l', '/bin'],
                stdout=subprocess.PIPE).communicate()[0].rstrip()
        (the_new_way, exitstatus) = pexpect.run ('ls -l /bin', withexitstatus=1)
        the_new_way = the_new_way.replace(b'\r',b'').rstrip()
        self.assertEqual(the_old_way, the_new_way)
        self.assertEqual(exitstatus, 0)

    def test_run_callback (self): # TODO it seems like this test could block forever if run fails...
        pexpect.run("cat", timeout=1, events={pexpect.TIMEOUT:timeout_callback})

    def test_run_bad_exitstatus (self):
        (the_new_way, exitstatus) = pexpect.run ('ls -l /najoeufhdnzkxjd', withexitstatus=1)
        assert exitstatus != 0

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase,'test')

